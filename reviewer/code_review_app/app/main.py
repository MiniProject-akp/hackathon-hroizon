from fastapi import FastAPI
from app.api import analyze, webhook
from app.services.database import init_db

app = FastAPI(title="AI Code Review App")

@app.on_event("startup")
async def startup_event():
    init_db()  # Initialize SQLite (optional)

app.include_router(analyze.router, prefix="/api")
app.include_router(webhook.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 