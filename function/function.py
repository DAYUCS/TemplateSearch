import logging
import json
from pydantic import BaseModel
from typing import List
from fastapi import APIRouter
from qdrant import qdrant

class Field(BaseModel):
    fieldName: str
    fieldType: str
    fieldValue: str
    fieldDescription: str

    class Config:
        schema_extra = {
            "example": {
                "fieldName": "EXPIRY_PLC",
                "fieldType": "SELECT",
                "fieldValue": "BENEFICIARY COUNTRY, AT OUR COUNTERS, ADVISING BANK COUNTRY, OTHER",
                "fieldDescription": "the place where the LC expires"
                }
        }

class Function(BaseModel):
    functionName: str
    functionId: str
    functionModule: str
    functionDescription: str
    functionFields: List[Field]

    class Config:
        schema_extra = {
            "example": {
                "functionName": "Register Letter of Credit",
                "functionId": "F05030702010",
                "functionModule": "IPLC",
                "functionDescription": "In this function, the incoming import LC is recorded and documented in the trade finance system of the bank. It involves capturing key information such as LC number, issuing bank details, applicant and beneficiary information, LC amount, and terms and conditions.",
                "functionFields": [
                    {"fieldName": "EXPIRY_PLC", "fieldType": "SELECT", "fieldValue": "BENEFICIARY COUNTRY, AT OUR COUNTERS, ADVISING BANK COUNTRY, OTHER", "fieldDescription": "the place where the LC expires"},
                    {"fieldName": "FORM_OF_LC", "fieldType": "SELECT", "fieldValue": "IRREVOCABLE, IRREVOCABLE TRANSFERABLE", "fieldDescription": "the type of LC"}
                ]
            }
        }

router = APIRouter(prefix="/function",
    tags=["function"])

# create function collection
@router.put("/create")
async def create_function_collection():
    logging.info("Creating collection function")
    return qdrant.create_collection('function')