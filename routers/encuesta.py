# routers/encuesta.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent   # raíz del proyecto
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()

@router.get("/encuesta", response_class=HTMLResponse)
async def encuesta_get(request: Request, reporte: str | None = None):
    return templates.TemplateResponse(
        "encuesta.html",
        {"request": request, "nombre_reporte": reporte}
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
