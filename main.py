#main.py
import os
import uvicorn
import logging.config
import yaml

from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
from template import template
from qdrant import qdrant
from function import function
from llm import llm

# load parameters from .env
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

# Get the environment
environment = os.getenv('ENVIRONMENT')

# Load logging config file
with open('logging_config.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())

# Configure the logging module with the config file
logging.config.dictConfig(config)

# Get a logger object
logger = logging.getLogger(environment)

# Create qdrant client
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
logging.info("Creating qdrant client to " + QDRANT_URL)
qdrant.qclient = qdrant.create_qdrant_client(QDRANT_URL, QDRANT_API_KEY)

# Create embedding encoder
ST_MODEL = os.getenv('ST_MODEL')
ST_DEVICE = os.getenv('ST_DEVICE')
logging.info("Creating embedder")
qdrant.encoder = qdrant.create_embedder(ST_MODEL, ST_DEVICE)

# Get OpenAI Key and Model
llm.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm.OPENAI_MODEL = os.getenv("OPENAI_MODEL")
llm.PROMPTS_PATH = os.getenv("PROMPTS_PATH")

app = FastAPI()

origins = [
    "http://10.39.101.14",
    "https://10.39.101.14:4200",
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(template.router)
app.include_router(function.router)

#logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

if __name__ == "__main__":
    config = uvicorn.Config("main:app", port=8000, log_level="info", host="0.0.0.0", reload=True)
    server = uvicorn.Server(config)
    server.run()

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return """
    <html>
        <head>
            <title>Eximbills Transaction AI Service</title>
            <link rel="icon" type="image/x-icon" href="/images/favicon.ico">
        </head>
        <body>
            <h1>Welcome to Eximbills Transaction AI Service</h1>
            <A href="/docs">Try it out</A>
        </body>
    </html>
    """

@app.get('/images/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('./images/favicon.ico')

# Startup Probe for K8s
@app.get("/health/startup", status_code=status.HTTP_200_OK)
async def startup_status():
    return {"message": "OK"}

@app.get("/health/liveness", status_code=status.HTTP_200_OK)
async def liveness_status():
    # TODO Will check embedding/qdrant/LLM status And return details
    return {"message": "OK"}

@app.get("/health/readiness", status_code=status.HTTP_200_OK)
async def readiness_status():
    # TODO Will check embedding/qdrant/LLM status And return HTTP Header & 200/500
    return {"message": "OK"}