# vectorize_topics.py
from chromadb.config import Settings
from chromadb.client import Client
import os
import json

# Connect to Chroma DB
client = Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./data/chroma"
))

# Example: load topics from JSON and insert into Chroma
TOPIC_FOLDER = "./data/topics"

for fname in os.listdir(TOPIC_FOLDER):
    if fname.endswith(".json"):
        with open(os.path.join(TOPIC_FOLDER, fname), "r", encoding="utf-8") as f:
            data = json.load(f)
        for topic in data.get("topics", []):
            client.collections.create_if_not_exists(name="topics")
            collection = client.collections.get("topics")
            collection.add(
                ids=[topic["topic_id"]],
                metadatas=[topic],
                documents=[topic["description"]]
            )

print("✅ Vectorization complete!")