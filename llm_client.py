import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiAdapter:
    """
    Adapts OpenAI response to look like Gemini response.
    Has a .text property.
    """
    def __init__(self, content):
        self.text = content

class GeminiStreamAdapter:
    """
    Adapts OpenAI stream chunk to look like Gemini stream chunk.
    """
    def __init__(self, content):
        self.text = content

def get_api_key():
    """
    Retrieves API key from Streamlit secrets or environment variables.
    Checks for OPENROUTER_API_KEY first, then GOOGLE_API_KEY (as fallback/legacy).
    """
    # Try Streamlit Secrets first
    try:
        if "OPENROUTER_API_KEY" in st.secrets:
            return st.secrets["OPENROUTER_API_KEY"]
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except:
        pass
    
    # Try Environment Variables
    if os.getenv("OPENROUTER_API_KEY"):
        return os.getenv("OPENROUTER_API_KEY")
    if os.getenv("GOOGLE_API_KEY"):
        return os.getenv("GOOGLE_API_KEY")
        
    return None

def generate(prompt, system_instruction=None, model=None, stream=False, temperature=0.7, api_key=None):
    """
    Generates content using OpenRouter (Llama 3 via Groq/others).
    
    Args:
        prompt (str): The user prompt.
        system_instruction (str): System prompt/role.
        model (str): Model ID. Defaults to Llama 3.1 70B.
        stream (bool): Whether to stream the response.
        temperature (float): Creativity.
        api_key (str): Optional API key override.
        
    Returns:
        GeminiAdapter object (if not stream) or Generator of GeminiStreamAdapter (if stream).
    """
    if not api_key:
        api_key = get_api_key()
    
    if not api_key:
        raise ValueError("Missing API Key. Please set OPENROUTER_API_KEY.")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    # Default models
    # Primary: Llama 3.1 70B (High Intelligence)
    # Fallback/Fast: Llama 3.1 8B
    if not model:
        model = "meta-llama/llama-3.1-70b-instruct"
        
    # Map legacy Gemini model names to OpenRouter equivalents if passed
    model_map = {
        "gemini-2.5-flash": "meta-llama/llama-3.1-8b-instruct", # Fast
        "gemini-2.0-flash": "meta-llama/llama-3.1-8b-instruct", # Fast
        "gemini-2.5-pro": "meta-llama/llama-3.1-70b-instruct",  # Smart
        "gemini-1.5-pro": "meta-llama/llama-3.1-70b-instruct",
        "gemini-1.5-flash": "meta-llama/llama-3.1-8b-instruct",
    }
    
    if model in model_map:
        model = model_map[model]

    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=stream,
            extra_headers={
                "HTTP-Referer": "https://stratos-app.com", # Optional, for OpenRouter rankings
                "X-Title": "Stratos AI",
            }
        )
        
        if stream:
            def stream_generator():
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield GeminiStreamAdapter(content)
            return stream_generator()
        else:
            content = response.choices[0].message.content
            return GeminiAdapter(content)
            
    except Exception as e:
        print(f"OpenRouter Error: {e}")
        raise e
