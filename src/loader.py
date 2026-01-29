import os
import pandas as pd
from pypdf import PdfReader
from typing import Dict, List, Any

def load_pdfs_text(sources_dir: str) -> Dict[str, str]:
    """
    Reads all PDF files in the sources_dir and returns a dictionary
    mapping filename -> full text content.
    """
    pdf_texts = {}
    if not os.path.exists(sources_dir):
        print(f"Warning: Directory {sources_dir} does not exist.")
        return pdf_texts

    for filename in os.listdir(sources_dir):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(sources_dir, filename)
            try:
                reader = PdfReader(path)
                text = []
                for page in reader.pages:
                    text.append(page.extract_text() or "")
                pdf_texts[filename] = "\n".join(text)
                print(f"Loaded {filename}: {len(reader.pages)} pages.")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    return pdf_texts

def load_guidelines_data(excel_path: str) -> pd.DataFrame:
    """
    Loads the Excel file containing guidelines.
    Expects columns like 'Título', 'Jurisdicción', 'Consulta', etc.
    """
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found at {excel_path}")
    
    try:
        df = pd.read_excel(excel_path)
        # Normalize columns if necessary, for now returning raw DF
        return df
    except Exception as e:
        print(f"Error reading Excel lines: {e}")
        return pd.DataFrame()

def load_keywords(df: pd.DataFrame) -> List[str]:
    """
    Extracts relevant keywords from the guidelines dataframe for scoring.
    """
    keywords = set()
    # Add words from Title, Subtitle, Jurisdiction
    # Adjust column names based on inspect_files.py output: ['Título', 'Subtítulo', 'Tipo de Norma', 'Jurisdicción']
    cols_to_scan = ['Título', 'Subtítulo', 'Jurisdicción', 'Tipo de Norma']
    
    for col in cols_to_scan:
        if col in df.columns:
            for val in df[col].dropna().astype(str):
                # Split by spaces and add to set
                words = val.lower().split()
                keywords.update(words)
    
    # Remove common stop words if needed (basic list for now)
    stop_words = {'de', 'la', 'el', 'en', 'y', 'a', 'que', 'los', 'del', 'las', 'un', 'una', 'por', 'para', 'con', 'no', 'sus', 'es'}
    return list(keywords - stop_words)
