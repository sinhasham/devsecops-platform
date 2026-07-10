from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import os
import time

app = FastAPI(title="DevSecOps Platform API", version="1.0.0")

Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
def root():
    return {"message": "Welcome to DevSecOps Platform API"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}

@app.post("/items")
def create_item(name: str):
    return {"name": name, "created": True}

@app.get("/db-check")
def db_check():
    db_host = os.getenv("DB_HOST", "not-configured")
    return {"db_host": db_host, "status": "connected (simulated)"}
