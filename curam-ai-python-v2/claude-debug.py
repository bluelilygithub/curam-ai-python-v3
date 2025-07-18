"""
Claude API Debug Script
Test Claude API connection step by step to identify the issue
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_claude_api():
    """Test Claude API connection step by step"""
    
    print("🔍 CLAUDE API DEBUG TEST")
    print("=" * 50)
    
    # Step 1: Check API key
    api_key = os.getenv('CLAUDE_API_KEY')
    print(f"1. API Key configured: {'✓' if api_key else '✗'}")
    if api_key:
        print(f"   Key length: {len(api_key)}")
        print(f"   Key starts with: {api_key[:8]}...")
    else:
        print("   ERROR: No CLAUDE_API_KEY environment variable found")
        return False
    
    # Step 2: Test import
    try:
        import anthropic
        print(f"2. Anthropic library import: ✓")
        print(f"   Version: {anthropic.__version__}")
    except ImportError as e:
        print(f"2. Anthropic library import: ✗ - {e}")
        return False
    
    # Step 3: Test client initialization
    try:
        client = anthropic.Anthropic(api_key=api_key.strip())
        print(f"3. Client initialization: ✓")
    except Exception as e:
        print(f"3. Client initialization: ✗ - {e}")
        return False
    
    # Step 4: Test different models (match what works in JS)
    models_to_test = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620", 
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]
    
    for model in models_to_test:
        try:
            print(f"\n4. Testing model: {model}")
            
            response = client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            print(f"   ✓ Model {model} works!")
            print(f"   Response: {response.content[0].text}")
            return True
            
        except Exception as e:
            print(f"   ✗ Model {model} failed: {e}")
            continue
    
    print("\n❌ All models failed!")
    return False

def test_with_minimal_example():
    """Test with the most minimal possible example"""
    print("\n🧪 MINIMAL TEST")
    print("=" * 30)
    
    try:
        import anthropic
        
        client = anthropic.Anthropic(
            api_key=os.getenv('CLAUDE_API_KEY')
        )
        
        # Minimal request
        message = client.messages.create(
            model="claude-3-haiku-20240307",  # Most basic model
            max_tokens=5,
            messages=[
                {"role": "user", "content": "Hi"}
            ]
        )
        
        print(f"✓ Minimal test successful!")
        print(f"Response: {message.content[0].text}")
        return True
        
    except Exception as e:
        print(f"✗ Minimal test failed: {e}")
        print(f"Error type: {type(e)}")
        return False

def compare_with_working_js():
    """Show what might be different from JS implementation"""
    print("\n🔄 JS vs Python Comparison")
    print("=" * 40)
    
    print("In your JS frontend, Claude likely works with:")
    print("- Model: claude-3-5-sonnet-20241022 or similar")
    print("- Direct API calls via fetch()")
    print("- Same API key from environment")
    
    print("\nIn Python backend, we're using:")
    print("- anthropic library wrapper")
    print("- Same API key")
    print("- Same model names")
    
    print("\nPossible differences:")
    print("1. Library version compatibility")
    print("2. API endpoint differences")
    print("3. Request format differences")
    print("4. Authentication header format")

if __name__ == "__main__":
    print("Starting Claude API debug session...")
    
    # Run tests
    basic_test = test_claude_api()
    
    if not basic_test:
        minimal_test = test_with_minimal_example()
    
    compare_with_working_js()
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATIONS:")
    print("1. Update anthropic library: pip install anthropic --upgrade")
    print("2. Try different model names")
    print("3. Check API key format in environment")
    print("4. Test with curl to verify API access")