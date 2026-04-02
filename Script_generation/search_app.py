from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from chromadb import HttpClient
from sentence_transformers import SentenceTransformer
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Initialize ChromaDB and embedding model
chroma_client = HttpClient(host='localhost', port=8000)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

@app.route('/')
def search_page():
    return send_from_directory('.', 'search.html')

@app.route('/vector-search', methods=['POST'])
def vector_search():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        print(f"Searching for: {query}")  # Debug log

        # Get collection
        collection = chroma_client.get_or_create_collection(name="topics")

        # Encode query
        query_embedding = embedding_model.encode(query).tolist()

        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=10,
            include=["documents", "metadatas", "distances"]
        )

        print(f"Found {len(results['documents'][0]) if results['documents'] else 0} results")  # Debug log

        # Format results
        formatted_results = []
        for i, (doc, meta, distance) in enumerate(zip(
            results["documents"][0] if results["documents"] else [],
            results["metadatas"][0] if results["metadatas"] else [],
            results["distances"][0] if results["distances"] else []
        )):
            if meta:
                formatted_results.append({
                    'headline': meta.get('headline', 'No headline'),
                    'summary': meta.get('summary', 'No summary')  # Show summary from metadata
                })

        return jsonify({'results': formatted_results})

    except Exception as e:
        print(f"Error: {e}")  # Debug log
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🔍 Vector Search App Starting...")
    print("📝 Visit http://localhost:5001")

    import webbrowser
    webbrowser.open('http://localhost:5001')

    app.run(debug=True, host='0.0.0.0', port=5001)