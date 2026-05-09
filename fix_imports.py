import re
import os

files_to_process = [
    r'd:\Resume_RAG\Resume-RAG\app\api\auth_routes.py',
    r'd:\Resume_RAG\Resume-RAG\app\api\chat_routes.py',
    r'd:\Resume_RAG\Resume-RAG\app\api\resume_routes.py',
    r'd:\Resume_RAG\Resume-RAG\app\rag_logic\filter.py',
    r'd:\Resume_RAG\Resume-RAG\app\rag_logic\rag_main.py',
    r'd:\Resume_RAG\Resume-RAG\app\services\auth_service.py',
    r'd:\Resume_RAG\Resume-RAG\app\services\chat.py'
]

for file_path in files_to_process:
    if not os.path.exists(file_path): continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the broken import syntax
    content = content.replace('from app.core.logger import logger\nimport ', 'import ')
    content = 'from app.core.logger import logger\n' + content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print('Fixed imports')
