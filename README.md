# YouTube Summarizer

An AI-powered tool that generates structured, timestamped summaries of any YouTube video — available as both a web app and a command-line tool.

Paste a link, get a clean summary broken into chapters with key takeaways, in the same language as the video.

---

## Features

- **Timestamped chapters** — each section is anchored to the exact moment in the video
- **Structured output** — Overview, Key Topics, and Key Takeaways sections
- **Multilingual** — summary language matches the video (Polish, English, and more)
- **Search history** — sidebar keeps track of all previously summarized videos with thumbnails
- **Downloadable** — export any summary as a Markdown file
- **CLI mode** — run headlessly from the terminal without the web UI

---

## Tech stack

| Layer | Technology |
|---|---|
| Web UI | [Streamlit](https://streamlit.io/) |
| AI model | Google Gemini 2.5 Flash via `google-genai` |
| Transcript | `youtube-transcript-api` |
| Metadata | YouTube oEmbed API (no API key required) |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/youtube-summarizer.git
cd youtube-summarizer
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

```bash
cp .env.example .env
```

Open `.env` and replace `your_gemini_api_key_here` with your actual key.  
Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## Usage

### Web app

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser, paste a YouTube URL, and click **Generate Summary**.

### Command-line

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

The summary is printed to stdout. Both standard (`?v=`) and short (`youtu.be/`) URLs are supported.

---

## Project structure

```
youtube-summarizer/
├── app.py              # Streamlit web application
├── main.py             # CLI entry point
├── src/
│   ├── __init__.py
│   ├── extractor.py    # Video ID parsing, metadata fetch, transcript download
│   └── summarizer.py   # Gemini API call and prompt
├── .env.example        # Template — copy to .env and add your API key
└── requirements.txt
```

---

## Requirements

- Python 3.10+
- A Google Gemini API key (free tier is sufficient for personal use)
- The video must have captions available (auto-generated or manual)
