from fastapi import FastAPI 
from api.routes import router as api_router


app = FastAPI()
# app.add_middleware(CORSMiddleware,
# allow_origins=)

app.include_router(api_router)