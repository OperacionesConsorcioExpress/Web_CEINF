# database.py
# -----------------------------------------------
# Capa de acceso a datos para PostgreSQL.
# - Conexión usando psycopg2.
# - Utilidades para leer catálogos (reportes, procesos, subprocesos).
# - Inserción de respuestas de encuesta.
# -----------------------------------------------

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
import pytz

# Para entorno local (.env); en Render usas Environment Vars.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# URL esperada: postgresql://usuario:password@host:5432/base
DATABASE_URL = os.getenv("DATABASE_PATH")


def get_conn():
    """Devuelve una conexión a PostgreSQL.
    Lanza RuntimeError si la variable no está configurada.
    """
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL no está configurado")
    # Si tu Postgres exige TLS: psycopg2.connect(DATABASE_URL, sslmode="require")
    return psycopg2.connect(DATABASE_URL)


# ---------- LECTURAS DE CATÁLOGO (ya existentes / usadas en UI) ----------
def get_report_names():
    """Lista el itemname de public.reportbi (para el <select> de 'reporte')."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT itemname FROM public.reportbi ORDER BY id;")
            rows = cur.fetchall()
            return [r["itemname"] for r in rows]

def get_report_meta_by_name(itemname: str):
    """
    Devuelve meta del reporte por NOMBRE (itemname):
    { 'id': int, 'workspacename': str, 'itemname': str }
    Lanza ValueError si no existe.
    """
    q = """
        SELECT id, workspacename, itemname
        FROM public.reportbi
        WHERE itemname = %s
        LIMIT 1;
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(q, (itemname,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Reporte no encontrado: {itemname!r}")
            return {
                "id": row["id"],
                "workspacename": row["workspacename"],
                "itemname": row["itemname"],
            }


def get_procesos():
    """Lista de procesos únicos desde public.procesos.proceso (ordenada)."""
    q = """
        SELECT DISTINCT proceso
        FROM public.procesos
        WHERE proceso IS NOT NULL AND btrim(proceso) <> ''
        ORDER BY proceso;
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(q)
            rows = cur.fetchall()
            return [r["proceso"] for r in rows]


def get_subprocesos(proceso: str):
    """Lista de subprocesos para un proceso dado (ordenada)."""
    q = """
        SELECT subproceso
        FROM public.procesos
        WHERE proceso = %s
          AND subproceso IS NOT NULL
          AND btrim(subproceso) <> ''
        ORDER BY subproceso;
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(q, (proceso,))
            rows = cur.fetchall()
            return [r["subproceso"] for r in rows]


# ---------- NUEVO: Resolver id del reporte por nombre ----------
def get_report_id_by_name(itemname: str) -> int | None:
    """Devuelve el id de public.reportbi dado su itemname. None si no existe."""
    q = "SELECT id FROM public.reportbi WHERE itemname = %s LIMIT 1;"
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (itemname,))
            row = cur.fetchone()
            return int(row[0]) if row else None

# --- NUEVO: obtener metadatos del reporte por id ---
def get_report_meta(id_reporte: int) -> dict | None:
    """
    Devuelve {'workspacename': str, 'itemname': str} para el reportbi.id dado.
    Si no existe, retorna None.
    """
    q = """
        SELECT workspacename, itemname
        FROM public.reportbi
        WHERE id = %s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (id_reporte,))
            row = cur.fetchone()
            if not row:
                return None
            workspacename, itemname = row
            return {
                "workspacename": workspacename,
                "itemname": itemname,
            }


# ---------- NUEVO: Insertar respuesta de encuesta ----------

BOGOTA_TZ = pytz.timezone("America/Bogota")

def insert_survey_response(
    *,
    id_reporte_bi: int,
    pregunta1: str,
    pregunta2: str,
    pregunta3: str,
    pregunta4: str,
    pregunta5: str,
    pregunta6: str,
    pregunta7: str,
    pregunta8: str,   # <-- workspacename
    pregunta9: str,
    pregunta10: str,  # <-- itemname
) -> int:
    """
    Inserta una fila en public.encuesta_bi.
    - fecha se toma en zona horaria de Bogotá
    - pregunta8 = workspacename (reportbi)
    - pregunta10 = itemname (reportbi)
    Devuelve el id (serial) insertado.
    """
    # Fecha/hora Bogotá
    fecha_bog = datetime.now(BOGOTA_TZ)

    q = """
        INSERT INTO public.encuesta_bi
        (id_reporte_bi, fecha, pregunta1, pregunta2, pregunta3, pregunta4,
         pregunta5, pregunta6, pregunta7, pregunta8, pregunta9, pregunta10)
        VALUES
        (%s, %s, %s, %s, %s, %s,
         %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    params = (
        id_reporte_bi, fecha_bog,
        pregunta1, pregunta2, pregunta3, pregunta4,
        pregunta5, pregunta6, pregunta7, pregunta8, pregunta9, pregunta10
    )
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, params)
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id


'''
def insert_survey_response(
    *,
    id_reporte_bi: int,
    # si prefieres que la DB ponga la hora, puedes omitir y usar NOW() en el SQL
    fecha: datetime | None = None,
    pregunta1: str | None = None,
    pregunta2: str | None = None,
    pregunta3: str | None = None,
    pregunta4: str | None = None,
    pregunta5: str | None = None,
    pregunta6: str | None = None,
    pregunta7: str | None = None,
    pregunta8: str | None = None,
    pregunta9: str | None = None,
    
) -> int:
    """Inserta un registro en public.encuesta_bi y devuelve el id generado."""
    q = """
        INSERT INTO public.encuesta_bi
            (id_reporte_bi, fecha, pregunta1, pregunta2, pregunta3, pregunta4,
             pregunta5, pregunta6, pregunta7, pregunta8, pregunta9)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    # Fecha por defecto: ahora (UTC)
    if fecha is None:
        fecha = datetime.now(timezone.utc)

    params = (
        id_reporte_bi,
        fecha,
        pregunta1, pregunta2, pregunta3, pregunta4,
        pregunta5, pregunta6, pregunta7, pregunta8, pregunta9,
    )

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, params)
            new_id = cur.fetchone()[0]
    return int(new_id)
'''
