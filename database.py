# database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DATABASE_URL = os.getenv("DATABASE_PATH")

def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL no está configurado. Revisa tu .env o las variables de entorno.")
    # Si usas Azure PG o Render PG con SSL:
    # return psycopg2.connect(DATABASE_URL, sslmode="require")
    return psycopg2.connect(DATABASE_URL)

def get_report_names():
    """Devuelve lista de itemname desde public.reportbi ordenados por id."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT itemname FROM public.reportbi ORDER BY id;")
            rows = cur.fetchall()
            # rows puede ser [] y está bien; el template ahora lo maneja
            return [r["itemname"] for r in rows]


