import logging
import uuid
from qdrant_client import models, QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer

global qclient, encoder

def create_qdrant_client(url, api_key):  
    qclient = QdrantClient(url=url, api_key=api_key)
    return qclient

def create_embedder():
    encoder = SentenceTransformer("../../../sentencetransformer/paraphrase-multilingual-mpnet-base-v2", device="cpu") # or device="cuda" if you have a GPU
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