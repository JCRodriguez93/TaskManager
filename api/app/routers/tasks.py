# api/app/routers/tasks.py — versión completa
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Tarea, Proyecto, Usuario
from app.security import get_current_user
from app.schemas import TareaCreate, TareaUpdate, TareaResponse

router = APIRouter(prefix='/tareas', tags=['Tareas'])

ESTADOS_VALIDOS = ['pendiente', 'en_progreso', 'revision', 'completada']
PRIORIDADES_VALIDAS = ['baja', 'media', 'alta', 'urgente']

# ── GET /tareas/ — Listar con filtros ────────────────────────────────
@router.get(
    '/',
    response_model=List[TareaResponse],
    summary='Listar tareas',
    description='Obtiene una lista de tareas permitiendo filtrar por proyecto, prioridad, estado y usuario asignado. Incluye paginación básica mediante skip y limit.'
)
def listar(
    proyecto_id: Optional[int] = Query(None, description='Filtrar tareas pertenecientes a un ID de proyecto específico'),
    prioridad: Optional[str] = Query(None, description='Filtrar por nivel de prioridad: baja, media, alta o urgente'),
    estado: Optional[str] = Query(None, description='Filtrar por estado actual: pendiente, en_progreso, revision o completada'),
    asignado_id: Optional[int] = Query(None, description='Filtrar tareas asignadas a un ID de usuario concreto'),
    skip: int = Query(0, ge=0, description='Número de registros a omitir (útil para paginación manual)'),
    limit: int = Query(50, ge=1, le=200, description='Cantidad máxima de registros a retornar (máximo 200)'),
    db: Session = Depends(get_db)
):
    query = db.query(Tarea)

    if proyecto_id:
        query = query.filter_by(proyecto_id=proyecto_id)

    if prioridad:
        if prioridad not in PRIORIDADES_VALIDAS:
            raise HTTPException(
                400,
                f'Prioridad no válida. Usa: {PRIORIDADES_VALIDAS}'
            )
        query = query.filter_by(prioridad=prioridad)

    if estado:
        if estado not in ESTADOS_VALIDOS:
            raise HTTPException(
                400,
                f'Estado no válido. Usa: {ESTADOS_VALIDOS}'
            )
        query = query.filter_by(estado=estado)

    if asignado_id:
        query = query.filter_by(asignado_id=asignado_id)

    return query.offset(skip).limit(limit).all()

# ── GET /tareas/{id} ─────────────────────────────────────────────────
@router.get(
    '/{tarea_id}',
    response_model=TareaResponse,
    summary='Obtener una tarea',
    description='Recupera los detalles completos de una tarea específica identificada por su ID único.'
)
def obtener(tarea_id: int, db: Session = Depends(get_db)):
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()

    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')

    return tarea

# ── POST /tareas/ — Crear ────────────────────────────────────────────
@router.post(
    '/',
    response_model=TareaResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Crear una tarea',
    description='Crea una nueva tarea. Es obligatorio proporcionar un ID de proyecto válido al que asociarla.'
)
def crear(
    datos: TareaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = db.query(Proyecto).filter_by(id=datos.proyecto_id).first()

    if not proyecto:
        raise HTTPException(
            404,
            f'No existe el proyecto con ID {datos.proyecto_id}'
        )
    if proyecto.propietario_id != usuario.id and not usuario.es_admin:
        raise HTTPException(
            status_code=403,
            detail='No tienes permiso para crear tareas en este proyecto'
        )

    tarea = Tarea(**datos.model_dump())

    db.add(tarea)
    db.commit()
    db.refresh(tarea)

    return tarea

# ── PATCH /tareas/{id} — Actualizar parcial ──────────────────────────
@router.patch(
    '/{tarea_id}',
    response_model=TareaResponse,
    summary='Actualizar una tarea',
    description='Permite la actualización parcial de los campos de una tarea. Solo se modificarán los campos enviados en el cuerpo de la petición.'
)
def actualizar(
    tarea_id: int,
    datos: TareaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()

    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')

    proyecto = db.query(Proyecto).filter_by(id=tarea.proyecto_id).first()
    if not proyecto:
        raise HTTPException(500, 'Proyecto asociado a la tarea no encontrado')

    if not (tarea.asignado_id == usuario.id or proyecto.propietario_id == usuario.id or usuario.es_admin):
        raise HTTPException(
            status_code=403,
            detail='No tienes permiso para actualizar esta tarea'
        )

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(tarea, campo, valor)

    db.commit()
    db.refresh(tarea)

    return tarea

# ── PATCH /tareas/{id}/estado — Cambio de estado ─────────────────────
# Endpoint especializado: el estado tiene lógica de transición propia
@router.patch(
    '/{tarea_id}/estado',
    response_model=TareaResponse,
    summary='Cambiar el estado de una tarea',
    description='Cambia solo el estado de una tarea validando la transición.'
)
def cambiar_estado(
    tarea_id: int,
    nuevo_estado: str = Body(
        ...,
        embed=True,
        description='Nuevo estado de la tarea'
    ),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    if nuevo_estado not in ESTADOS_VALIDOS:
        raise HTTPException(
            400,
            detail={
                'mensaje': 'Estado no válido',
                'estados_validos': ESTADOS_VALIDOS
            }
        )

    tarea = db.query(Tarea).filter_by(id=tarea_id).first()

    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')

    proyecto = db.query(Proyecto).filter_by(id=tarea.proyecto_id).first()
    if not proyecto:
        raise HTTPException(500, 'Proyecto asociado a la tarea no encontrado')

    if not (tarea.asignado_id == usuario.id or proyecto.propietario_id == usuario.id or usuario.es_admin):
        raise HTTPException(
            status_code=403,
            detail='No tienes permiso para cambiar el estado de esta tarea'
        )

    tarea.estado = nuevo_estado

    db.commit()
    db.refresh(tarea)

    return tarea

# ── DELETE /tareas/{id} ───────────────────────────────────────────────
@router.delete(
    '/{tarea_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Eliminar una tarea',
    description='Elimina permanentemente una tarea de la base de datos. Esta operación no se puede deshacer.'
)
def eliminar(
    tarea_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()

    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')

    proyecto = db.query(Proyecto).filter_by(id=tarea.proyecto_id).first()
    if not proyecto:
        raise HTTPException(500, 'Proyecto asociado a la tarea no encontrado')

    if not (proyecto.propietario_id == usuario.id or usuario.es_admin):
        raise HTTPException(
            status_code=403,
            detail='No tienes permiso para eliminar esta tarea'
        )

    db.delete(tarea)
    db.commit()
