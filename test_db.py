print("=" * 50)
print("SIMPLE DATABASE TEST")
print("=" * 50)

# Step 1: Check if supabase is installed
print("\n[1] Checking if Supabase is installed...")
try:
    from supabase import create_client
    print("    [OK] Supabase is installed!")
except ImportError:
    print("    [ERROR] Supabase is NOT installed!")
    print("    Run: pip install supabase")

# Step 2: Check if secrets file exists
print("\n[2] Checking for secrets file...")
import os
secrets_path = ".streamlit/secrets.toml"
if os.path.exists(secrets_path):
    print(f"    [OK] Found: {secrets_path}")
    with open(secrets_path, 'r') as f:
        content = f.read()
        if "SUPABASE_URL" in content:
            print("    [OK] SUPABASE_URL is set")
        else:
            print("    [ERROR] SUPABASE_URL not found in secrets")
        if "SUPABASE_KEY" in content:
            print("    [OK] SUPABASE_KEY is set")
        else:
            print("    [ERROR] SUPABASE_KEY not found in secrets")
else:
    print(f"    [ERROR] Secrets file not found at: {secrets_path}")
    print("    You need to create it!")

# Step 3: Try to connect
print("\n[3] Trying to connect to Supabase...")
try:
    # Try to read secrets
    supabase_url = None
    supabase_key = None
    
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r') as f:
            for line in f:
                if line.startswith("SUPABASE_URL"):
                    supabase_url = line.split("=")[1].strip().strip('"').strip("'")
                if line.startswith("SUPABASE_KEY"):
                    supabase_key = line.split("=")[1].strip().strip('"').strip("'")
    
    if supabase_url and supabase_key:
        print(f"    URL: {supabase_url[:30]}...")
        print(f"    KEY: {supabase_key[:20]}...")
        
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)
        print("    [OK] Connected to Supabase!")
    else:
        print("    [ERROR] Missing URL or KEY")

except Exception as e:
    print(f"    [ERROR] Connection failed: {e}")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)
input("\nPress Enter to close...")