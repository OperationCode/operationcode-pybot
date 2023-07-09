import os

import weaviate
from dotenv import load_dotenv

load_dotenv()

print("Starting weaviate client...")
weaviate_client = weaviate.Client(os.getenv("WEAVIATE_URL", "http://localhost:8015"))

print("Retrieve results...")
results = (
    weaviate_client.query.get(
        class_name="TextChunk", properties=["text", "ingestion_date", "index_number", "unique_id"]
    )
    .with_limit(10)
    .with_near_text(
        {
            "concepts": [
                "the VET TEC (Veteran Employment Through Technology Education Courses) program is a VA (Department of Veterans Affairs) initiative that provides funding for eligible veterans to receive training in technology-related fields. Under the VET TEC program, there is no specific maximum amount allowed for a single veteran. However, the program covers the cost of tuition and fees for eligible veterans, up to a maximum of $10,000. It's important to note that the funding provided is for the training program itself and does not cover additional expenses such as housing or books."
            ]
        }
    )
    .do()
)

results = results.get("data", {}).get("Get").get("TextChunk", {})
print(f"Found {len(results)} results:")
for i, article in enumerate(results):
    print(f"\t{i}. {article['text']}\n\n")
