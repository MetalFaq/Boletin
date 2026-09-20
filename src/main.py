import asyncio
import os
import sys

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import BoletinAgentWrapper

async def ainput(prompt: str = "") -> str:
    """Async input helper (runs input in executor)"""
    return await asyncio.to_thread(input, prompt)

async def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("Initializing Agent... (this may take a moment to load PDFs)")
    try:
        agent_wrapper = BoletinAgentWrapper(base_dir)
        print("\nAgent Ready! Type 'exit' to quit.\n")
    except Exception as e:
        print(f"Initialization Failed: {e}")
        return

    while True:
        try:
            user_input = await ainput("User> ")
            if user_input.lower() in ('exit', 'quit'):
                break
            
            response = await agent_wrapper.process_message(user_input)
            print(f"\nAgent> {response}\n")
            
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass # Handle top-level interrupt cleanly
