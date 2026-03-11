from fastapi import FastAPI
from src.api.v1.routers import analysis, users

app = FastAPI(title="EduBot API")

app.include_router(analysis.router)
app.include_router(users.router)
