#main.py
import os
import uvicorn
import logging.config
import yaml

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from pathlib import Path
from template import template
from qdrant import qdrant

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

# create qdrant client and embedding encoder
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
logging.info("Creating qdrant client to " + QDRANT_URL)
qdrant.qclient = qdrant.create_qdrant_client(QDRANT_URL, QDRANT_API_KEY)
logging.info("Creating embedder")
qdrant.encoder = qdrant.create_embedder()

app = FastAPI()

app.include_router(template.router)

#logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

if __name__ == "__main__":
    config = uvicorn.Config("main:app", port=8000, log_level="info", host="0.0.0.0", reload=True)
    server = uvicorn.Server(config)
    server.run()

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Eximbills Transaction AI Service</title>
        </head>
        <body>
            <h1>Welcome to Eximbills Transaction AI Service</h1>
            <A href="/docs">Try it out</A>
        </body>
    </html>
    """
