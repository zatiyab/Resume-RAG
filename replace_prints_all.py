import re
import os

files_to_process = [
    r'd:\Resume_RAG\Resume-RAG\app\rag_logic\rag_main.py',
    r'd:\Resume_RAG\Resume-RAG\app\rag_logic\filter.py',
    r'd:\Resume_RAG\Resume-RAG\app\rag_logic\utils.py',
    r'd:\Resume_RAG\Resume-RAG\app\services\chat.py',
    r'd:\Resume_RAG\Resume-RAG\app\services\auth_service.py',
    r'd:\Resume_RAG\Resume-RAG\app\api\auth_routes.py',
    r'd:\Resume_RAG\Resume-RAG\app\api\chat_routes.py',
    r'd:\Resume_RAG\Resume-RAG\app\api\resume_routes.py'
]

def replacer(match):
    args = match.group(1)
    args = re.sub(r',\s*flush=True', '', args)
    args_lower = args.lower()
    
    if 'error' in args_lower or 'failed' in args_lower or 'warning' in args_lower:
        return f'logger.error({args})'
    elif 'debug' in args_lower:
        return f'logger.debug({args})'
    else:
        return f'logger.info({args})'

for file_path in files_to_process:
    if not os.path.exists(file_path): continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'print(' not in content:
        continue
        
    if 'from app.core.logger import logger' not in content:
        # Find first import or add at top
        if 'import ' in content:
            content = content.replace('import ', 'from app.core.logger import logger\nimport ', 1)
        else:
            content = 'from app.core.logger import logger\n' + content
            
    content = re.sub(r'print\((.*?)\)', replacer, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f'Processed {os.path.basename(file_path)}')

