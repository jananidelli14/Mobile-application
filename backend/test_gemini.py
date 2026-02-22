import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini():
    load_dotenv()
    key = os.getenv('GEMINI_API_KEY')
    print(f"API Key: {key[:5]}...{key[-5:]}" if key else "No Key found")
    
    if not key:
        return
        
    try:
        genai.configure(api_key=key)
        print("Available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        
        # Try a safe default
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, keeping safe?")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini()
