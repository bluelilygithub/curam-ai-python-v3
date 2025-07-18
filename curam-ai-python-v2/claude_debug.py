#!/usr/bin/env python3
"""
Claude API Debug Script
Direct test of Claude API integration to identify issues
"""

import os
import sys
import json
from datetime import datetime

def test_claude_api():
    """Test Claude API with minimal setup"""
    print("🔍 Claude API Debug Test")
    print("=" * 50)
    
    # Check API key
    claude_key = os.getenv('CLAUDE_API_KEY')
    if not claude_key:
        print("❌ CLAUDE_API_KEY environment variable not found")
        return False
    
    print(f"✅ API Key found: {claude_key[:8]}...{claude_key[-4:]}")
    
    # Test anthropic import
    try:
        import anthropic
        print("✅ anthropic library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import anthropic: {e}")
        print("💡 Run: pip install anthropic")
        return False
    
    # Initialize client
    try:
        client = anthropic.Anthropic(api_key=claude_key.strip())
        print("✅ Claude client initialized")
    except Exception as e:
        print(f"❌ Claude client initialization failed: {e}")
        return False
    
    # Test models from your working JS app
    working_models = [
        "claude-3-5-sonnet-20241022",  # Latest from your JS
        "claude-3-5-sonnet-20240620",  # Alternative
        "claude-3-haiku-20240307",     # Haiku from your JS
        "claude-3-sonnet-20240229"     # Fallback
    ]
    
    print(f"\n🧪 Testing {len(working_models)} Claude models...")
    
    successful_models = []
    failed_models = []
    
    for model_name in working_models:
        print(f"\n🤖 Testing model: {model_name}")
        
        try:
            # Use the exact same test prompt as your JS app
            response = client.messages.create(
                model=model_name,
                max_tokens=100,
                messages=[{"role": "user", "content": "Hello, can you explain what you are and what you can do?"}]
            )
            
            response_text = response.content[0].text
            print(f"✅ SUCCESS: {model_name}")
            print(f"📝 Response preview: {response_text[:100]}...")
            successful_models.append(model_name)
            
        except Exception as e:
            print(f"❌ FAILED: {model_name}")
            print(f"🔍 Error: {str(e)}")
            failed_models.append((model_name, str(e)))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    if successful_models:
        print(f"✅ WORKING MODELS ({len(successful_models)}):")
        for model in successful_models:
            print(f"  - {model}")
    
    if failed_models:
        print(f"\n❌ FAILED MODELS ({len(failed_models)}):")
        for model, error in failed_models:
            print(f"  - {model}: {error}")
    
    # Test with Brisbane property prompt
    if successful_models:
        print(f"\n🏘️ Testing Brisbane property analysis with {successful_models[0]}...")
        try:
            response = client.messages.create(
                model=successful_models[0],
                max_tokens=500,
                messages=[{"role": "user", "content": "What new development applications were submitted in Brisbane this month?"}]
            )
            
            print("✅ Brisbane property analysis successful!")
            print(f"📝 Response: {response.content[0].text[:200]}...")
            
        except Exception as e:
            print(f"❌ Brisbane property analysis failed: {e}")
    
    return len(successful_models) > 0

def check_environment():
    """Check Python environment and dependencies"""
    print("🐍 Python Environment Check")
    print("=" * 30)
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check required packages
    required_packages = ['anthropic', 'flask', 'google.generativeai']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - installed")
        except ImportError:
            print(f"❌ {package} - missing")

def check_api_keys():
    """Check all API keys configuration"""
    print("\n🔑 API Keys Check")
    print("=" * 20)
    
    api_keys = {
        'CLAUDE_API_KEY': os.getenv('CLAUDE_API_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')
    }
    
    for key_name, key_value in api_keys.items():
        if key_value:
            print(f"✅ {key_name}: {key_value[:8]}...{key_value[-4:]}")
        else:
            print(f"❌ {key_name}: Not found")

def test_gemini_comparison():
    """Test Gemini for comparison"""
    print("\n🤖 Gemini API Comparison Test")
    print("=" * 35)
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key.strip())
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, can you explain what you are and what you can do?")
        
        print("✅ Gemini test successful!")
        print(f"📝 Response: {response.text[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Brisbane Property Intelligence - Claude Debug")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Run all checks
    check_environment()
    check_api_keys()
    
    # Test Claude API
    claude_success = test_claude_api()
    
    # Test Gemini for comparison
    gemini_success = test_gemini_comparison()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 FINAL DIAGNOSIS")
    print("=" * 60)
    
    if claude_success:
        print("✅ Claude API: WORKING - Your integration should work!")
        print("💡 Check your simple_llm.py initialization code")
    else:
        print("❌ Claude API: FAILING - This is the issue!")
        print("💡 Check API key, billing, or model availability")
    
    if gemini_success:
        print("✅ Gemini API: WORKING - Good fallback")
    else:
        print("❌ Gemini API: FAILING - Both APIs have issues")
    
    print(f"\n🏁 Debug completed at {datetime.now().strftime('%H:%M:%S')}")