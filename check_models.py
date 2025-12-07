import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: No API key found in .env file!")
    exit(1)

genai.configure(api_key=api_key)

print("=" * 60)
print("AVAILABLE GEMINI MODELS FOR YOUR API KEY:")
print("=" * 60)

available_models = []
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        model_name = m.name.replace('models/', '')
        available_models.append(model_name)
        print(f"  - {model_name}")

print("=" * 60)
print(f"Total models available: {len(available_models)}")
print("=" * 60)

# Suggest which ones to use
print("\nRECOMMENDED FOR STRATOS:")
flash_models = [m for m in available_models if 'flash' in m.lower()]
pro_models = [m for m in available_models if 'pro' in m.lower() and 'flash' not in m.lower()]

if flash_models:
    print(f"Primary (Fast): {flash_models[0]}")
if pro_models:
    print(f"Fallback (Powerful): {pro_models[0]}")
