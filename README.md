# 🌙 AI Content Creator

**AI Content Creator** is an intelligent content creation platform that helps you discover trending topics and generate professional scripts powered by advanced AI—all in one streamlined workflow.

## ✨ Features

### 📝 Script Generation
- **AI-Powered Script Writing**: Generate professional scripts using Groq's LLaMA 3.3 70B model
- **Multiple Script Types**: Video scripts, podcasts, presentations, YouTube videos, explainer videos, and more
- **Customizable Parameters**: Choose duration, tone, and style
- **Copy-Ready Output**: Instantly copy generated scripts to your clipboard

### 💡 Idea Explorer
- **Trending Topic Search**: Discover hot topics using Tavily's real-time web search
- **Custom Date Ranges**: Search topics from specific time periods (24 hours, week, month, year, or custom)
- **AI Summarization**: Automatically summarize topics into concise, script-ready descriptions
- **One-Click Integration**: Seamlessly transfer ideas to the script generator with automatic topic prefill

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/AI-Content-Creator.git
   cd AI-Content-Creator
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   # or
   source venv/bin/activate      # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   cd Script_generation
   pip install -r requirements.txt
   ```

### API Keys Configuration

You'll need to configure the following API keys in `Script_generation/Scripting_agent.py`:

- **Groq API**: For AI-powered script generation and topic summarization
  - Get your free API key at: [https://console.groq.com](https://console.groq.com)
  - Add to the .env file: `Groq_API_KEY="your-groq-api-key-here"`

- **Tavily API**: For real-time trending topic search
  - Get your free API key at: [https://tavily.com](https://tavily.com)
  - Add to the .env file: `TAvily_API_KEY="your-groq-api-key-here"`

## 📖 Usage

### Running the Application

1. **Start the Flask server**
   ```bash
   cd Script_generation
   python Scripting_agent.py
   ```
   The server will start on `http://localhost:5000`

2. **Access the application**
   - **Idea Explorer**: `http://localhost:5000/` or `http://localhost:5000/ideas`
   - **Script Generator**: `http://localhost:5000/script`

### Workflow

**Step 1: Find Trending Ideas**
- Navigate to the Idea Explorer homepage
- Enter what you want to find ideas for (e.g., "AI technology", "fitness trends")
- Optionally select a custom date range to search within
- Browse trending topics and click "Use idea" on any topic you like

**Step 2: Generate Your Script**
- The selected topic is automatically summarized and transferred to the Script Generator
- Review and edit the prefilled topic if needed
- Choose your script type (Video Script, Podcast, YouTube Video, etc.)
- Select duration and tone
- Click "Generate Script" and watch the AI create your content
- Copy the script to your clipboard with one click

## 🛠️ Tech Stack

- **Backend**: Flask 3.0.0, Python
- **AI Models**: 
  - Groq (LLaMA 3.3 70B Versatile) - Script generation & summarization
  - Tavily Search API - Real-time web search
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Architecture**: RESTful API with Flask-CORS

## 📁 Project Structure

```
AI-Content-Creator/
├── Script_generation/
│   ├── Scripting_agent.py      # Flask backend with all endpoints
│   ├── ideas.html              # Trending topic search interface
│   ├── index.html              # Script generator interface
│   └── requirements.txt        # Python dependencies
│
├── venv/                       # Virtual environment (not in git)
└── README.md                   # Project documentation
```

## 🔌 API Endpoints

The Flask backend provides the following endpoints:

- `GET /` - Serve idea explorer page
- `GET /script` - Serve script generator page
- `GET /ideas` - Serve idea explorer page (alias)
- `POST /search-topics` - Search trending topics via Tavily
- `POST /generate-script` - Generate script via Groq
- `POST /summarize-idea` - Summarize topic into 2 lines
- `GET /health` - Health check endpoint

## 🎯 Features in Detail

### Script Generation
- **Smart Prompting**: Automatically enhances user input for optimal AI results
- **Real-time Generation**: See your script created in seconds
- **Professional Formatting**: Includes hooks, structure, transitions, and stage directions
- **Flexible Output**: Supports multiple tones from professional to humorous
- **Multiple Formats**: Video scripts, podcasts, presentations, explainer videos, educational content, and more
- **Duration Control**: Generate scripts for specific time lengths (30s to 30min+)

### Idea Explorer
- **Advanced Search**: Powered by Tavily's deep web crawling technology
- **Time-Based Filtering**: Find topics from the last 24 hours, week, month, year, or custom date ranges
- **AI Summarization**: Uses Groq to condense complex topics into clear 2-line summaries
- **Direct Integration**: Click "Use idea" to automatically populate the script generator
- **Clean Interface**: Single-line topic display with smooth animations
- **Real-time Results**: Get up-to-date trending topics instantly

## 🔧 Configuration

### Port Configuration
Default port: `localhost:5000`

To change the port, edit `Scripting_agent.py`:
```python
app.run(debug=True, host='0.0.0.0', port=YOUR_PORT)
```

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Groq** for providing lightning-fast LLM inference with LLaMA 3.3 70B
- **Tavily** for real-time web search capabilities
- **Flask** community for the excellent web framework

## 💡 Use Cases

- **Content Creators**: Find trending topics and generate video scripts
- **YouTubers**: Research what's hot and create engaging content faster
- **Podcasters**: Discover discussion topics and structure episodes
- **Marketers**: Stay on top of trends and create timely content
- **Educators**: Find relevant topics and create educational materials


---
