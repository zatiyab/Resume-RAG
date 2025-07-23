from fastapi import FastAPI 
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.routes import router as api_router


app = FastAPI()
# app.add_middleware(CORSMiddleware,
# allow_origins=)

app.include_router(api_router)