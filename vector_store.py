from pymongo import MongoClient
from chromadb import HttpClient
from sentence_transformers import SentenceTransformer

# =========================
# 1. Connect to MongoDB
# =========================
client = MongoClient("mongodb://admin:password@localhost:27017/")
db = client["youtube_ai"]
topics_collection = db["topics"]

# =========================
# 2. Connect to ChromaDB
# =========================
chroma_client = HttpClient(host='localhost', port=8000)

# Delete existing collection to start fresh
try:
    chroma_client.delete_collection(name="topics")
except:
    pass

collection = chroma_client.get_or_create_collection(name="topics")

# =========================
# 3. Load embedding model
# =========================
model = SentenceTransformer("all-MiniLM-L6-v2")

# =========================
# 4. Load topics from MongoDB
# =========================
topics_docs = list(topics_collection.find())

print(f"Found {len(topics_docs)} topic documents")

# =========================
# 5. Insert into ChromaDB
# =========================
for doc in topics_docs:
    for topic in doc.get("topics", []):
        text = topic.get("summary", "No summary")
        topic_id = topic["topic_id"]

        embedding = model.encode(text).tolist()

        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[topic_id],
            metadatas=[topic]
        )

print("✅ Topics stored in ChromaDB!")

# =========================
# 6. Test semantic search
# =========================
query = input("\n🔍 Enter search query: ")

query_embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    include=["documents", "metadatas"]
)

print("\n🎯 Top Results:")
for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
    if meta:
        headline = meta.get("headline", "No headline")
    else:
        headline = "No headline"
    print(f"{i+1}. {headline}")
    print(f"   Summary: {doc}")
    print()