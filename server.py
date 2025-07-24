# backend/server.py (UPDATED to run Uvicorn)
import uvicorn
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.main import app as application

if __name__ == '__main__':
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0",  
        port=5000,       
        reload=True,     
        reload_dirs=[os.path.join(os.path.dirname(__file__), 'app')]
    )