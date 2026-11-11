from fastapi import FastAPI
from backend.api.boardgame import router


app = FastAPI()

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Hello, Welcome to Boardgame Documentation."}