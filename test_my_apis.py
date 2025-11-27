"""
🔍 API Diagnostic Tool
This will tell us EXACTLY what models work for YOUR API keys
"""

import os

print("=" * 60)
print("🔍 API DIAGNOSTIC TOOL")
print("=" * 60)

# ============================================
# STEP 1: Load your API keys from secrets.toml
# ============================================

print("\n📂 Loading API keys from secrets.toml...")

secrets_path = ".streamlit/secrets.toml"
api_keys = {}

try:
    with open(secrets_path, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                api_keys[key] = value
    print("✅ Loaded secrets.toml successfully!")
except FileNotFoundError:
    print("❌ secrets.toml not found!")
    print("   Please make sure .streamlit/secrets.toml exists")
    exit()

# Show what keys we found (hidden for security)
print("\n📋 Found these API keys:")
for key in api_keys:
    if api_keys[key]:
        print(f"   ✅ {key}: {'*' * 10}...{api_keys[key][-4:]}")
    else:
        print(f"   ❌ {key}: (empty)")

# ============================================
# STEP 2: Test Anthropic (Claude)
# ============================================

print("\n" + "=" * 60)
print("🧠 TESTING ANTHROPIC (CLAUDE)")
print("=" * 60)

anthropic_key = api_keys.get('ANTHROPIC_API_KEY', '')

if not anthropic_key:
    print("❌ No ANTHROPIC_API_KEY found in secrets.toml")
else:
    try:
        from anthropic import Anthropic
        
        client = Anthropic(api_key=anthropic_key)
        
        # List of Claude models to try (newest to oldest)
        claude_models = [
            "claude-sonnet-4-20250514",
            "claude-3-7-sonnet-20250219",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]
        
        print("\n🔍 Testing Claude models...")
        working_claude_models = []
        
        for model in claude_models:
            try:
                print(f"   Testing {model}...", end=" ")
                response = client.messages.create(
                    model=model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                print("✅ WORKS!")
                working_claude_models.append(model)
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "not_found" in error_msg:
                    print("❌ Not found")
                elif "401" in error_msg or "authentication" in error_msg.lower():
                    print("❌ Auth failed - check API key")
                elif "402" in error_msg or "billing" in error_msg.lower():
                    print("❌ Needs billing")
                elif "rate" in error_msg.lower():
                    print("⚠️ Rate limited (but model exists!)")
                    working_claude_models.append(model)
                else:
                    print(f"❌ Error: {error_msg[:50]}")
        
        print("\n" + "-" * 40)
        if working_claude_models:
            print("✅ WORKING CLAUDE MODELS FOR YOU:")
            for m in working_claude_models:
                print(f"   ✅ {m}")
            print(f"\n📝 USE THIS MODEL: {working_claude_models[0]}")
        else:
            print("❌ NO CLAUDE MODELS WORK!")
            print("   Possible issues:")
            print("   1. API key is invalid")
            print("   2. Need to add billing at console.anthropic.com")
            print("   3. API key expired")
            
    except ImportError:
        print("❌ anthropic package not installed")
        print("   Run: pip install anthropic")
    except Exception as e:
        print(f"❌ Error: {e}")

# ============================================
# STEP 3: Test Google (Gemini)
# ============================================

print("\n" + "=" * 60)
print("✨ TESTING GOOGLE (GEMINI)")
print("=" * 60)

gemini_key = api_keys.get('GEMINI_API_KEY', '')

if not gemini_key:
    print("❌ No GEMINI_API_KEY found in secrets.toml")
else:
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=gemini_key)
        
        print("\n🔍 Listing ALL available Gemini models...")
        print("-" * 40)
        
        available_models = []
        
        try:
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    model_name = model.name.replace('models/', '')
                    available_models.append(model_name)
                    print(f"   ✅ {model_name}")
        except Exception as e:
            print(f"   ❌ Could not list models: {e}")
        
        print("-" * 40)
        
        if available_models:
            # Find the best model
            preferred_order = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
            best_model = None
            
            for pref in preferred_order:
                for avail in available_models:
                    if pref in avail:
                        best_model = avail
                        break
                if best_model:
                    break
            
            if not best_model:
                best_model = available_models[0]
            
            print(f"\n📝 USE THIS MODEL: {best_model}")
            
            # Test it
            print(f"\n🧪 Testing {best_model}...")
            try:
                test_model = genai.GenerativeModel(best_model)
                response = test_model.generate_content("Hi")
                print(f"   ✅ {best_model} works perfectly!")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print("❌ NO GEMINI MODELS AVAILABLE!")
            print("   Possible issues:")
            print("   1. API key is invalid")
            print("   2. API key doesn't have Gemini access")
            print("   3. Region restrictions")
            
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("   Run: pip install google-generativeai")
    except Exception as e:
        print(f"❌ Error: {e}")

# ============================================
# STEP 4: Test OpenAI (GPT)
# ============================================

print("\n" + "=" * 60)
print("🤖 TESTING OPENAI (GPT)")
print("=" * 60)

openai_key = api_keys.get('OPENAI_API_KEY', '')

if not openai_key:
    print("❌ No OPENAI_API_KEY found in secrets.toml")
else:
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=openai_key)
        
        # List of OpenAI models to try
        openai_models = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]
        
        print("\n🔍 Testing OpenAI models...")
        working_openai_models = []
        
        for model in openai_models:
            try:
                print(f"   Testing {model}...", end=" ")
                response = client.chat.completions.create(
                    model=model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                print("✅ WORKS!")
                working_openai_models.append(model)
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg:
                    print("❌ Not found")
                elif "401" in error_msg:
                    print("❌ Auth failed")
                elif "429" in error_msg:
                    print("⚠️ Rate limited (but exists!)")
                    working_openai_models.append(model)
                elif "billing" in error_msg.lower():
                    print("❌ Needs billing")
                else:
                    print(f"❌ {error_msg[:40]}")
        
        print("\n" + "-" * 40)
        if working_openai_models:
            print("✅ WORKING OPENAI MODELS FOR YOU:")
            for m in working_openai_models:
                print(f"   ✅ {m}")
            print(f"\n📝 USE THIS MODEL: {working_openai_models[0]}")
        else:
            print("❌ NO OPENAI MODELS WORK!")
            
    except ImportError:
        print("❌ openai package not installed")
        print("   Run: pip install openai")
    except Exception as e:
        print(f"❌ Error: {e}")

# ============================================
# FINAL SUMMARY
# ============================================

print("\n" + "=" * 60)
print("📋 SUMMARY - COPY THESE MODEL NAMES!")
print("=" * 60)
print("""
After running this script, you'll see which models work.
Use those EXACT model names in your code!

Example output to look for:
   📝 USE THIS MODEL: claude-3-haiku-20240307
   📝 USE THIS MODEL: gemini-1.5-flash
   📝 USE THIS MODEL: gpt-3.5-turbo
""")

print("\n✅ Diagnostic complete!")
print("=" * 60)

input("\nPress Enter to close...")