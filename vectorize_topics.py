# vectorize_topics.py
from chromadb import HttpClient
import os
import json

# Connect to Chroma DB server
client = HttpClient(host='localhost', port=8000)

# Delete existing collection to start fresh
try:
    client.delete_collection(name="topics")
except:
    pass

# Create or get the collection
collection = client.get_or_create_collection(name="topics")

# Example: load topics from JSON and insert into Chroma
TOPIC_FOLDER = "./data/topics"

total_topics = 0
for fname in os.listdir(TOPIC_FOLDER):
    if fname.endswith(".json"):
        with open(os.path.join(TOPIC_FOLDER, fname), "r", encoding="utf-8") as f:
            data = json.load(f)
        for topic in data.get("topics", []):
            collection.add(
                ids=[topic["topic_id"]],
                metadatas=[topic],
                documents=[topic["headline"]]
            )
            total_topics += 1

print(f"✅ Vectorization complete! Added {total_topics} topics from {len([f for f in os.listdir(TOPIC_FOLDER) if f.endswith('.json')])} files.")