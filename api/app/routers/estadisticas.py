# api/app/routers/estadisticas.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Proyecto, Tarea, Usuario
from app.schemas import EstadisticasResponse
from app.security import get_current_user

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas"])


@router.get(
    "/",
    response_model=EstadisticasResponse,
    summary="Obtener estadísticas generales",
    description="Proporciona un resumen de las métricas clave del sistema. Si el usuario no es admin, devuelve solo sus datos."
)
def obtener_estadisticas(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    """
    Si el usuario es admin devuelve totales globales.
    Si no es admin devuelve estadísticas filtradas por el usuario autenticado.
    """
    if usuario.es_admin:
        total_proyectos = db.query(Proyecto).count()
        proyectos_activos = db.query(Proyecto).filter_by(estado="activo").count()
        proyectos_pausados = db.query(Proyecto).filter_by(estado="pausado").count()
        total_tareas = db.query(Tarea).count()
        tareas_pendientes = db.query(Tarea).filter_by(estado="pendiente").count()
        tareas_en_progreso = db.query(Tarea).filter_by(estado="en_progreso").count()
        tareas_completadas = db.query(Tarea).filter_by(estado="completada").count()
        total_usuarios = db.query(Usuario).count()
    else:
        total_proyectos = db.query(Proyecto).filter_by(propietario_id=usuario.id).count()
        proyectos_activos = db.query(Proyecto).filter_by(propietario_id=usuario.id, estado="activo").count()
        proyectos_pausados = db.query(Proyecto).filter_by(propietario_id=usuario.id, estado="pausado").count()
        total_tareas = db.query(Tarea).filter_by(asignado_id=usuario.id).count()
        tareas_pendientes = db.query(Tarea).filter_by(asignado_id=usuario.id, estado="pendiente").count()
        tareas_en_progreso = db.query(Tarea).filter_by(asignado_id=usuario.id, estado="en_progreso").count()
        tareas_completadas = db.query(Tarea).filter_by(asignado_id=usuario.id, estado="completada").count()
        total_usuarios = 1
    return EstadisticasResponse(
        total_proyectos=total_proyectos,
        proyectos_activos=proyectos_activos,
        proyectos_pausados=proyectos_pausados,
        total_tareas=total_tareas,
        tareas_pendientes=tareas_pendientes,
        tareas_en_progreso=tareas_en_progreso,
        tareas_completadas=tareas_completadas,
        total_usuarios=total_usuarios,
    )
