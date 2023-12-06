import logging
import uuid
from qdrant_client import models, QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer

global qclient, encoder

def create_qdrant_client(url, api_key):  
    qclient = QdrantClient(url=url, api_key=api_key)
    return qclient

def create_embedder(ST_MODEL, ST_DEVICE):
    encoder = SentenceTransformer(ST_MODEL, device=ST_DEVICE)
    return encoder

def create_collection(collection_name="template"):
    logging.info("Creating collection." +  " Collection name:" + collection_name)

    try:
        qclient.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
                distance=models.Distance.COSINE,
            ),
        )
    except UnexpectedResponse:
        logging.error(UnexpectedResponse.content)
        return {'code': UnexpectedResponse.status_code, 'reason': UnexpectedResponse.reason_phrase}
    else:
        return {'code': 200, 'reason': 'OK'}
    
def upload_templates(transactions):
    logging.info("Uploading templates...")
    try:
        qclient.upload_records(
            collection_name="template",
            records=[
                models.Record(
                    id=str(uuid.uuid4()),
                    vector=encoder.encode(trx["transactionSummary"]).tolist(), 
                    payload=trx
                )
                for idx, trx in enumerate(transactions)
            ],
        )
    except UnexpectedResponse:
        logging.error(UnexpectedResponse.content)
        return {'code': UnexpectedResponse.status_code, 'reason': UnexpectedResponse.reason_phrase}
    else:
        return {'code': 200, 'reason': 'OK'}
    
def search_templates(user_Command, unit_Code, module_Name, customer_Id, limitRecords):
    logging.info("Searching templates...")
    try:
        hits = qclient.search(
            collection_name="template",
            query_vector=encoder.encode(user_Command).tolist(),
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="customerId", match=models.MatchAny(any=[customer_Id, ":ALL:"]) # filter by our customer, :ALL: means public templates
                    ),
                    models.FieldCondition(
                        key="unitCode", match=models.MatchValue(value=unit_Code) # filter by unit code
                    ),
                    models.FieldCondition(
                        key="moduleName", match=models.MatchValue(value=module_Name) # filter by module
                    )
                ]
            ),
            limit=limitRecords,
        )
        return hits
    except UnexpectedResponse:
        logging.error(UnexpectedResponse.content)
        return {'code': UnexpectedResponse.status_code, 'reason': UnexpectedResponse.reason_phrase}
    
def search_functions(user_Command):
    logging.info("Searching functions...")
    functions = [
        {
        "functionName": "Register Letter of Credit",
        "functionId": "F05030702010",
        "functionModule": "IPLC",
        "functionDescription": "In this function, the incoming import LC is recorded and documented in the trade finance system of the bank. It involves capturing key information such as LC number, issuing bank details, applicant and beneficiary information, LC amount, and terms and conditions.",
        "functionFields": 
        [
          {
            "fieldName": "EXPIRY_PLC",
            "fieldValue": "BENEFICIARY COUNTRY,AT OUR COUNTERS,ADVISING BANK COUNTRY,OTHER",
            "fieldDescription": "This refers to the place where the LC expires."
          },
          {
            "fieldName": "FORM_OF_LC",
            "fieldType": "SELECT",
            "fieldValue": "IRREVOCABLE, IRREVOCABLE TRANSFERABLE",
            "fieldDescription": "This indicates the type of LC."
          },
          {
            "fieldName": "EXPIRY_DT",
            "fieldType": "DATE",
            "fieldDescription": "This refers to the date on which the LC expires."
          },
          {
            "fieldName": "LC_CCY",
            "fieldType": "CCY",
            "fieldValue": "ISO4217",
            "fieldDescription": "Use the fields provided to specify the currency of the LC."
          },
          {
            "fieldName": "LC_AMT",
            "fieldType": "AMOUNT",
            "fieldDescription": "Use the fields provided to specify the amount of the LC."
          },
          {
            "fieldName": "APPLICANT",
            "fieldType": "CUSTOMER",
            "fieldDescription": "This refers to the Id of the Applicant."
          },
          {
            "fieldName": "ADVISE_BANK",
            "fieldType": "BANK",
            "fieldDescription": "This refers to the Id of the Advising Bank."
          },
          {
            "fieldName": "AVAL_BY",
            "fieldType": "SELECT",
            "fieldValue": "BY PAYMENT, BY ACCEPTANCE, BY NEGOTIATION, BY DEF PAYMENT, BY MIXED PYMT",
            "fieldDescription": "This indicates the method by which the LC is available."
          }
        ]
      },
      {
        "functionName": "Issue Letter of Credit",
        "functionId": "F05030702015",
        "functionModule": "IPLC",
        "functionDescription": "This function involves the issuance of the import LC by the bank on behalf of the importer. The bank prepares the LC document, including the terms and conditions, and sends it to the beneficiary (exporter) or their bank.",
        "functionFields":
        [
          {
            "fieldName": "FORM_OF_LC",
            "fieldType": "SELECT",
            "fieldValue": "IRREVOCABLE, IRREVOCABLE TRANSFERABLE",
            "fieldDescription": "Form of Documentary Credit"
          },
          {
            "fieldName": "EXPIRY_PLC",
            "fieldType": "SELECT",
            "fieldValue": "BENEFICIARY COUNTRY,AT OUR COUNTERS,ADVISING BANK COUNTRY,OTHER",
            "fieldDescription": "Expiry Place"
          },
          {
            "fieldName": "APLB_RULE",
            "fieldType": "SELECT",
            "fieldValue": "EUCP LATEST VERSION,EUCPURR LATEST VERSION,OTHER,UCP LATEST VERSION,UCPURR LATEST VERSION",
            "fieldDescription": "Applicable Rules"
          },
          {
            "fieldName": "AVAL_BY",
            "fieldType": "SELECT",
            "fieldValue": "BY PAYMENT, BY ACCEPTANCE, BY NEGOTIATION, BY DEF PAYMENT, BY MIXED PYMT",
            "fieldDescription": "Available By"
          }
        ]
      }
    ]
    return functions