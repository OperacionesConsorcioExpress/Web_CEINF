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
    get_report_id_by_name,   # <-- NUEVO aunque se puede eliminar si no se usa
    get_report_meta_by_name,   # <-- NUEVO: trae id, workspacename, itemname por nombre
    insert_survey_response,  # <-- NUEVO
    get_report_meta,           # <--- agrega esta línea
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
    # Informe a evaluar (string con itemname del reporte tal como viene del <select>)
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

    # Comentarios abiertos (máx. 500 palabras)
    sugerencias_mejora: str = Form(""),
):
    """
    1) Resuelve id, workspace e itemname del reporte por nombre (itemname).
    2) Valida que los comentarios tengan <= 500 palabras.
    3) Inserta en public.encuesta_bi:
       - id_reporte_bi = id del reporte
       - fecha = ahora en zona 'America/Bogota'
       - pregunta8 = workspacename
       - pregunta10 = itemname
    4) Devuelve JSON para que el front muestre el modal sin redirección.
    """

    # 1) Resolver id del reporte
    id_rep = get_report_id_by_name(reporte)
    if id_rep is None:
        raise HTTPException(status_code=400, detail="El reporte seleccionado no existe en la base.")

    # 2) (Opcional) Validación de 500 palabras
    if sugerencias_mejora:
        palabras = re.findall(r"\S+", sugerencias_mejora.strip())
        if len(palabras) > 500:
            raise HTTPException(
                status_code=422,
                detail=f"El comentario tiene {len(palabras)} palabras; el máximo permitido es 500.",
            )

    # 3) Traer metadatos del reporte para pregunta8/10
    meta = get_report_meta(id_rep)  # -> {"workspacename":..., "itemname":...} o None
    workspace_name = meta.get("workspacename") if meta else None
    item_name      = meta.get("itemname")      if meta else None

    try:
        new_id = insert_survey_response(
            id_reporte_bi=id_rep,
            # fecha ya la pone database.py (zona Bogotá)
            pregunta1=proceso,
            pregunta2=subproceso_evaluacion,
            pregunta3=cargo_evaluador,
            pregunta4=frecuencia_uso,
            pregunta5=str(claridad_precision),
            pregunta6=str(utilidad_general),
            pregunta7=str(utilidad_decisiones),
            pregunta8=workspace_name,                 # workspace del reporte
            pregunta9=(sugerencias_mejora or None),   # comentario (puede ser None)
            pregunta10=item_name,                     # itemname del reporte
        )
    except Exception as e:
        print("Error insertando encuesta:", e)
        raise HTTPException(status_code=500, detail="No se pudo guardar la encuesta. Intenta de nuevo.")

    # 4) Responder JSON (el front muestra el modal)
    return JSONResponse({"ok": True, "id": new_id, "reporte": reporte}, status_code=200)



'''

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