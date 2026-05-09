import re

file_path = r'd:\Resume_RAG\Resume-RAG\app\services\qdrant_client.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add import at the top
if 'from app.core.logger import logger' not in content:
    content = content.replace('from qdrant_client.http import models as rest', 'from qdrant_client.http import models as rest\nfrom app.core.logger import logger')

# Replace print( with logger.debug( or logger.error( or logger.info(
def replacer(match):
    full_print = match.group(0)
    args = match.group(1)
    
    # Remove flush=True if it exists
    args = re.sub(r',\s*flush=True', '', args)

    if 'error' in args.lower() or 'failed' in args.lower() or 'warning' in args.lower():
        return f'logger.error({args})'
    elif 'debug' in args.lower():
        return f'logger.debug({args})'
    else:
        return f'logger.info({args})'

# This simple regex assumes no nested parentheses in print() arguments that contain other prints
# Actually, a better regex is to match the start of print( and then balance parentheses
# But let's just use a simple regex that matches print(...) on a single line
content = re.sub(r'print\((.*?)\)', replacer, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Replaced in qdrant_client.py')
