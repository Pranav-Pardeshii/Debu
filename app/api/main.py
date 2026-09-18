from fastapi import FastAPI
from app.api.routes import debates

app = FastAPI()

app.include_router(debates.router)

