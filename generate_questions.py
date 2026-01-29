import os
import pandas as pd
from src import loader

base_dir = r"c:\Users\fnrivarola\Desktop\Celula\Boletin"
sources_dir = os.path.join(base_dir, "Sources")
excel_path = os.path.join(sources_dir, "Temas de interes para monitorear.xlsx")

print(f"Loading guidelines from {excel_path}...")
df = loader.load_guidelines_data(excel_path)

print(f"Guidelines DataFrame shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

guidelines_str = df.to_string()
print(f"Guidelines String Length: {len(guidelines_str)}")
print("-" * 50)

# Generate questions
print("\nGENERATED TEST QUESTIONS:\n")
questions = []

# Assuming columns like 'Título', 'Jurisdicción', 'Tipo de Norma' exists based on previous context
if 'Título' in df.columns:
    titles = df['Título'].dropna().unique()
    for t in titles[:5]: # Take top 5
        questions.append(f"¿Hay alguna información sobre {t}?")
        questions.append(f"¿Qué dice el boletín acerca de {t}?")

if 'Tipo de Norma' in df.columns and 'Jurisdicción' in df.columns:
    sample = df[['Tipo de Norma', 'Jurisdicción']].dropna().head(3)
    for _, row in sample.iterrows():
        questions.append(f"Listame las {row['Tipo de Norma']} de la jurisdicción {row['Jurisdicción']}.")

for q in questions:
    print(f"- {q}")

# Check PDF size again just to be sure
pdf_texts = loader.load_pdfs_text(sources_dir)
full_text = "\n\n".join([v for v in pdf_texts.values()])
print(f"\nPDF Text Length: {len(full_text)}")
