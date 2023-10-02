"""Utilities to assist with ingesting documents and turning them into vectors."""
import datetime
import os
import uuid

import weaviate
from dotenv import load_dotenv
from transformers import AutoTokenizer
from unstructured.cleaners.core import clean
from unstructured.documents.elements import Text
from unstructured.partition.pdf import partition_pdf
from unstructured.staging.huggingface import stage_for_transformers

load_dotenv()

# Weaviate configuration
auth_config = weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY", ""))

# Create a weaviate client
weaviate_client = weaviate.Client(os.getenv("WEAVIATE_URL", "http://localhost:8015"), auth_client_secret=auth_config)


def main() -> None:
    weaviate_client.batch.configure(batch_size=300)
    try:
        model_name = "sentence-transformers/all-mpnet-base-v2"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        elements = partition_pdf(
            "/Users/judson/Projects/OperationCode/operationcode-pybot/data/VA-Documents/2020-CFR-Title38-Vol-1.pdf",
            strategy="ocr_only",
        )
        staged_elements = stage_for_transformers(
            [element for element in elements if isinstance(element, Text)],
            tokenizer,
        )
        no_items_in_batch = 0
        batch_size = 300
        for idx, element in enumerate(staged_elements):
            if isinstance(element, Text):
                clean_text = clean(
                    element.text,
                    bullets=True,
                    extra_whitespace=True,
                )
                text_chunk = {
                        "text": clean_text,
                        "cfr_title_number": 38,
                        "ingestion_date": str(datetime.datetime.now(tz=datetime.timezone.utc).isoformat()),
                        "index_number": idx,
                        "unique_id": str(uuid.uuid4()),
                    }
                print("Adding object to batch. On number: " + str(idx))
                weaviate_client.batch.add_data_object(text_chunk, "TextChunk")
                no_items_in_batch += 1
                if no_items_in_batch >= batch_size:
                    print("Sending batch...")
                    print("Currently at count: ", idx)
                    weaviate_client.batch.create_objects()
                    no_items_in_batch = 0
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
