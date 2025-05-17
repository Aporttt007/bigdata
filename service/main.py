from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Добавляем текущую папку
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Добавляем backend
from db import db

app = FastAPI(
    title="AliExpress Clone API",
    description="Microservice for product management",
    version="1.0.0",
)

# CORS Middleware (if needed)
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],  # Change to specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Root Endpoint
@app.get("/")
async def root():
    return {"message": "FastAPI Microservice is running!"}
