# Kyungdong University Global Campus Chatbot

A Streamlit-based AI assistant for Kyungdong University Global Campus. It helps students, applicants, and staff get fast answers from the university's official website, while also supporting voice input, text-to-speech, tool actions, safety controls, admin feedback reporting, and long-term user preferences.

## About this project

This project turns the official Kyungdong University Global website into a conversational assistant. Users can ask natural-language questions about admissions, scholarships, programs, housing, and student services, and the app returns answers grounded in the university's own published information.

It is designed to be practical for students and maintainable for developers: the UI is simple, the knowledge source is official, and the app includes analytics, feedback capture, admin access, and deployment support.

## Project description

This project is designed to make official Kyungdong University information easier to access in one place. Instead of manually searching across multiple pages, users can ask questions in natural language and receive direct answers backed by the university's official website content.

The chatbot is especially useful for:

- New international students who need admissions or visa-related guidance
- Current students looking for campus life, housing, or student service information
- Applicants comparing programs, scholarships, and tuition details
- Developers or administrators who want analytics, feedback, and quality review tools

The app is built with Streamlit for the interface and Groq for language generation, and it pulls content directly from the official KDU Global website so answers stay grounded in the university's own information.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-LLM-black.svg)](https://groq.com/)
[![Render](https://img.shields.io/badge/Render-Deploy-46E3B7.svg)](https://render.com/)
[![License](https://img.shields.io/badge/License-Unlicensed-lightgrey.svg)]()

## What it does

- Answers admissions, program, scholarship, tuition, housing, and student service questions.
- Pulls knowledge from official KDU Global website pages.
- Shows source links and retrieval confidence.
- Supports voice input and text-to-speech output.
- Includes safe tool actions for web search, calendar drafts, and email drafts.
- Stores per-user preferences such as tone, language, and voice settings.
- Tracks feedback and analytics so developers can review quality over time.
- Supports Korean and English responses.

## Key features

### Official website-backed answers

- Uses official KDU Global pages as the main knowledge source.
- Caches parsed website content locally for faster startup.
- Lets you refresh the official data from the sidebar.

### Better chat experience

- Tone controls: Friendly, Professional, Conversational
- Detail controls: Concise, Balanced, Detailed
- Language controls: English, Korean, Auto
- Follow-up question suggestions
- Chat export to JSON

### Voice and audio

- Microphone recording in the browser
- Speech-to-text transcription
- Text-to-speech playback for answers
- Korean-aware voice handling

### Tool actions

- Web search via `/search ...`
- Calendar drafts via `/calendar ...`
- Email drafts via `/email ...`

### Safety and moderation

- Prompt-injection and jailbreak resistance
- Harmful request blocking
- Honest unknown responses when the official data does not cover a question

### Developer and admin support

- Detailed feedback capture with reasons and notes
- Analytics dashboard for unknown rate, moderation rate, topics, and tool usage
- Admin login protected by password
- Exportable developer feedback report

## Screenshots

Add real screenshots here to make the GitHub page more convincing and easier to scan.

Recommended screenshots:

- Main chat interface
- Sidebar profile settings
- Voice input and text-to-speech controls
- Analytics dashboard
- Admin feedback report download

Suggested file names:

- `docs/screenshots/home.png`
- `docs/screenshots/voice-settings.png`
- `docs/screenshots/analytics.png`
- `docs/screenshots/admin-report.png`

Example markdown once the images are added:

```md
![Main chat interface](docs/screenshots/home.png)
![Voice settings](docs/screenshots/voice-settings.png)
![Analytics dashboard](docs/screenshots/analytics.png)
![Admin report](docs/screenshots/admin-report.png)
```

## Project structure

```text
app.py
src/
	app.py
	chatbot_rag.py
	knowledge_base.py
render.yaml
requirements.txt
```

## Requirements

- Python 3.12 is recommended for local development.
- A Groq API key is required.
- Microphone access is required for voice input.

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### Required environment variables

- `GROQ_API_KEY` - Groq API key used for chat and transcription.

### Optional environment variables

- `ADMIN_PASSWORD` - Enables the admin profile panel.

### Local secrets file

For local development, you can use `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_groq_api_key"
ADMIN_PASSWORD = "your_admin_password"
```

## Run locally

```bash
streamlit run app.py
```

If you use Windows PowerShell:

```powershell
$env:GROQ_API_KEY = "your_groq_api_key"
streamlit run app.py
```

## Deploy on Render

This repository includes `render.yaml` for Render deployment.

Important settings:

- Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
- Python version: `3.12.4`
- Set `GROQ_API_KEY` in the Render environment variables

## How to use

### Ask normal questions

- Tell me about admissions for international students.
- What scholarships are available?
- What housing options does KDU Global offer?

### Try voice input

1. Enable Voice Input in the sidebar.
2. Allow microphone permission in the browser.
3. Record a question and stop the recording.

### Try tool actions

- `/search Kyungdong University Global admissions`
- `/calendar remind me to submit documents`
- `/email draft a question about scholarships`

### Try Korean

- `한국어로 입학 요건을 알려줘`
- `장학금 정보를 한국어로 설명해줘`

## Feedback workflow

- Use the 👍 / 👎 buttons on assistant responses.
- If you click 👎, select a reason and add a note.
- Open the Analytics Dashboard to review totals, unknown rate, moderation rate, and topic trends.
- Use the Admin Profile panel to download the developer feedback report.

## Notes for administrators

- Admin login uses the username `admin` and the password from `ADMIN_PASSWORD`.
- If `ADMIN_PASSWORD` is not set, the admin panel stays disabled.

## Troubleshooting

- If the chatbot says the Groq key is missing, set `GROQ_API_KEY` in your environment or secrets file.
- If voice input does not work, check browser microphone permissions.
- If Korean audio transcription seems weak, select Korean in the response language control and speak clearly.
- If official data looks stale, use the sidebar refresh button to reload website content.

## License

No license file is included yet. Add one if you want the project to be public and reusable under explicit terms.