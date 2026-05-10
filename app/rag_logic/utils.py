from app.core.logger import logger
import subprocess
import os
import unicodedata
import re
import tempfile
import uuid

# from pathlib import Path

# directory = Path("resumes")

# for file in directory.iterdir():
#     if file.suffix == ".pdf":
#         new_name = ""
#         for i in file.name:
#             if i==" ":
#                 i = "_"
#             new_name+=i
        
#         logger.info(f"Renamed: {file.name} → {new_name}")


import shutil

def convert_with_libreoffice(input_path):
    if not os.path.isfile(input_path):
        logger.info(f"File not found: {input_path}")
        return

    if not input_path.lower().endswith(('.doc', '.docx')):
        logger.info(f"Skipped unsupported file: {input_path}")
        return

    output_dir = os.path.dirname(input_path)

    soffice_path = "soffice"
    if os.name == 'nt':
        if not shutil.which("soffice"):
            common_paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
            ]
            for p in common_paths:
                if os.path.isfile(p):
                    soffice_path = p
                    break

    try:
        subprocess.run([
            soffice_path,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_path
        ], check=True)
        logger.info(f"Converted: {input_path}")
    except Exception as e:
        logger.error(f"Error executing soffice: {e}")

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
            logger.info('Copy : %s', resume)

def basic_text_normalization(text: str) -> str:
    """Basic cleaning that should be applied to all text"""
    
    # Remove or normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Fix common encoding issues
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    
    # Remove special characters but keep meaningful punctuation
    text = re.sub(r'[^\w\s\-\.\,\(\)\/]', '', text)
    
    # # Normalize case (but preserve acronyms)
    # words = text.split()
    # normalized_words = []
    # for word in words:
    #     if word.isupper() and len(word) > 1:  # Keep acronyms
    #         normalized_words.append(word)
    #     else:
    #         normalized_words.append(word.lower())
    
    return text


def convert_doc_content_to_pdf_bytes(content_bytes: bytes, original_filename: str) -> bytes:
    """Takes DOC/DOCX bytes, saves temp files for LibreOffice, converts to PDF, returns PDF bytes, limits disk footprint."""
    temp_dir = tempfile.gettempdir()
    unique_id = uuid.uuid4().hex[:8]
    
    # Needs to match docx/doc extension for libreoffice to convert it properly
    _, ext = os.path.splitext(original_filename)
    if not ext:
        ext = ".docx"

    temp_input_name = f"temp_resume_{unique_id}{ext}"
    temp_input_path = os.path.join(temp_dir, temp_input_name)
    
    with open(temp_input_path, "wb") as f:
        f.write(content_bytes)
        
    try:
        # Convert using existing method
        convert_with_libreoffice(temp_input_path)
        
        pdf_path = os.path.splitext(temp_input_path)[0] + ".pdf"
        
        if not os.path.exists(pdf_path):
            raise Exception("LibreOffice failed to generate PDF output.")
            
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        # Clean up output PDF
        os.remove(pdf_path)
        
        return pdf_bytes
    finally:
        # Clean up input DOC
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
