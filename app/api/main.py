from fastapi import FastAPI
from app.api.routes import debates, debates_ws

app = FastAPI()

app.include_router(debates.router)
app.include_router(debates_ws.router)

