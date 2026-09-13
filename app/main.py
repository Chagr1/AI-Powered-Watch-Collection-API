from fastapi import FastAPI
from app.database.database import engine
from app.models import watch,user
from app.routers import watches,auth







app = FastAPI(
    title="AI-Powered Watch Collection API",
    description="A robust backend service for managing a watch collection with AI enrichment.",
    version="1.0.0"
)


app.include_router(auth.router)
app.include_router(watches.router)


@app.get("/", tags=["General"])
def root():
    return {
        "message": "Welcome to the AI-Powered Watch API!",
        "documentation": "Visit http://127.0.0.1:8000/docs to explore the API."
    }