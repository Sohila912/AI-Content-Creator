from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import requests
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# Initialize Groq client
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)

# Tavily API configuration
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
TAVILY_API_URL = "https://api.tavily.com/search"

@app.route('/')
def index():
    """Serve the HTML frontend"""
    return send_from_directory('.', 'ideas.html')

@app.route('/script')
def script_page():
    """Serve the script generator page"""
    return send_from_directory('.', 'index.html')

@app.route('/ideas')
def ideas_page():
    """Serve the ideas page"""
    return send_from_directory('.', 'ideas.html')

@app.route('/search-topics', methods=['POST'])
def search_topics():
    """Search for trending topics using Tavily"""
    try:
        data = request.get_json()
        idea_query = data.get('query', '').strip()
        time_range = data.get('time_range', 'week')
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        max_results = int(data.get('max_results', 8))

        if not idea_query:
            return jsonify({'error': 'Query is required'}), 400

        if (start_date and not end_date) or (end_date and not start_date):
            return jsonify({'error': 'Both start and end dates are required'}), 400

        # Expand the query to emphasize trending topics
        query = f"{idea_query} trending topics latest insights"

        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": False,
            "max_results": max_results,
            "time_range": time_range,
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
        for item in results:
            title = item.get('title', 'Untitled')
            snippet = item.get('content', '') or item.get('snippet', '')
            url = item.get('url', '')
            description = snippet.strip() if snippet else "No description available."

            topics.append({
                "title": title,
                "description": description,
                "url": url,
                "copy_text": f"Topic: {title}\nDescription: {description}\nSource: {url}"
            })

        return jsonify({
            'success': True,
            'query': idea_query,
            'time_range': time_range,
            'start_date': start_date,
            'end_date': end_date,
            'answer': result.get('answer', ''),
            'topics': topics
        })

    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Tavily request timed out. Please try again.'
        }), 504
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-script', methods=['POST'])
def generate_script():
    """Generate a script based on the user's topic"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        script_type = data.get('script_type', 'general')
        duration = data.get('duration', '2-3 minutes')
        tone = data.get('tone', 'professional')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Create a detailed prompt for script generation
        prompt = f"""You are a professional script writer for Moonify. Write a compelling and engaging {script_type} script about: {topic}

Script Requirements:
- Duration: {duration}
- Tone: {tone}
- Include a strong hook/introduction
- Clear structure with introduction, main content, and conclusion
- Engaging and conversational language
- Professional formatting with scene descriptions or stage directions where appropriate

Generate a complete, ready-to-use script."""

        # Call Groq API to generate the script
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert script writer who creates engaging, well-structured scripts for various purposes including videos, presentations, podcasts, and more. You write in a clear, compelling style that captures and maintains audience attention."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=2048,
        )
        
        script = chat_completion.choices[0].message.content
        
        return jsonify({
            'success': True,
            'script': script,
            'topic': topic,
            'script_type': script_type
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/summarize-idea', methods=['POST'])
def summarize_idea():
    """Summarize a topic idea in two lines max"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'error': 'Text is required'}), 400

        prompt = (
            "Summarize the idea below in at most two lines. "
            "Use plain text only, no bullets, no quotes.\n\n"
            f"Idea: {text}"
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You summarize ideas clearly and concisely."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=120,
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

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Moonify Script Generator'})

if __name__ == '__main__':
    print("🌙 Moonify Script Generator Starting...")
    print("📝 Visit http://localhost:5000 to use the script generator")
    app.run(debug=True, host='0.0.0.0', port=5000)
