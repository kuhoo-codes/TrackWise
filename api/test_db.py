# test_db.py
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    print("✅ Connected to PostgreSQL!")
    conn.close()
except Exception as e:
    print("❌ DB connection failed:", e)
