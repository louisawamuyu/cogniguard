"""Check what's happening with the database"""

print("=" * 50)
print("DATABASE DIAGNOSTIC")
print("=" * 50)

# Check 1: Can we import the database?
print("\n[1] Importing database.py...")
try:
    from database import ThreatDatabase
    print("    [OK] Import successful!")
except Exception as e:
    print(f"    [ERROR] Import failed: {e}")
    exit()

# Check 2: Can we create a connection?
print("\n[2] Creating database connection...")
try:
    db = ThreatDatabase()
    print("    [OK] ThreatDatabase created!")
except Exception as e:
    print(f"    [ERROR] Creation failed: {e}")
    exit()

# Check 3: Is it connected?
print("\n[3] Checking connection...")
if db.is_connected():
    print("    [OK] Database IS connected!")
else:
    print("    [ERROR] Database is NOT connected")

print("\n" + "=" * 50)
input("Press Enter to close...")