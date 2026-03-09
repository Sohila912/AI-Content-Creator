from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import json
from urllib.parse import urlparse
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime, UTC

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# Initialize Groq client
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)

# Tavily API configuration
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
TAVILY_API_URL = "https://api.tavily.com/search"

# Create data folders
TOPIC_FOLDER = "data/topics"
SCRIPT_FOLDER = "data/scripts"

os.makedirs(TOPIC_FOLDER, exist_ok=True)
os.makedirs(SCRIPT_FOLDER, exist_ok=True)


# -------------------------
# Helper Functions
# -------------------------

def get_domain(url):
    try:
        return urlparse(url).netloc
    except:
        return ""


def get_next_filename(folder, prefix):
    """
    Generates filenames like:
    topics_metadata_001.json
    topics_metadata_002.json
    """
    existing = [f for f in os.listdir(folder) if f.startswith(prefix)]

    if not existing:
        return f"{prefix}_001.json"

    numbers = []

    for f in existing:
        try:
            num = int(f.split("_")[-1].split(".")[0])
            numbers.append(num)
        except:
            pass

    next_num = max(numbers) + 1 if numbers else 1

    return f"{prefix}_{str(next_num).zfill(3)}.json"


def save_json(folder, prefix, data):
    filename = get_next_filename(folder, prefix)
    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return filepath


# -------------------------
# Routes
# -------------------------

@app.route('/')
def index():
    return send_from_directory('.', 'ideas.html')


@app.route('/script')
def script_page():
    return send_from_directory('.', 'index.html')


@app.route('/ideas')
def ideas_page():
    return send_from_directory('.', 'ideas.html')


# -------------------------
# Topic Search Agent
# -------------------------

@app.route('/search-topics', methods=['POST'])
def search_topics():

    try:

        data = request.get_json()
        idea_query = data.get('query', '').strip()
        time_range = data.get('time_range', 'week')
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        max_results = int(data.get('max_results', 8))

        if not idea_query:
            return jsonify({'error': 'Query is required'}), 400

        query = f"{idea_query} trending topics latest insights"

        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": False,
            "max_results": max_results,
            "time_range": time_range
        }

        if start_date and end_date:
            payload["time_range"] = "custom"
            payload["start_date"] = start_date
            payload["end_date"] = end_date

        response = requests.post(TAVILY_API_URL, json=payload, timeout=30)

        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f"Tavily API Error {response.status_code}: {response.text}"
            }), response.status_code

        result = response.json()
        results = result.get('results', [])

        topics = []

        for i, item in enumerate(results):

            title = item.get('title', 'Untitled')
            snippet = item.get('content', '') or item.get('snippet', '')
            url = item.get('url', '')
            published = item.get('published_date', '')
            score = item.get('score', None)

            # topics.append({

            #     "topic_id": f"topic_{i+1:03}",
            #     "headline": title,
            #     "summary": snippet[:200],
            #     "published_date": published,
            #     "source_url": url,
            #     "source_domain": get_domain(url),
            #     "relevance_score": score,
            #     "keywords": idea_query.split(),
            #     "content_snippet": snippet,
            #     "discovered_by_query": query,
            #     "language": "en"

            # })
            topics.append({

                "topic_id": f"topic_{i+1:03}",

                # frontend fields
                "title": title,
                "description": snippet[:200],
                "url": url,

                # metadata fields
                "headline": title,
                "summary": snippet[:200],
                "source_url": url,
                "source_domain": get_domain(url),
                "keywords": idea_query.split(),
                "published_date": item.get("published_date", ""),
                "relevance_score": item.get("score", None)

        })

        topics_json = {

            "generated_at": datetime.now(UTC).isoformat(),
            "query": idea_query,
            "time_range": time_range,
            "topics_count": len(topics),
            "topics": topics

        }

        print("Topics returned:", topics)

        file_path = save_json(TOPIC_FOLDER, "topics_metadata", topics_json)

        return jsonify({
            'success': True,
            'topics': topics,
            'saved_to': file_path
        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)  
        }), 500


# -------------------------
# Script Generation Agent
# -------------------------

@app.route('/generate-script', methods=['POST'])
def generate_script():

    try:

        data = request.get_json()
        topic = data.get('topic', '')
        script_type = data.get('script_type', 'general')
        duration = data.get('duration', '2-3 minutes')
        tone = data.get('tone', 'professional')

        if not topic:
            return jsonify({'error': 'Topic is required'}), 400

        prompt = f"""
You are a professional script writer for Moonify.

Write a compelling {script_type} script about:

{topic}

Requirements:

- Duration: {duration}
- Tone: {tone}
- Strong hook
- Clear introduction
- Engaging main content
- Strong conclusion
- Conversational voice-over style
"""

        chat_completion = client.chat.completions.create(

            messages=[
                {"role": "system", "content": "You are an expert script writer."},
                {"role": "user", "content": prompt}
            ],

            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=2048

        )

        script = chat_completion.choices[0].message.content

        script_data = {

            "generated_at": datetime.now(UTC).isoformat(),

            "script": {

                "topic": topic,
                "script_type": script_type,
                "duration_target": duration,
                "tone": tone,
                "estimated_word_count": len(script.split()),
                "target_platform": "general",
                "language": "en",
                "model_used": "llama-3.3-70b-versatile",
                "script_text": script

            }

        }

        file_path = save_json(SCRIPT_FOLDER, "script_output", script_data)

        return jsonify({

            'success': True,
            'script': script,
            'topic': topic,
            'script_type': script_type,
            'saved_to': file_path

        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/summarize-idea', methods=['POST'])
def summarize_idea():

    try:

        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'error': 'Text is required'}), 400

        prompt = f"""
Summarize the following idea in **maximum two lines**.

Idea:
{text}
"""

        chat_completion = client.chat.completions.create(

            messages=[
                {"role": "system", "content": "You summarize ideas clearly and concisely."},
                {"role": "user", "content": prompt}
            ],

            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=120

        )

        summary = chat_completion.choices[0].message.content.strip()

        return jsonify({
            'success': True,
            'summary': summary
        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# -------------------------
# Health Check
# -------------------------

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "Moonify Script Generator"
    })


if __name__ == '__main__':

    print("🌙 Moonify Script Generator Starting...")
    print("📝 Visit http://localhost:5000")

    app.run(debug=True, host='0.0.0.0', port=5000)
