from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import os
import requests
import json
from urllib.parse import urlparse
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime, UTC

load_dotenv()

app = Flask(__name__)
CORS(app)

# -------------------------
# White-label configuration
# -------------------------
BRAND_NAME = os.getenv("BRAND_NAME", "Content Studio")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

SCRIPT_MODEL = os.getenv("SCRIPT_MODEL", "openai/gpt-oss-120b")
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "openai/gpt-oss-20b")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
TAVILY_API_URL = "https://api.tavily.com/search"

TOPIC_FOLDER = "data/topics"
SCRIPT_FOLDER = "data/scripts"
os.makedirs(TOPIC_FOLDER, exist_ok=True)
os.makedirs(SCRIPT_FOLDER, exist_ok=True)


def get_domain(url):
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def get_next_filename(folder, prefix):
    existing = [f for f in os.listdir(folder) if f.startswith(prefix)]
    if not existing:
        return f"{prefix}_001.json"

    numbers = []
    for f in existing:
        try:
            numbers.append(int(f.split("_")[-1].split(".")[0]))
        except Exception:
            pass

    next_num = max(numbers) + 1 if numbers else 1
    return f"{prefix}_{str(next_num).zfill(3)}.json"


def save_json(folder, prefix, data):
    filename = get_next_filename(folder, prefix)
    filepath = os.path.join(folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return filepath


def require_client():
    if not client:
        raise RuntimeError("GROQ_API_KEY is not configured.")


@app.route("/")
def index():
    return send_from_directory(".", "ideas.html")


@app.route("/script")
def script_page():
    return send_from_directory(".", "index.html")


@app.route("/ideas")
def ideas_page():
    return send_from_directory(".", "ideas.html")

@app.route("/style.css")
def stylesheet():
    return send_from_directory(".", "style.css")


@app.route("/app.js")
def javascript():
    return send_from_directory(".", "app.js")


# -------------------------
# Topic Discovery
# -------------------------
@app.route("/search-topics", methods=["POST"])
def search_topics():
    try:
        data = request.get_json() or {}
        idea_query = data.get("query", "").strip()
        time_range = data.get("time_range", "week")
        start_date = data.get("start_date", "").strip()
        end_date = data.get("end_date", "").strip()
        max_results = max(1, min(int(data.get("max_results", 8)), 20))

        if not idea_query:
            return jsonify({"success": False, "error": "Query is required"}), 400
        if not TAVILY_API_KEY:
            return jsonify({"success": False, "error": "TAVILY_API_KEY is not configured."}), 500

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
                "success": False,
                "error": f"Tavily API Error {response.status_code}: {response.text}"
            }), response.status_code

        result = response.json()
        results = result.get("results", [])
        topics = []

        for i, item in enumerate(results):
            title = item.get("title", "Untitled")
            snippet = item.get("content", "") or item.get("snippet", "")
            url = item.get("url", "")

            topics.append({
                "topic_id": f"topic_{i+1:03}",
                "title": title,
                "description": snippet[:280],
                "url": url,
                "headline": title,
                "summary": snippet[:280],
                "source_url": url,
                "source_domain": get_domain(url),
                "keywords": idea_query.split(),
                "published_date": item.get("published_date", ""),
                "relevance_score": item.get("score"),
            })

        topics_json = {
            "generated_at": datetime.now(UTC).isoformat(),
            "query": idea_query,
            "time_range": time_range,
            "topics_count": len(topics),
            "topics": topics,
        }

        file_path = save_json(TOPIC_FOLDER, "topics_metadata", topics_json)

        return jsonify({
            "success": True,
            "topics": topics,
            "saved_to": file_path,
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------
# Script Generation
# -------------------------
def build_script_prompt(data):
    topic = data.get("topic", "").strip()
    script_type = data.get("script_type", "Explainer")
    duration = data.get("duration", "2–3 minutes")
    tone = data.get("tone", "Professional")
    platform = data.get("platform", "YouTube")
    audience = data.get("audience", "General audience")
    language = data.get("language", "English")
    cta = data.get("cta", "End with a natural call to action.")
    style = data.get("style", "Clear, cinematic, conversational")

    return f"""
You are an elite commercial content creator working inside a private white-label content studio.

Create a polished, production-ready {script_type} script about:
{topic}

Creative brief:
- Duration: {duration}
- Tone: {tone}
- Platform: {platform}
- Target audience: {audience}
- Language: {language}
- Style: {style}
- CTA: {cta}

Structure:
1. Start with a powerful hook.
2. Build curiosity quickly.
3. Deliver useful, specific main content.
4. Use natural voice-over language.
5. Include short visual direction cues in [brackets] only when useful.
6. Finish with a memorable conclusion and CTA.

Do not mention any AI company, model, internal tool, or brand name.
Return only the final script.
""".strip()


def generate_script_payload(data):
    require_client()
    prompt = build_script_prompt(data)

    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert commercial script writer."},
            {"role": "user", "content": prompt},
        ],
        model=SCRIPT_MODEL,
        temperature=0.7,
        max_tokens=3000,
    )
    return completion.choices[0].message.content.strip()


@app.route("/generate-script", methods=["POST"])
def generate_script():
    try:
        data = request.get_json() or {}
        topic = data.get("topic", "").strip()
        if not topic:
            return jsonify({"success": False, "error": "Topic is required"}), 400

        script = generate_script_payload(data)
        script_data = {
            "generated_at": datetime.now(UTC).isoformat(),
            "brand": BRAND_NAME,
            "script": {
                "topic": topic,
                "script_type": data.get("script_type", "Explainer"),
                "duration_target": data.get("duration", "2–3 minutes"),
                "tone": data.get("tone", "Professional"),
                "target_platform": data.get("platform", "YouTube"),
                "language": data.get("language", "English"),
                "estimated_word_count": len(script.split()),
                "model_used": SCRIPT_MODEL,
                "script_text": script,
            },
        }

        file_path = save_json(SCRIPT_FOLDER, "script_output", script_data)

        return jsonify({
            "success": True,
            "script": script,
            "topic": topic,
            "saved_to": file_path,
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/generate-script-stream", methods=["POST"])
def generate_script_stream():
    """Server-Sent Events endpoint for live script generation."""
    try:
        data = request.get_json() or {}
        topic = data.get("topic", "").strip()
        if not topic:
            return jsonify({"success": False, "error": "Topic is required"}), 400

        require_client()
        prompt = build_script_prompt(data)

        def event_stream():
            chunks = []
            try:
                stream = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are an expert commercial script writer."},
                        {"role": "user", "content": prompt},
                    ],
                    model=SCRIPT_MODEL,
                    temperature=0.7,
                    max_tokens=3000,
                    stream=True,
                )

                for chunk in stream:
                    text = ""
                    if chunk.choices and chunk.choices[0].delta:
                        text = chunk.choices[0].delta.content or ""
                    if text:
                        chunks.append(text)
                        yield f"data: {json.dumps({'type': 'chunk', 'text': text})}\n\n"

                script = "".join(chunks).strip()
                script_data = {
                    "generated_at": datetime.now(UTC).isoformat(),
                    "brand": BRAND_NAME,
                    "script": {
                        "topic": topic,
                        "script_type": data.get("script_type", "Explainer"),
                        "duration_target": data.get("duration", "2–3 minutes"),
                        "tone": data.get("tone", "Professional"),
                        "target_platform": data.get("platform", "YouTube"),
                        "language": data.get("language", "English"),
                        "estimated_word_count": len(script.split()),
                        "model_used": SCRIPT_MODEL,
                        "script_text": script,
                    },
                }
                file_path = save_json(SCRIPT_FOLDER, "script_output", script_data)

                yield f"data: {json.dumps({'type': 'done', 'word_count': len(script.split()), 'saved_to': file_path})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return Response(
            stream_with_context(event_stream()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------
# Idea Summarizer
# -------------------------
@app.route("/summarize-idea", methods=["POST"])
def summarize_idea():
    try:
        data = request.get_json() or {}
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"success": False, "error": "Text is required"}), 400

        require_client()
        prompt = f"""
Summarize the following content idea in 1–2 complete sentences.
Do not introduce information that is not in the idea.
Return ONLY the summary.

Idea:
{text}
""".strip()

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You summarize ideas clearly and concisely."},
                {"role": "user", "content": prompt},
            ],
            model=SUMMARY_MODEL,
            temperature=0.2,
            max_tokens=200,
        )

        return jsonify({
            "success": True,
            "summary": completion.choices[0].message.content.strip(),
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": BRAND_NAME,
        "streaming": True,
    })


@app.route("/config")
def config():
    # Deliberately exposes no secrets.
    return jsonify({
        "brand_name": BRAND_NAME,
        "default_model": SCRIPT_MODEL,
    })


if __name__ == "__main__":
    print(f"✨ {BRAND_NAME} starting...")
    print("🌐 http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
