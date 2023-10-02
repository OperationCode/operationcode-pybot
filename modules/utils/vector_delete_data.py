"""Configuration for a vector database connection."""
import os

import weaviate
from dotenv import load_dotenv

load_dotenv()

# Weaviate configuration
auth_config = weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY", ""))

# Create a weaviate client
weaviate_client = weaviate.Client(os.getenv("WEAVIATE_URL", "http://localhost:8015"), auth_client_secret=auth_config)


weaviate_client.batch.delete_objects("TextChunk", where={"operator": "Like", "valueText": "*", "path": ["text"]})
