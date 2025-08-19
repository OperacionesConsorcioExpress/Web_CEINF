# routers/encuesta.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from database import get_report_names  # <-- función del paso 1

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()

@router.get("/encuesta", response_class=HTMLResponse, name="encuesta_get")
async def encuesta_get(request: Request, reporte: str | None = None):
    """
    - Si viene ?reporte=... -> input readonly.
    - Si NO viene -> traer lista desde PostgreSQL y mostrar <select>.
    """
    nombres = None
    if not reporte:
        try:
            nombres = get_report_names()
        except Exception as e:
            # Mira los logs en local/Render si algo falla aquí
            print("Error cargando nombres de reportes:", e)

    return templates.TemplateResponse(
        "encuesta.html",
        {"request": request, "nombre_reporte": reporte, "lista_reportes": nombres}
    )

@router.post("/encuesta")
async def encuesta_post(
    reporte: str = Form(...),
    area_evaluacion: str = Form(""),
    cargo_evaluador: str = Form(""),
    claridad_precision: int = Form(...),
    utilidad_general: int = Form(...),
    utilidad_decisiones: int = Form(...),
    frecuencia_uso: str = Form(...),
    sugerencias_mejora: str = Form("")
):
    return RedirectResponse(url=f"/paginas/forms_redirect?reporte={reporte}", status_code=303)
