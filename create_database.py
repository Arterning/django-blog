# -*- coding: utf-8 -*-
"""
创建PostgreSQL数据库的脚本
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

print("=" * 60)
print("Create PostgreSQL Database")
print("=" * 60)

db_name = os.getenv('DB_NAME', 'django_blog')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')

print(f"\nTarget database: {db_name}")
print(f"User: {db_user}")
print(f"Host: {db_host}:{db_port}")

# Connect to postgres database (default)
print("\n1. Connecting to PostgreSQL...")
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    conn = psycopg2.connect(
        dbname='postgres',  # Connect to default database
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    print("   [OK] Connected to PostgreSQL")

except Exception as e:
    print(f"   [ERROR] Connection failed: {e}")
    print("\nPlease check:")
    print("  1. PostgreSQL service is running")
    print("  2. Username and password in .env are correct")
    print("  3. PostgreSQL is listening on localhost:5432")
    sys.exit(1)

# Check if database exists
print(f"\n2. Checking if database '{db_name}' exists...")
cursor = conn.cursor()
cursor.execute(
    "SELECT 1 FROM pg_database WHERE datname = %s",
    (db_name,)
)
exists = cursor.fetchone()

if exists:
    print(f"   [INFO] Database '{db_name}' already exists")
else:
    print(f"   [INFO] Database '{db_name}' does not exist")
    print(f"\n3. Creating database '{db_name}'...")

    try:
        cursor.execute(f'CREATE DATABASE "{db_name}" ENCODING "UTF8"')
        print(f"   [OK] Database '{db_name}' created successfully!")
    except Exception as e:
        print(f"   [ERROR] Failed to create database: {e}")
        cursor.close()
        conn.close()
        sys.exit(1)

cursor.close()
conn.close()

# Verify the database
print(f"\n4. Verifying database '{db_name}'...")
try:
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"   [OK] Successfully connected to '{db_name}'")
    print(f"   PostgreSQL: {version[:50]}...")
    cursor.close()
    conn.close()

except Exception as e:
    print(f"   [ERROR] Failed to connect to '{db_name}': {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Database setup complete!")
print("=" * 60)
print(f"\nNext steps:")
print(f"  1. Run migrations: uv run python manage.py migrate")
print(f"  2. Create superuser: uv run python manage.py createsuperuser")
print(f"  3. Start server: uv run python manage.py runserver")
