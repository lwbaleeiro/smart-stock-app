from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import health, upload, predictions
from app.core.database import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    print("Iniciando aplicação...")
    create_tables()
    yield
    # On shutdown
    print("Encerrando aplicação...")

app = FastAPI(
    title="Quantyfy API",
    description="API para a plataforma de inteligência preditiva Quantyfy.",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API Quantyfy!"}

# Routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
