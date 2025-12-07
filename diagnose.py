import os
from dotenv import load_dotenv
import google.generativeai as genai

def main():
    print("--- Diagnostic Tool ---")
    
    # 1. Check .env
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        return
    
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in .env")
        return
        
    print(f"✅ API Key found: {api_key[:4]}...{api_key[-4:]}")
    
    # 2. Configure
    try:
        genai.configure(api_key=api_key)
        print("✅ Configured Gemini API")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return

    # 3. List Models
    print("\n--- Available Models ---")
    try:
        count = 0
        for m in genai.list_models():
            count += 1
            print(f"Model: {m.name}")
            print(f"  Methods: {m.supported_generation_methods}")
            
        if count == 0:
            print("⚠️ No models found. Your API key might not have access to any models, or is invalid.")
        else:
            print(f"\n✅ Found {count} models.")
            
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        print("\nPossible causes:")
        print("1. API Key is invalid.")
        print("2. API Key does not have 'Generative Language API' enabled in Google Cloud Console.")
        print("3. You are in a region where Gemini is not available.")

if __name__ == "__main__":
    main()
