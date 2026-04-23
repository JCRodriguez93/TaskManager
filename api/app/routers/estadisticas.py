from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Proyecto, Tarea, Usuario
from app.schemas import EstadisticasResponse

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas"])


@router.get(
    "/",
    response_model=EstadisticasResponse,
    summary='Obtener estadísticas generales',
    description='Proporciona un resumen de las métricas clave del sistema, incluyendo el número total de proyectos, tareas por estado y usuarios.')
def obtener_estadisticas(db: Session = Depends(get_db)):
    return EstadisticasResponse(
        total_proyectos=db.query(Proyecto).count(),
        proyectos_activos=db.query(Proyecto).filter_by(estado="activo").count(),
        proyectos_pausados=db.query(Proyecto).filter_by(estado="pausado").count(),
        total_tareas=db.query(Tarea).count(),
        tareas_pendientes=db.query(Tarea).filter_by(estado="pendiente").count(),
        tareas_en_progreso=db.query(Tarea).filter_by(estado="en_progreso").count(),
        tareas_completadas=db.query(Tarea).filter_by(estado="completada").count(),
        total_usuarios=db.query(Usuario).count(),
    )
