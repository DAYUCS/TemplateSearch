import logging
import json
from pydantic import BaseModel
from typing import List
from fastapi import APIRouter
from qdrant import qdrant

class Transaction(BaseModel):
    transactionSummary: str
    unitCode: str
    moduleName: str
    referenceNumber: str
    eventNumber: int
    customerId: str

    class Config:
        schema_extra = {
            "example": {
                "transactionSummary": "Initiate performance bond gurantee for Dubai water company with USD 10,000",
                "unitCode": "HED0001",
                "moduleName": "XXBG",
                "referenceNumber": "XXBG0001",
                "eventNumber": 1,
                "customerId": "CUST-00001"
            }
        }

router = APIRouter(prefix="/template",
    tags=["template"])

# create template collection
@router.put("/create")
async def create_template_collection():
    logging.info("Creating collection template")
    return qdrant.create_collection('template')

# upload templates
@router.post("/upload")
async def upload_templates(transactions: List[Transaction]):
    logging.info("Uploading templates")
    json_data = json.dumps(transactions, default=lambda x: x.__dict__)
    json_object = json.loads(json_data)
    return qdrant.upload_templates(json_object)

# search templates
@router.get("/search")
async def search_templates(userCommand: str, unitCode: str, moduleName: str, customerId: str, limit: int = 3):
    logging.info("Searching templates")
    return qdrant.search_templates(userCommand, unitCode, moduleName, customerId, limit)