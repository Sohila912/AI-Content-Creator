# White-Label Content Studio

A polished Flask + vanilla JS content research and script-generation demo.

## What changed

- White-label branding via `BRAND_NAME`
- Premium responsive dark UI with dynamic accent colors
- Topic discovery cards with "Use for script" flow
- Live Server-Sent Events script streaming
- Creative brief controls: format, tone, duration, platform, audience, language, CTA
- Copy and `.txt` export
- Automatic topic → script handoff
- Health/config endpoints
- Local JSON output retained
- `.gitignore` keeps virtual environments and generated data out of Git

## Setup

Create/activate your virtual environment, then:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add your API keys.

Run:

```bash
python run.py
```

The browser opens at:

`http://localhost:5000/ideas`

Script Studio:

`http://localhost:5000/script`
