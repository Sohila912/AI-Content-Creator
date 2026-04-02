from pymongo import MongoClient
import chromadb
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
chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(name="topics")

# =========================
# 3. Load embedding model
# =========================
model = SentenceTransformer("all-MiniLM-L6-v2")

# =========================
# 4. Load topics from MongoDB
# =========================
topics = list(topics_collection.find())

print(f"Found {len(topics)} topics")

# =========================
# 5. Insert into ChromaDB
# =========================
for topic in topics:
    text = topic.get("title", "Untitled topic")
    topic_id = str(topic["_id"])

    embedding = model.encode(text).tolist()

    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[topic_id]
    )

print("✅ Topics stored in ChromaDB!")

# =========================
# 6. Test semantic search
# =========================
query = input("\n🔍 Enter search query: ")

query_embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print("\n🎯 Top Results:")
for i, doc in enumerate(results["documents"][0]):
    print(f"{i+1}. {doc}")