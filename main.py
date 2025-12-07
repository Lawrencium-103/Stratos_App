print("DEBUG: Script starting...")
import sys
try:
    import os
    from dotenv import load_dotenv
    import google.generativeai as genai
    print("DEBUG: Imports successful.")
except ImportError as e:
    print(f"CRITICAL ERROR: Missing dependencies. {e}")
    print("Please run: pip install -r requirements.txt")
    input("Press Enter to exit...")
    sys.exit(1)
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

# Load environment variables
load_dotenv()

def load_prompt(filepath):
    """Loads the system prompt from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {filepath}")
        # sys.exit(1) # Don't exit, just return empty to keep debug alive
        return ""

def main():
    print("🚀 Content Agent 'Viral Engine' Initializing...")
    
    # Check for API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key.")
        return

    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Load System Prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "master_system_prompt.txt")
    system_instruction = load_prompt(prompt_path)
    
    # Get User Input
    print("\n--- Content Source ---")
    print("1. Topic (Auto-Research)")
    print("2. URL (Analyze specific link)")
    print("3. Content Strategy (Roadmap Generator) [NEW]")
    
    choice = input("Select (1/2/3): ").strip()
    
    topic = ""
    scraped_data = ""
    keywords = ""
    sources = []
    
    if choice == "3":
        import strategist
        niche = input("Enter Niche/Industry: ").strip()
        user_url = input("Enter Your Website URL (Optional, press Enter to skip): ").strip()
        comp_url = input("Enter Competitor URL (Optional, press Enter to auto-find): ").strip()
        
        manual_competitors = [comp_url] if comp_url else []
        
        # Run Strategist
        roadmap = strategist.generate_roadmap(niche, user_url, manual_competitors, api_key)
        
        # Save Roadmap
        with open("content_roadmap.md", "w", encoding="utf-8") as f:
            f.write(roadmap)
        print(f"\n\n✅ Roadmap saved to content_roadmap.md")
        return # Exit after roadmap generation

    elif choice == "2":
        url = input("Enter URL: ").strip()
        if not url:
            print("Error: URL is required.")
            return
        topic = "Analysis of " + url # Placeholder topic for the prompt
        import researcher
        scraped_data, keywords, sources = researcher.process_url(url, api_key)
    else:
        topic = input("Enter TOPIC: ").strip()
        if not topic:
            print("Error: Topic is required.")
            return
        import researcher
        scraped_data, keywords, sources = researcher.research_topic(topic, api_key)
    
    print(f"\n--- Research Results ---")
    print(f"Context Length: {len(scraped_data)} chars")
    print(f"Keywords: {keywords}\n")
    print(f"Sources Found: {len(sources)}")

    # Prepare the model
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 65536,
        "response_mime_type": "text/plain",
    }
    
    # Candidate models
    candidate_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-latest",
        "gemini-pro"
    ]

    print(f"\nAttempting to connect to Gemini...")
    
    # Prepare the user message part
    user_message = f"""
TOPIC: {topic}
SCRAPED CONTEXT (Facts/News): {scraped_data}
SEO KEYWORDS: {keywords}

IMPORTANT INSTRUCTION FOR "AEO Answer Card":
You MUST follow the strict format:
1. Start with a Direct Definition (No Intro).
2. Use Question Headers.
3. End with an FAQ Section.
If you fail this structure, the content is useless.
"""

    print("\nGenerating content... This may take a moment.")
    
    success = False
    last_error = None

    for model_name in candidate_models:
        try:
            print(f"Using model: {model_name}")
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=system_instruction
            )
            chat_session = model.start_chat(history=[])
            
            print("  ⏳ Waiting for response stream...")
            response_stream = chat_session.send_message(user_message, stream=True)
            
            print("\n" + "="*30)
            print("       GENERATED CONTENT       ")
            print("="*30 + "\n")
            
            full_text = ""
            for chunk in response_stream:
                print(chunk.text, end="", flush=True)
                full_text += chunk.text
            
            # Format References
            references_md = "\n\n## References\n"
            for s in sources:
                references_md += f"- [{s.get('title', 'Source')}]({s['href']})\n"
            
            final_output = full_text + references_md
            print(references_md)
            
            # Save to file
            output_filename = "generated_content.md"
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(final_output)
            print(f"\n\n✅ Content saved to {output_filename}")
            success = True
            break
        except Exception as e:
            print(f"Failed with {model_name}: {e}")
            last_error = e
            if "404" in str(e) or "not found" in str(e).lower():
                continue
            else:
                break
    
    if not success:
        print("\nAll model attempts failed.")
        print(f"Last error: {last_error}")

if __name__ == "__main__":
    main()
