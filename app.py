import html
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from src.extractor import extract_video_id, get_transcript_with_timestamps, get_video_metadata
from src.summarizer import generate_summary, chat_with_video, compare_videos

load_dotenv()

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #FF0000 0%, #B00000 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 6px 28px rgba(200, 0, 0, 0.22);
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    margin: 0 0 0.4rem 0;
}
.hero p {
    font-size: 1.05rem;
    opacity: 0.88;
    margin: 0;
}

/* Video metadata card */
.video-meta .v-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 0.2rem;
}
.video-meta .v-channel {
    font-size: 0.88rem;
    color: #6c757d;
}

/* Sidebar history item */
.hist-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #1a1a1a;
    line-height: 1.3;
    margin-bottom: 2px;
}
.hist-time {
    font-size: 0.75rem;
    color: #888;
    margin-bottom: 6px;
}

/* Primary button */
div[data-testid="stButton"] > button[kind="primary"] {
    background: #FF0000 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.65rem 1.5rem !important;
    transition: background 0.2s, transform 0.1s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #CC0000 !important;
    transform: translateY(-1px) !important;
}

/* Download button */
div[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    border: 2px solid #FF0000 !important;
    color: #FF0000 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: background 0.2s, color 0.2s !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: #FF0000 !important;
    color: white !important;
}
</style>
"""


def _truncate(text: str, max_len: int) -> str:
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def run_web_app():
    st.set_page_config(
        page_title="YouTube Summarizer",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    if "history" not in st.session_state:
        st.session_state.history = []
    if "current_summary" not in st.session_state:
        st.session_state.current_summary = None

    # ── Sidebar: history ──────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## History")
        if not st.session_state.history:
            st.info("No videos summarized yet.")
        else:
            for i, item in enumerate(reversed(st.session_state.history)):
                original_idx = len(st.session_state.history) - 1 - i
                st.image(item["thumbnail"], width="stretch")
                st.markdown(
                    f'<div class="hist-title">{html.escape(_truncate(item["title"], 52))}</div>'
                    f'<div class="hist-time">{html.escape(item["channel"])} · {html.escape(item["time"])}</div>',
                    unsafe_allow_html=True,
                )
                if st.button("View summary", key=f"hist_{original_idx}"):
                    st.session_state.current_summary = item
                st.divider()

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero">
            <h1>🎬 YouTube Summarizer</h1>
            <p>Paste any YouTube link — get an AI-powered summary with timestamps in seconds.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_summarize, tab_compare = st.tabs(["📄 Summarize", "⚖️ Compare Videos"])

    # ── Tab: Summarize ────────────────────────────────────────────────────────
    with tab_summarize:
        video_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
        )
        submitted = st.button("Generate Summary", type="primary", use_container_width=True)

        if submitted:
            if not video_url.strip():
                st.error("Please enter a YouTube URL before clicking Generate.")
            else:
                with st.status("Analyzing video…", expanded=True) as status:
                    try:
                        st.write("Extracting video ID…")
                        video_id = extract_video_id(video_url)

                        st.write("Fetching video metadata…")
                        metadata = get_video_metadata(video_id)

                        st.write("Downloading transcript…")
                        transcript = get_transcript_with_timestamps(video_id)

                        st.write("Generating AI summary with Gemini…")
                        summary = generate_summary(transcript)

                        entry = {
                            "video_id": video_id,
                            "url": video_url,
                            "summary": summary,
                            "transcript": transcript,
                            "chat": [],
                            "time": datetime.now().strftime("%H:%M"),
                            "title": metadata["title"],
                            "channel": metadata["channel"],
                            "thumbnail": metadata["thumbnail"],
                        }
                        st.session_state.history.append(entry)
                        st.session_state.current_summary = entry
                        status.update(label="Summary ready!", state="complete")

                    except Exception as error:
                        status.update(label="Something went wrong", state="error")
                        st.error(str(error))

        # ── Display current summary ───────────────────────────────────────────
        if st.session_state.current_summary:
            current = st.session_state.current_summary
            st.divider()

            col_thumb, col_info = st.columns([1, 3], gap="large")
            with col_thumb:
                st.image(current["thumbnail"], width="stretch")

            with col_info:
                st.markdown(
                    f'<div class="video-meta">'
                    f'<div class="v-title">{html.escape(current["title"])}</div>'
                    f'<div class="v-channel">by {html.escape(current["channel"])}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                st.write("")
                st.download_button(
                    label="Download Summary (.md)",
                    data=current["summary"],
                    file_name=f"summary_{current['video_id']}.md",
                    mime="text/markdown",
                )

            st.divider()

            with st.container(border=True):
                st.markdown(current["summary"])

            # ── Chat with this video ──────────────────────────────────────────
            st.divider()
            st.markdown("### 💬 Chat with this video")

            for msg in current.get("chat", []):
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if prompt := st.chat_input("Ask anything about this video…"):
                current["chat"].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking…"):
                        answer = chat_with_video(current["transcript"], current["chat"])
                    st.markdown(answer)
                current["chat"].append({"role": "assistant", "content": answer})

    # ── Tab: Compare Videos ───────────────────────────────────────────────────
    with tab_compare:
        st.markdown("Paste 2–5 YouTube URLs (one per line) to get a side-by-side AI analysis.")
        urls_input = st.text_area(
            "YouTube URLs",
            placeholder=(
                "https://www.youtube.com/watch?v=...\n"
                "https://www.youtube.com/watch?v=...\n"
                "https://www.youtube.com/watch?v=..."
            ),
            height=140,
            label_visibility="collapsed",
        )
        compare_btn = st.button("Compare Videos", type="primary", use_container_width=True)

        if compare_btn:
            urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
            if len(urls) < 2:
                st.error("Please enter at least 2 URLs to compare.")
            elif len(urls) > 5:
                st.error("Maximum 5 videos at a time.")
            else:
                with st.status(f"Analyzing {len(urls)} videos…", expanded=True) as status:
                    try:
                        videos = []
                        for i, url in enumerate(urls, 1):
                            st.write(f"Processing video {i}/{len(urls)}…")
                            vid_id = extract_video_id(url)
                            meta = get_video_metadata(vid_id)
                            transcript = get_transcript_with_timestamps(vid_id)
                            videos.append({
                                "title": meta["title"],
                                "channel": meta["channel"],
                                "thumbnail": meta["thumbnail"],
                                "transcript": transcript,
                            })

                        st.write("Generating comparative report with Gemini…")
                        report = compare_videos(videos)
                        st.session_state.comparison = {"videos": videos, "report": report}
                        status.update(label="Comparison ready!", state="complete")

                    except Exception as error:
                        status.update(label="Something went wrong", state="error")
                        st.error(str(error))

        if st.session_state.get("comparison"):
            comp = st.session_state.comparison
            st.divider()

            thumb_cols = st.columns(len(comp["videos"]))
            for col, v in zip(thumb_cols, comp["videos"]):
                with col:
                    st.image(v["thumbnail"], width="stretch")
                    st.caption(f"**{html.escape(v['title'])}**  \n{html.escape(v['channel'])}")

            st.divider()

            with st.container(border=True):
                st.markdown(comp["report"])

            st.download_button(
                label="Download Report (.md)",
                data=comp["report"],
                file_name="comparison_report.md",
                mime="text/markdown",
            )


if __name__ == "__main__":
    run_web_app()
