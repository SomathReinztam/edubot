from fastapi import FastAPI
from src.api.v1.routers import users, analysis

app = FastAPI(title="EduBot API")

app.include_router(users.router)
app.include_router(analysis.router)
