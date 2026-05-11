import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load environment variables (e.g., GOOGLE_API_KEY) from the .env file
load_dotenv()

def generate_summary(transcript: str, title: str, channel: str) -> str:
    """
    Generates a concise summary of the video transcript using Gemini.
    """
    # Verify if the API key is present
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Google API Key not found. Please check your .env file.")

    # Using the current standard free-tier model (gemini-2.5-flash)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    
    # Define the instruction structure for the AI
    prompt_template = """
    You are an expert content summarizer. Your task is to summarize the following YouTube video.
    
    Video Title: {title}
    Channel: {channel}
    
    Transcript:
    {transcript}
    
    Please provide a structured, easy-to-read summary.
    IMPORTANT: Detect the primary language of the transcript and write the entire summary in THAT EXACT SAME language. 
    (For example: if the transcript is in Polish, write the summary in Polish. If it's in English, write in English).
    
    Include:
    1. A concise overview of the main topic.
    2. Key takeaways or main points (use bullet points).
    3. A short conclusion.
    
    Summary:
    """
    
    # Create the prompt using LangChain's core PromptTemplate
    prompt = PromptTemplate(
        input_variables=["title", "channel", "transcript"],
        template=prompt_template
    )
    
    # Create the execution chain
    chain = prompt | llm
    
    try:
        # Run the model with our variables
        response = chain.invoke({
            "title": title,
            "channel": channel,
            "transcript": transcript
        })
        return response.content
    except Exception as e:
        raise RuntimeError(f"Failed to generate summary: {str(e)}")