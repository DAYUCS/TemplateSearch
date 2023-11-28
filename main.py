#main.py
import os
import uvicorn
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from template import template
from qdrant import qdrant

# load parameters from .env
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

# create qdrant client and embedding encoder
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
qdrant.qclient = qdrant.create_qdrant_client(QDRANT_URL, QDRANT_API_KEY)
qdrant.encoder = qdrant.create_embedder()

app = FastAPI()

app.include_router(template.router)

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

if __name__ == "__main__":
    config = uvicorn.Config("main:app", port=8000, log_level="info", host="0.0.0.0", reload=True)
    server = uvicorn.Server(config)
    server.run()

class Product(BaseModel):
    prodId: int
    prodName: str
    price: float
    stock: int

    class Config:
        schema_extra = {
            "example": {
                "prodId": 1,
                "prodName": "Iphone",
                "price": 100,
                "stock": 10
            }
        }

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/employee/{name}/{age}")
async def employee(name:str, age:int):
    return {"name": name, "age": age}

@app.get("/employee/{name}")
async def get_employee(name:str, age:int=57):
    return {"name": name, "age": age}

@app.post("/product")
async def addnew(product:Product):
    return product
