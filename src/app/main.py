"""Main application entry point."""
from fastapi import FastAPI

app = FastAPI(
    title="SVC Censorium",
    description="Service API",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to SVC Censorium"}
