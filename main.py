import sys
import argparse
import re
from src.extractor import extract_video_id, get_video_metadata, get_video_transcript
from src.summarizer import generate_summary

def main():
    # Setup argument parser for command line interface
    parser = argparse.ArgumentParser(description="YouTube Video Summarizer CLI")
    parser.add_argument("url", help="The full YouTube video URL to summarize")
    args = parser.parse_args()

    url = args.url
    
    print(f"\n🚀 Analyzing YouTube URL: {url}")
    
    try:
        # Step 1: Extract Video ID
        print("⏳ Extracting video ID...")
        video_id = extract_video_id(url)
        
        # Step 2: Get Video Metadata
        print("⏳ Fetching metadata (title, channel)...")
        metadata = get_video_metadata(url)
        print(f"🎬 Title: {metadata['title']}")
        print(f"👤 Channel: {metadata['channel']}")
        
        # Step 3: Download Transcript
        print("⏳ Downloading transcript...")
        transcript = get_video_transcript(video_id)
        # Count approximate words to show the user
        word_count = len(transcript.split())
        print(f"✅ Transcript downloaded ({word_count} words).")
        
        # Step 4: Generate AI Summary
        print("🧠 Generating summary using Gemini AI (this might take a moment)...")
        summary = generate_summary(transcript, metadata['title'], metadata['channel'])
        
        # Step 5: Display the formatted result
        print("\n" + "="*60)
        print("✨ VIDEO SUMMARY ✨")
        print("="*60)
        print(summary)
        print("="*60 + "\n")
        
        # Step 6: Save summary to a text file
        print("💾 Saving summary to file...")
        # Remove characters that are invalid in file names
        safe_title = re.sub(r'[\\/*?:"<>|]', "", metadata['title'])
        filename = f"{safe_title}.txt"
        
        # Write the metadata and summary to the file with UTF-8 encoding
        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"Title: {metadata['title']}\n")
            file.write(f"Channel: {metadata['channel']}\n")
            file.write("URL: " + url + "\n")
            file.write("="*60 + "\n\n")
            file.write(summary)
            
        print(f"✅ Summary successfully saved to: {filename}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()