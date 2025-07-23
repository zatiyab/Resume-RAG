import subprocess
import os
import unicodedata
import re

# from pathlib import Path

# directory = Path("resumes")

# for file in directory.iterdir():
#     if file.suffix == ".pdf":
#         new_name = ""
#         for i in file.name:
#             if i==" ":
#                 i = "_"
#             new_name+=i
        
#         print(f"Renamed: {file.name} → {new_name}")


def convert_with_libreoffice(input_path):
    if not os.path.isfile(input_path):
        print(f"File not found: {input_path}")
        return

    if not input_path.lower().endswith(('.doc', '.docx')):
        print(f"Skipped unsupported file: {input_path}")
        return

    output_dir = os.path.dirname(input_path)

    subprocess.run([
        "soffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_path
    ])
    print(f"Converted: {input_path}")

def convert_all_docs_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.doc', '.docx')):
            file_path = os.path.join(folder_path, filename)
            convert_with_libreoffice(file_path)
            os.remove(file_path)

def remove_same_files(folder):
    import re
    pattern = r"\(\d+\)$"
    resumes = os.listdir(folder)
    resumes = [i for i in resumes if i.endswith('.pdf')]
    for resume in resumes:
        resume = resume.rstrip('.pdf')
        if re.search(pattern,resume):
            print('Copy : ',resume)

def basic_text_normalization(text: str) -> str:
    """Basic cleaning that should be applied to all text"""
    
    # Remove or normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Fix common encoding issues
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep meaningful punctuation
    text = re.sub(r'[^\w\s\-\.\,\(\)\/]', '', text)
    
    # Normalize case (but preserve acronyms)
    words = text.split()
    normalized_words = []
    for word in words:
        if word.isupper() and len(word) > 1:  # Keep acronyms
            normalized_words.append(word)
        else:
            normalized_words.append(word.lower())
    
    return ' '.join(normalized_words).strip()
