# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

print("="  * 60)
print("Database Connection Diagnostic")
print("=" * 60)

# Check .env file
print("\n1. Checking .env file...")
env_file = BASE_DIR / '.env'
if env_file.exists():
    print(f"   [OK] .env file exists: {env_file}")

    # Read raw bytes
    with open(env_file, 'rb') as f:
        raw_data = f.read()
        print(f"   File size: {len(raw_data)} bytes")

        # Try UTF-8 decode
        try:
            content = raw_data.decode('utf-8')
            print(f"   [OK] UTF-8 decoding successful")
        except UnicodeDecodeError as e:
            print(f"   [ERROR] UTF-8 decoding failed: {e}")
            # Try GBK
            try:
                content = raw_data.decode('gbk')
                print(f"   [WARNING] File is GBK encoded, should be UTF-8")
                print(f"   Please re-save .env file as UTF-8 encoding")
            except:
                print(f"   [ERROR] Cannot decode file")
                sys.exit(1)
else:
    print(f"   [ERROR] .env file not found: {env_file}")
    sys.exit(1)

# Load environment variables
print("\n2. Loading environment variables...")
from dotenv import load_dotenv
load_dotenv(env_file)

db_name = os.getenv('DB_NAME', 'NOT_SET')
db_user = os.getenv('DB_USER', 'NOT_SET')
db_password = os.getenv('DB_PASSWORD', 'NOT_SET')
db_host = os.getenv('DB_HOST', 'NOT_SET')
db_port = os.getenv('DB_PORT', 'NOT_SET')

print(f"   DB_NAME: {db_name}")
print(f"   DB_USER: {db_user}")
print(f"   DB_PASSWORD: {'*' * len(db_password)} (length: {len(db_password)})")
print(f"   DB_HOST: {db_host}")
print(f"   DB_PORT: {db_port}")

# Check password encoding
print("\n3. Checking password encoding...")
if db_password != 'NOT_SET':
    try:
        encoded = db_password.encode('utf-8')
        print(f"   [OK] Password UTF-8 encoding successful")
        print(f"   Password bytes: {len(encoded)} bytes")
    except UnicodeEncodeError as e:
        print(f"   [ERROR] Password encoding failed: {e}")
        sys.exit(1)

# Test psycopg2 connection
print("\n4. Testing psycopg2 connection...")
try:
    import psycopg2
    print(f"   psycopg2 version: {psycopg2.__version__}")

    # Connect
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        client_encoding='UTF8'
    )
    print(f"   [OK] Connection successful!")

    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"   PostgreSQL: {version[:50]}...")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"   [ERROR] Connection failed: {e}")
    print(f"   Error type: {type(e).__name__}")

    # Print detailed error
    if hasattr(e, 'args'):
        for arg in e.args:
            print(f"   Error detail: {arg}")

    sys.exit(1)

print("\n" + "=" * 60)
print("All tests passed!")
print("=" * 60)
print("\nYou can now run: uv run python manage.py migrate")
