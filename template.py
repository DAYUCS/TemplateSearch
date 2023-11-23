from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("../../sentencetransformer/paraphrase-multilingual-mpnet-base-v2", device="cpu") # or device="cuda" if you have a GPU

documents = [
    {
        "type": "BG",
        "sub-type": "Performance Bond Guarantee",
        "their-customer": "Dubai water and electricity company",
        "currency": "AED",
        "amount": 100000,
        "transaction-date": "2023-10-01",
        "our-customer": "CUST-00001",
        "rdb-id": "RDB-00001",
    },
    {
        "type": "BG",
        "sub-type": "Advance Payment Guarantee",
        "their-customer": "Dubai water and electricity company",
        "currency": "USD",
        "amount": 120000,
        "transaction-date": "2023-10-19",
        "our-customer": "CUST-00001",
        "rdb-id": "RDB-00002",
    },
    {
        "type": "BG",
        "sub-type": "Warranty bond Guarantee",
        "their-customer": "Dubai water and electricity company",
        "currency": "EUR",
        "amount": 220000,
        "transaction-date": "2023-10-19",
        "our-customer": "CUST-00001",
        "rdb-id": "RDB-00003",
    },
    {
        "type": "BG",
        "sub-type": "Performance Bond Guarantee",
        "their-customer": "Dubai water and electricity company",
        "currency": "AED",
        "amount": 100000,
        "transaction-date": "2023-10-01",
        "our-customer": "CUST-00002",
        "rdb-id": "RDB-00004",
    },
    {
        "type": "BG",
        "sub-type": "Performance Bond Guarantee",
        "their-customer": "Dubai water and electricity company",
        "currency": "USD",
        "amount": 100000,
        "transaction-date": "2023-10-01",
        "our-customer": ":ALL:",
        "rdb-id": "RDB-00005",
    },
    {
        "type": "BG",
        "sub-type": "Performance Bond Guarantee",
        "their-customer": "Dubai water and electricity company",
        "currency": "CNY",
        "amount": 1000000,
        "transaction-date": "2022-10-01",
        "our-customer": "CUST-00001",
        "rdb-id": "RDB-00006",
    },
    {
        "type": "BG",
        "sub-type": "Performance Bond Guarantee",
        "their-customer": "Chinasystems company",
        "currency": "CNY",
        "amount": 1000000,
        "transaction-date": "2022-10-01",
        "our-customer": "CUST-00001",
        "rdb-id": "RDB-00007",
    },
    {
        "type": "LC",
        "sub-type": "Stand-by LC",
        "their-customer": "Dubai water and electricity company",
        "currency": "AED",
        "amount": 100000,
        "transaction-date": "2023-10-01",
        "our-customer": "CUST-00001",
        "rdb-id": "RDB-00008",
    },
    {
        "type": "LC",
        "sub-type": "Confirmed LC",
        "their-customer": "Dubai water and electricity company",
        "currency": "AED",
        "amount": 100000,
        "transaction-date": "2023-10-01",
        "our-customer": "CUST-00001",
        "rdb-id": "RDB-00009",
    },
    
]

qdrant = QdrantClient(url="http://10.39.101.186:6333", api_key="eximbills2024futures")

qdrant.recreate_collection(
    collection_name="my_templates",
    vectors_config=models.VectorParams(
        size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
        distance=models.Distance.COSINE,
    ),
)

qdrant.upload_records(
    collection_name="my_templates",
    records=[
        models.Record(
            id=idx, vector=encoder.encode(
                "The transaction is for " + doc["their-customer"] + 
                ". The transaction type is " + doc["sub-type"] + 
                ", and the amount is " + doc["currency"] + " " + str(doc["amount"]) + 
                " and the transaction date is " + doc["transaction-date"]
                ).tolist(), payload=doc
        )
        for idx, doc in enumerate(documents)
    ],
)

hits = qdrant.search(
    collection_name="my_templates",
    query_vector=encoder.encode("Initiate performance guarantee for Dubai water and electricity for AED 12000").tolist(),
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="our-customer", match=models.MatchAny(any=["CUST-00001", ":ALL:"]) # filter by our customer, :ALL: means public templates
            ),
            models.FieldCondition(
                key="sub-type", match=models.MatchValue(value="Performance Bond Guarantee") # filter by transaction type
            )
        ]   
    ),
    limit=3,
)

for hit in hits:
    print(hit.payload, "score:", hit.score)