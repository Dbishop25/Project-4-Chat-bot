from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.boardgame import chat_router, router
from backend.core.config import settings


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(router)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "Hello, Welcome to Boardgame Documentation."}
