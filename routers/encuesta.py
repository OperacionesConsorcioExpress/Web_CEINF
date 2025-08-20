# routers/encuesta.py
# ---------------------------------------------------
# Router de la encuesta:
#  - GET /encuesta: pinta el formulario (reportes, procesos)
#  - GET /api/subprocesos: devuelve subprocesos por proceso (AJAX)
#  - POST /encuesta: valida y guarda en public.encuesta_bi
# ---------------------------------------------------

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from database import (
    get_report_names,
    get_procesos,
    get_subprocesos,
    get_report_id_by_name,   # <-- NUEVO
    insert_survey_response,  # <-- NUEVO
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()


# ------------------ VISTA GET: formulario ------------------

@router.get("/encuesta", response_class=HTMLResponse, name="encuesta_get")
async def encuesta_get(request: Request, reporte: str | None = None):
    """
    - Si viene ?reporte=... -> input readonly.
    - Si NO viene -> traer lista desde PostgreSQL y mostrar <select>.
    - Trae procesos para el combo dependiente de subproceso.
    """
    nombres = None
    procesos = []
    if not reporte:
        try:
            nombres = get_report_names()
        except Exception as e:
            print("Error cargando nombres de reportes:", e)

    try:
        procesos = get_procesos()
    except Exception as e:
        print("Error cargando procesos:", e)

    # versión estática de la hoja CSS para bust de caché
    static_version = "1.0.0"

    return templates.TemplateResponse(
        "encuesta.html",
        {
            "request": request,
            "nombre_reporte": reporte,
            "lista_reportes": nombres,
            "lista_procesos": procesos,
            "static_version": static_version,
        },
    )


# ------------------ API para subprocesos (AJAX) ------------------

@router.get("/api/subprocesos")
async def api_subprocesos(proceso: str):
    """Devuelve JSON con los subprocesos para un proceso dado."""
    try:
        items = get_subprocesos(proceso)
        return JSONResponse({"ok": True, "items": items})
    except Exception as e:
        print("Error en /api/subprocesos:", e)
        return JSONResponse({"ok": False, "items": []}, status_code=500)


# ------------------ POST: guardar respuesta ------------------

@router.post("/encuesta")
async def encuesta_post(
    # Informe a evaluar (string con itemname del reporte)
    reporte: str = Form(...),

    # Proceso/Subproceso seleccionados
    proceso: str = Form(...),
    subproceso_evaluacion: str = Form(...),

    # Cargo del evaluador
    cargo_evaluador: str = Form(...),

    # Matriz 1-5
    claridad_precision: int = Form(...),
    utilidad_general: int = Form(...),
    utilidad_decisiones: int = Form(...),

    # Frecuencia (diario, semanal, mensual, eventual)
    frecuencia_uso: str = Form(...),

    # Comentarios abiertos
    sugerencias_mejora: str = Form(""),
):
    """
    1) Resuelve id del reporte por nombre.
    2) Valida que comentarios tengan <= 500 palabras (además de la restricción de DB si la pusiste).
    3) Inserta el registro en public.encuesta_bi.
    4) Redirige a una página de confirmación (la que ya usabas).
    """

    # 1) Resolver id del reporte
    id_rep = get_report_id_by_name(reporte)
    if id_rep is None:
        # Elegimos rechazar si no existe el reporte; si prefieres insertar con NULL/0, cambia esto.
        raise HTTPException(status_code=400, detail="El reporte seleccionado no existe en la base.")

    # 2) Validación de máximo 500 palabras en comentarios
    #    (la DB puede tener además un CHECK; aquí damos feedback amable al usuario)
    if sugerencias_mejora:
        # Cuenta palabras separadas por espacios en blanco
        palabras = re.findall(r"\S+", sugerencias_mejora.strip())
        if len(palabras) > 500:
            raise HTTPException(
                status_code=422,
                detail=f"El comentario tiene {len(palabras)} palabras; el máximo permitido es 500.",
            )

    # 3) Preparar el mapeo a columnas de encuesta_bi
    #    - fecha: ahora (UTC)
    #    - pregunta1..9 según especificación del usuario
    # dentro de encuesta_post, antes del insert:
    fecha_now = datetime.now(ZoneInfo("America/Bogota"))

    # Nota: en la tabla pregunta5/6/7 son texto; pasamos los valores numéricos como str
    try:
        new_id = insert_survey_response(
            id_reporte_bi=id_rep,
            fecha=fecha_now,
            pregunta1=proceso,
            pregunta2=subproceso_evaluacion,
            pregunta3=cargo_evaluador,
            pregunta4=frecuencia_uso,
            pregunta5=str(claridad_precision),
            pregunta6=str(utilidad_general),
            pregunta7=str(utilidad_decisiones),
            pregunta8="",  # o None si hiciste la columna nullable
            pregunta9=sugerencias_mejora or None,
        )
    except Exception as e:
        # log opcional
        print("Error insertando encuesta:", e)
        raise HTTPException(status_code=500, detail="No se pudo guardar la encuesta. Intenta de nuevo.")

# ...

    # 4) Responder en JSON para que el front muestre el modal sin navegar
    return JSONResponse(
        {"ok": True, "id": new_id, "reporte": reporte},
        status_code=200
    )


'''

# routers/encuesta.py
# ---------------------------------------------------------------------------
# Rutas de la encuesta:
# - GET  /encuesta           -> Muestra formulario (reportes + procesos)
# - GET  /api/subprocesos    -> Devuelve subprocesos por proceso (JSON)
# - POST /encuesta           -> Recibe envío del formulario y redirige
# ---------------------------------------------------------------------------

from pathlib import Path
from time import time
from typing import Optional

from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# Funciones de acceso a BD (debes tenerlas en database.py)
from database import (
    get_report_names,   # lista de reportes BI (para el primer select)
    get_procesos,       # lista de procesos (para el combo de área)
    get_subprocesos,    # lista de subprocesos según proceso (combo dependiente)
    # insert_survey_response  # <- cuando integremos el guardado real
)

# ---------------------------------------------------------------------------
# Config de paths y templates
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /encuesta
# Carga el formulario. Si viene ?reporte=... lo muestra readonly; si no,
# trae la lista de reportes desde BD. Además trae la lista de procesos.
# ---------------------------------------------------------------------------
@router.get("/encuesta", response_class=HTMLResponse, name="encuesta_get")
async def encuesta_get(request: Request, reporte: Optional[str] = None):
    # 1) Reportes BI
    nombres = None
    if not reporte:
        try:
            nombres = get_report_names()
        except Exception as e:
            # Log para diagnóstico (Render/local)
            print("[encuesta_get] Error cargando nombres de reportes:", e)
            nombres = None

    # 2) Procesos (para la pregunta de área/proceso)
    procesos = []
    try:
        procesos = get_procesos()
    except Exception as e:
        print("[encuesta_get] Error cargando procesos:", e)
        procesos = []

    # 3) Render del template
    return templates.TemplateResponse(
        "encuesta.html",
        {
            "request": request,
            "nombre_reporte": reporte,     # si viene por query, el input queda readonly
            "lista_reportes": nombres,     # si NO viene reporte -> <select>
            "lista_procesos": procesos,    # llena el primer combo (proceso)
            "static_version": int(time()), # cache-busting para CSS/JS
        }
    )


# ---------------------------------------------------------------------------
# GET /api/subprocesos?proceso=...
# Devuelve JSON con los subprocesos para un proceso dado.
# Usado por el combo dependiente vía fetch() en encuesta.html
# ---------------------------------------------------------------------------
@router.get("/api/subprocesos")
async def api_subprocesos(proceso: str = Query(..., min_length=1)):
    try:
        items = get_subprocesos(proceso)
        return JSONResponse({"ok": True, "items": items})
    except Exception as e:
        print("[api_subprocesos] Error:", e)
        return JSONResponse({"ok": False, "items": [], "error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# POST /encuesta
# Recibe los datos del formulario. Por ahora solo redirige a la página
# de "gracias". Cuando integremos el guardado, llamaremos a insert_survey_response().
# ---------------------------------------------------------------------------
@router.post("/encuesta")
async def encuesta_post(
    request: Request,
    reporte: str = Form(...),
    # CAMBIO: ahora el "área" viene como proceso y subproceso separados:
    proceso: str = Form(...),
    subproceso_evaluacion: str = Form(...),
    cargo_evaluador: str = Form(...),
    claridad_precision: int = Form(...),
    utilidad_general: int = Form(...),
    utilidad_decisiones: int = Form(...),
    frecuencia_uso: str = Form(...),
    sugerencias_mejora: str = Form(...)
):
    # TODO (próximo paso): guardar en BD con insert_survey_response(...)
    # new_id = insert_survey_response(...)

    # Redirección a la página de confirmación
    return RedirectResponse(
        url=f"/paginas/forms_redirect?reporte={reporte}",
        status_code=303
    )

'''
