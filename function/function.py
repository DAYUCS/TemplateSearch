import logging
import yaml
import json
from pydantic import BaseModel
from typing import List, Optional
from fastapi import APIRouter
from qdrant import qdrant
from llm import llm

class Field(BaseModel):
    fieldName: str
    fieldType: str
    fieldValue: Optional[str] = None
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

# create function collection on vector database(qdrant)
@router.put("/create")
async def create_function_collection():
    logging.info("Creating collection function")
    return qdrant.create_collection('function')

# upload functions to the collection
@router.post("/upload")
async def upload_functions(functions: List[Function]):
    logging.info("Uploading functions")
    json_data = json.dumps(functions, default=lambda x: x.__dict__)
    json_object = json.loads(json_data)
    return qdrant.upload_functions(json_object)

# find out which function the user intended to perform
@router.get("/find")
async def find_function(userCommand: str):
    logging.info("Finding out which function the user intended to perform")

    # Step 1: search functions from the collection on vector database
    functions = qdrant.search_functions(userCommand)

    # Step 2: let llm identify function and key fields
    functions_yaml = yaml.dump(functions)
    response = llm.identify_function(userCommand, functions_yaml)
    
    # Step 3: identify CUBK ID

    return response