FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask flask-cors requests python-dotenv groq pymongo

CMD ["python", "Script_generation/Scripting_agent.py"]