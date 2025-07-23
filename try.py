from sqlalchemy import create_engine
import psycopg2

engine = create_engine("postgresql://postgres.lpwvvsxyspfzwagajxrd:8DduWNzeRt4z31Gs@aws-0-ap-south-1.pooler.supabase.com:6543/postgres")

try:
    with engine.connect() as conn:
        result = conn.execute("SELECT * FROM chats")
        print(result)
except Exception as e:
    print("Connection failed:", e)



