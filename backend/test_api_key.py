#!/usr/bin/env python3
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_api():
    """Test the OpenAI API key directly"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No API key found in .env file")
        return
    
    print(f"🔑 API Key found: {api_key[:20]}...")
    
    try:
        # Initialize client
        client = OpenAI(api_key=api_key)
        
        # Test with a simple request
        print("🧪 Testing API key...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello, API test successful!'"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Test Successful!")
        print(f"📝 Response: {result}")
        
    except Exception as e:
        print(f"❌ API Test Failed: {e}")
        
        # Check for specific error types
        error_str = str(e)
        if "quota" in error_str.lower() or "insufficient" in error_str.lower():
            print("\n💡 This appears to be a quota/billing issue.")
            print("   Check your OpenAI account billing and usage limits.")
        elif "invalid" in error_str.lower() or "authentication" in error_str.lower():
            print("\n💡 This appears to be an authentication issue.")
            print("   Verify your API key is correct and active.")
        elif "rate" in error_str.lower():
            print("\n💡 This appears to be a rate limiting issue.")
            print("   Try again in a few minutes.")

if __name__ == "__main__":
    test_openai_api() 