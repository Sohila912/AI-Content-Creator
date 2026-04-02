@echo off
echo Activating virtual environment...
call c:\Users\Shrouk\Desktop\AI-Content-Creator\venv\Scripts\activate.bat

echo Starting Docker services...
docker-compose up -d

echo Waiting for MongoDB to be healthy...
timeout /t 20 /nobreak > nul

echo Starting ChromaDB server...
start "" c:\Users\Shrouk\Desktop\AI-Content-Creator\venv\Scripts\chroma.exe run --path ./data/chroma --host 0.0.0.0 --port 8000

echo Waiting for ChromaDB to start...
timeout /t 10 /nobreak > nul

echo Starting Moonify web app on port 5000...
start "" python Script_generation/Scripting_agent.py

echo Starting Vector Search web app on port 5001...
start "" python Script_generation/search_app.py

echo Running vectorize_topics.py...
python vectorize_topics.py

echo All services started and vectorization complete.
pause