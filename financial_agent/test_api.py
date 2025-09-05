#!/usr/bin/env python3
import os
import openai

def test_openai_api():
    """Test if the OpenAI API is working"""
    try:
        # Check if API key is set
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY environment variable is not set")
            return False
        
        print(f"✅ API Key found: {api_key[:10]}...")
        
        # Test the API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': 'Say hello'}],
            max_tokens=10
        )
        
        print(f"✅ API working! Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    test_openai_api()
