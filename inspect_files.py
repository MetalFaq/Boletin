import pandas as pd
from pypdf import PdfReader
import os

base_dir = r"c:\Users\fnrivarola\Desktop\Celula\Boletin\Sources"
excel_path = os.path.join(base_dir, "Temas de interes para monitorear.xlsx")
pdf1_path = os.path.join(base_dir, "Primera.pdf")
pdf2_path = os.path.join(base_dir, "Segunda.pdf")

print("--- Excel Analysis ---")
try:
    df = pd.read_excel(excel_path)
    print(df.head())
    print("\nColumns:", df.columns.tolist())
except Exception as e:
    print(f"Error reading Excel: {e}")

print("\n--- PDF 1 Analysis ---")
try:
    reader = PdfReader(pdf1_path)
    print(f"Total Pages: {len(reader.pages)}")
    print("First Page Text:")
    print(reader.pages[0].extract_text())
except Exception as e:
    print(f"Error reading PDF 1: {e}")

print("\n--- PDF 2 Analysis ---")
try:
    reader = PdfReader(pdf2_path)
    print(f"Total Pages: {len(reader.pages)}")
    print("First Page Text:")
    print(reader.pages[0].extract_text())
except Exception as e:
    print(f"Error reading PDF 2: {e}")
