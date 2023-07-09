"""Configuration for a vector database connection."""
import os

import weaviate
from dotenv import load_dotenv

load_dotenv()

# Weaviate configuration
auth_config = weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY", ""))

# Create a weaviate client
weaviate_client = weaviate.Client(os.getenv("WEAVIATE_URL", "http://localhost:8015"), auth_client_secret=auth_config)

# Create the schema
class_obj = {
    "class": "TextChunk",
    "description": "A chunk of text from the Federal Title Code.",
    "properties": [
        {"name": "text", "dataType": ["text"]},
        {"name": "cfr_title_number", "dataType": ["int"]},
        {"name": "ingestion_date", "dataType": ["date"]},
        {"name": "index_number", "dataType": ["int"]},
        {"name": "unique_id", "dataType": ["uuid"]},
        {"name": "surrounding_context", "dataType": ["text"]},
    ],
    "vectorizer": "text2vec-transformers",
    "vectorIndexConfig": {
        "ef": 450,
    },
}

try:
    weaviate_client.schema.create_class(class_obj)
except weaviate.exceptions.UnexpectedStatusCodeException:
    print("Schema already exists.")

try:
    weaviate_client.schema.update_config("TextChunk", class_obj)
except weaviate.exceptions.UnexpectedStatusCodeException as e:
    print(e)
    print("Schema already updated.")
