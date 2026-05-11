import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load environment variables (e.g., GOOGLE_API_KEY) from the .env file
load_dotenv()

def generate_summary(transcript: str, title: str, channel: str, style: str = "Detailed") -> str:
    """
    Generates a summary of the video transcript using Gemini.
    'style' can be 'Short' or 'Detailed'.
    """
    # Verify if the API key is present
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Google API Key not found. Please check your .env file.")

    # Initialize the model
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    
    # Adjust the prompt based on selected style
    if style == "Short":
        detail_instruction = "Provide a very brief 3-4 sentence summary focusing only on the main idea."
    else:
        detail_instruction = """
        Provide a structured, easy-to-read summary. 
        Include:
        1. A concise overview of the main topic.
        2. Key takeaways or main points (use bullet points).
        3. A short conclusion.
        """

    # Define the instruction structure for the AI
    prompt_template = f"""
    You are an expert content summarizer. Your task is to summarize the following YouTube video.
    
    Video Title: {{title}}
    Channel: {{channel}}
    
    Transcript:
    {{transcript}}
    
    {detail_instruction}
    
    IMPORTANT: Detect the primary language of the transcript and write the entire summary in THAT EXACT SAME language.
    
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