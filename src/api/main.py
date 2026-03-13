from fastapi import FastAPI
from .v1.routers import dulcineav1

app = FastAPI(title="Dulcinea")

app.include_router(dulcineav1.router)

