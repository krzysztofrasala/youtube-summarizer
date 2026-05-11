import streamlit as st
from src.extractor import extract_video_id, get_video_metadata, get_video_transcript
from src.summarizer import generate_summary

# Page configuration
st.set_page_config(page_title="AI YouTube Summarizer", page_icon="🎬", layout="wide")

st.title("🎬 AI YouTube Summarizer")

# Input section
url = st.text_input("YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Generate Summary 🚀"):
    if not url:
        st.warning("Please provide a valid URL!")
    else:
        try:
            with st.spinner("Processing..."):
                video_id = extract_video_id(url)
                metadata = get_video_metadata(url)
                
                # Layout: Two columns for metadata and thumbnail
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if metadata.get('thumbnail'):
                        st.image(metadata['thumbnail'], use_container_width=True)
                
                with col2:
                    st.subheader(metadata['title'])
                    st.write(f"**Channel:** {metadata['channel']}")
                    st.write(f"**Video ID:** {video_id}")

                # AI Processing
                transcript = get_video_transcript(video_id)
                summary = generate_summary(transcript, metadata['title'], metadata['channel'])
                
                st.success("Summary generated!")
                st.markdown("### ✨ Summary")
                st.info(summary)
                
                # Export functionality
                export_data = f"Title: {metadata['title']}\nChannel: {metadata['channel']}\nURL: {url}\n\n{summary}"
                st.download_button(
                    label="📥 Download Summary",
                    data=export_data,
                    file_name=f"summary_{video_id}.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"An error occurred: {e}")