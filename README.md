# Kyungdong University Global Campus Chatbot

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-LLM-black.svg)](https://groq.com/)
[![Render](https://img.shields.io/badge/Render-Deploy-46E3B7.svg)](https://render.com/)

An AI assistant for Kyungdong University Global Campus that answers questions using the university's official website content. The app is built with Streamlit and Groq, and it includes voice input, text-to-speech, tool actions, admin analytics, feedback reporting, and Korean/English support.

## Overview

This project turns the official Kyungdong University Global website into a conversational assistant. Users can ask natural-language questions about admissions, scholarships, programs, housing, tuition, and student services, and the app returns answers grounded in the university's own published information.

The project is designed to be practical for students and maintainable for developers. It uses a lightweight retrieval pipeline, shows source links, supports user preferences, and includes moderation and analytics features for quality control.

## Features

- Official website-backed answers
- Source links and retrieval confidence
- Voice input and text-to-speech output
- Korean and English responses
- Tool actions for web search, calendar drafts, and email drafts
- Personalized chat settings for tone, detail level, and language
- Detailed feedback capture with admin reporting
- Analytics dashboard for conversation quality review
- Safety checks for harmful content and prompt injection

## Screenshots

Add screenshots to the files below to make the GitHub page more polished and easier to scan.

- `docs/screenshots/home.png`
- `docs/screenshots/voice-settings.png`
- `docs/screenshots/analytics.png`
- `docs/screenshots/admin-report.png`

Example:

```md
![Main chat interface](docs/screenshots/home.png)
![Voice settings](docs/screenshots/voice-settings.png)
![Analytics dashboard](docs/screenshots/analytics.png)
![Admin report](docs/screenshots/admin-report.png)
```

## Project Structure

```text
app.py
src/
	app.py
	chatbot_rag.py
	knowledge_base.py
docs/
	screenshots/
render.yaml
requirements.txt
```

## Requirements

- Python 3.12 recommended
- Groq API key
- Microphone access for voice input

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Required environment variable:

- `GROQ_API_KEY`

Optional environment variable:

- `ADMIN_PASSWORD`

Example `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_groq_api_key"
ADMIN_PASSWORD = "your_admin_password"
```

## Run Locally

```bash
streamlit run app.py
```

Windows PowerShell:

```powershell
$env:GROQ_API_KEY = "your_groq_api_key"
streamlit run app.py
```

## Deployment

The repository includes `render.yaml` for Render deployment.

Deployment settings:

- Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
- Python version: `3.12.4`
- Set `GROQ_API_KEY` in Render environment variables

## Usage

### Example questions

- Tell me about admissions for international students.
- What scholarships are available?
- What housing options does KDU Global offer?

### Voice input

1. Enable Voice Input in the sidebar.
2. Allow microphone permission in your browser.
3. Record a question and stop the recording.

### Tool actions

- `/search Kyungdong University Global admissions`
- `/calendar remind me to submit documents`
- `/email draft a question about scholarships`

### Korean examples

- `한국어로 입학 요건을 알려줘`
- `장학금 정보를 한국어로 설명해줘`

## Feedback and Admin

- Use the 👍 / 👎 buttons on answers.
- When you click 👎, select a reason and add a note.
- Review analytics from the dashboard in the sidebar.
- Use the Admin Profile panel to download the developer feedback report.

Admin access:

- Username: `admin`
- Password: value from `ADMIN_PASSWORD`

## Troubleshooting

- If the Groq key is missing, set `GROQ_API_KEY` in your environment or secrets file.
- If voice input does not work, check browser microphone permissions.
- If Korean transcription is weak, switch the language setting to Korean and speak clearly.
- If the website data seems stale, use the refresh button in the sidebar.

## License

No license file is included yet. Add one if you want to publish the project under explicit terms.