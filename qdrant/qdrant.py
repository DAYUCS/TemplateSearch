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