import os
import asyncio
import json
import logging
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import pandas as pd

try:
    from . import loader
    from . import scorer
except ImportError:
    import loader
    import scorer

load_dotenv()

class BoletinAgentWrapper:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.sources_dir = os.path.join(base_dir, "Sources")
        self.excel_path = os.path.join(self.sources_dir, "Temas de interes para monitorear.xlsx")
        
        print(f"Loading PDFs from {self.sources_dir}...")
        self.pdf_texts = loader.load_pdfs_text(self.sources_dir)
        self.full_pdf_context = "\n\n".join([f"--- FILE: {k} ---\n{v}" for k, v in self.pdf_texts.items()])
        
        print(f"Loading guidelines from {self.excel_path}...")
        self.guidelines_df = loader.load_guidelines_data(self.excel_path)
        self.keywords = loader.load_keywords(self.guidelines_df)
        
        # Construct the System Instruction once
        guidelines_str = self.guidelines_df.to_string()
        
        system_instruction = f"""
        ROLE:
        You are an intelligent assistant analyzing "Boletin Oficial" PDFs.
        
        CONTEXT (Full Text of Documents):
        {self.full_pdf_context}
        
        GUIDELINES (Topics to Monitor):
        {guidelines_str}
        
        BEHAVIOR:
        1. You act as a specialized analyst.
        2. When the user asks a question, check if it relates to any of the GUIDELINES.
        3. If the query matches a guideline (STRICT mode), output a JSON response.
        4. If the query is general (GENERAL mode), answer conversationally based on the text.
        
        STRICT MODE FORMAT (JSON):
        If the user query specifically asks about a monitored topic or matches a guideline title/keyword:
        Output a strictly valid JSON list:
        [
            {{
                "found": true,
                "topic": "Title from guidelines",
                "summary": "Brief summary of what the document says about this topic.",
                "page": 10
            }}
        ]
        
        GENERAL MODE FORMAT (Text):
        If the query is generic (e.g., "What is the date?", "List sections"), simply answer in plain text.
        """

        self.agent = Agent(
            name="BoletinAgent",
            model="gemini-2.0-flash", 
            instruction=system_instruction
        )
        
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            app_name="boletin_agent_app",
            agent=self.agent,
            session_service=self.session_service,
            auto_create_session=True,
        )

    async def _run_async(self, prompt: str, metadata: dict) -> str:
        """Helper to run the ADK runner asynchronously and log events"""
        content = Content(role="user", parts=[Part(text=prompt)])
        full_text = ""
        
        user_id = "cli_user"
        session_id = "session_001"
        
        try:
            # Runner with auto_create_session=True handles session creation internally.
            async for event in self.runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                if hasattr(event, 'content') and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            full_text += part.text
        except Exception as e:
            full_text = f"Error executing agent: {e}"
            self._log_interaction(metadata, full_text, error=str(e))
            return full_text
            
        self._log_interaction(metadata, full_text, error=None)
        return full_text

    def _log_interaction(self, metadata: dict, response: str, error: str = None):
        """Logs interaction details to a file"""
        log_entry = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "query": metadata.get('query'),
            "score": metadata.get('score'),
            "routing": metadata.get('routing'),
            "response": response,
            "error": error
        }
        
        log_file = os.path.join(self.base_dir, "interaction_logs.jsonl")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[ERROR] Could not write to log: {e}")

    def _format_strict_response(self, raw_json: str) -> str:
        """Parses the JSON response from Gemini and makes it human readable."""
        try:
            # Clean markdown code blocks if present
            clean_json = raw_json.replace("```json", "").replace("```", "").strip()
            # Find first [ and last ]
            start = clean_json.find("[")
            end = clean_json.rfind("]")
            if start != -1 and end != -1:
                clean_json = clean_json[start:end+1]
            
            data = json.loads(clean_json)
            
            if isinstance(data, list) and data:
                 output = []
                 for item in data:
                     if item.get("found"):
                         output.append(
                             f"✅ **Tema Encontrado**: {item.get('topic')}\n"
                             f"📄 **Página**: {item.get('page')}\n"
                             f"📝 **Resumen**: {item.get('summary')}\n"
                         )
                 if not output:
                     return "No se encontró información específica sobre ese lineamiento en el boletín."
                 return "\n---\n".join(output)
            elif isinstance(data, dict):
                 if data.get("found"):
                     return (
                         f"✅ **Tema Encontrado**: {data.get('topic')}\n"
                         f"📄 **Página**: {data.get('page')}\n"
                         f"📝 **Resumen**: {data.get('summary')}\n"
                     )
                 else:
                    return "No se encontró información específica en los lineamientos monitoreados."
            
            return raw_json # Fallback if structure is unexpected
            
        except json.JSONDecodeError:
            # If not JSON, it might be a general response (text)
            return raw_json

    async def process_message(self, user_message: str) -> str:
        score = scorer.calculate_relevance_score(user_message, self.keywords)
        # Threshold 
        routing = "STRICT" if score >= 4 else "GENERAL"
        
        print(f"[DEBUG] Query: '{user_message}' | Score: {score}")
        print(f"[DEBUG] Routing: {routing}")

        metadata = {
            "query": user_message,
            "score": score,
            "routing": routing
        }

        # We now send ONLY the user message. The context is in the Agent Instruction.
        # We can append a hint if we want to force format, but let's try relying on the System Instruction first.
        # This drastically reduces token usage per turn.
        
        if routing == "STRICT":
            # Hint to force strict behavior if the Score is high
            prompt = f"{user_message}\n(Use STRICT JSON format for this monitoring request)"
            raw_response = await self._run_async(prompt, metadata)
            return self._format_strict_response(raw_response)
        else:
            # General query
            prompt = user_message
            return await self._run_async(prompt, metadata)
