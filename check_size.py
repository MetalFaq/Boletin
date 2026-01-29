import os
from src import loader

base_dir = r"c:\Users\fnrivarola\Desktop\Celula\Boletin"
sources_dir = os.path.join(base_dir, "Sources")

print("Loading PDFs...")
pdf_texts = loader.load_pdfs_text(sources_dir)
full_text = "\n\n".join([v for v in pdf_texts.values()])

char_count = len(full_text)
est_tokens = char_count / 4

print(f"Total Characters: {char_count}")
print(f"Estimated Tokens: {est_tokens}")

if est_tokens > 800000:
    print("WARNING: Context is very large!")
else:
    print("Context fits in 1M window.")
