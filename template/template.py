import logging
from fastapi import APIRouter, status
from qdrant import qdrant

router = APIRouter(prefix="/template",
    tags=["template"])

@router.get("/hello", status_code=status.HTTP_200_OK)
async def template_hello():
    return {"message": "Hello Templates"}

# create template collection
@router.put("/create")
async def create_template_collection():
    logging.info("Creating collection template")
    return qdrant.create_collection('template')