# api/app/routers/projects.py — versión completa
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Proyecto, Usuario
from app.schemas import (
    ProyectoCreate, ProyectoUpdate,
    ProyectoResponse, RespuestaPaginada
)
from app.security import get_current_user, require_admin

router = APIRouter(prefix='/proyectos', tags=['Proyectos'])

# ── GET /proyectos/ — Listar con filtros y paginación ────────────────
@router.get(
    '/',
    response_model=RespuestaPaginada[ProyectoResponse],
    summary='Listar proyectos',
    description='Obtiene una lista paginada de proyectos, con opciones de filtrado por título, descripción y estado.'
)
def listar(
    pagina: int = Query(1, ge=1, description='Número de página a recuperar (mínimo 1)'),
    tamano: int = Query(10, ge=1, le=100, description='Cantidad de proyectos por página (máximo 100)'),
    q: Optional[str] = Query(None, description='Buscar en título y descripción'),
    estado: Optional[str] = Query(None, description='activo | pausado | completado'),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    """
    Listar proyectos. Si el usuario no es admin, solo devuelve sus proyectos.
    El cliente debe enviar el JWT en Authorization; get_current_user lo valida.
    """
    query = db.query(Proyecto)

    # Si el usuario no es admin, limitar a sus proyectos
    if not usuario.es_admin:
        query = query.filter_by(propietario_id=usuario.id)

    if q:
        query = query.filter(
            Proyecto.titulo.ilike(f'%{q}%') |
            Proyecto.descripcion.ilike(f'%{q}%')
        )

    if estado:
        query = query.filter_by(estado=estado)

    total = query.count()

    items = query.order_by(Proyecto.creado_en.desc()) \
        .offset((pagina - 1) * tamano) \
        .limit(tamano) \
        .all()

    return RespuestaPaginada(
        total=total,
        pagina=pagina,
        paginas=(total + tamano - 1) // tamano,
        items=items
    )

# ── GET /proyectos/{id} — Detalle ────────────────────────────────────
@router.get(
    '/{proyecto_id}',
    response_model=ProyectoResponse,
    summary='Obtener un proyecto',
    description='Obtiene los detalles de un proyecto específico por su ID.'
)
def obtener(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()

    if not proyecto:
        raise HTTPException(
            status_code=404,
            detail=f'No existe ningún proyecto con ID {proyecto_id}'
        )

    return proyecto

# ── POST /proyectos/ — Crear ──────────────────────────────────────────
# status_code=201 porque creamos un nuevo recurso
@router.post(
    '/',
    response_model=ProyectoResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Crear un proyecto',
    description='Crea un nuevo proyecto con el título, descripción y fecha límite proporcionados.'
)
def crear(
    datos: ProyectoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    # Verificar que no existe otro proyecto con el mismo título (opcional)
    existente = db.query(Proyecto).filter(
        Proyecto.titulo.ilike(datos.titulo)
    ).first()

    if existente:
        raise HTTPException(
            status_code=409,
            detail='Ya existe un proyecto con ese título'
        )

    proyecto = Proyecto(
        titulo=datos.titulo.strip(),
        descripcion=datos.descripcion,
        fecha_limite=datos.fecha_limite,
        propietario_id=usuario.id
    )

    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)  # Recargar para obtener id y creado_en asignados por la BD

    return proyecto

# ── PUT /proyectos/{id} — Actualizar completo ─────────────────────────
@router.put(
    '/{proyecto_id}',
    response_model=ProyectoResponse,
    summary='Actualizar un proyecto completo',
    description='Actualiza completamente un proyecto existente. Todos los campos editables deben ser proporcionados.'
)
def actualizar(
    proyecto_id: int,
    datos: ProyectoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()

    if not proyecto:
        raise HTTPException(status_code=404, detail='Proyecto no encontrado')

    if proyecto.propietario_id != usuario.id and not usuario.es_admin:
        raise HTTPException(
            status_code=403,
            detail='No tienes permiso para editar este proyecto'
        )

    # PUT reemplaza todos los campos editables
    proyecto.titulo = datos.titulo.strip()
    proyecto.descripcion = datos.descripcion
    proyecto.fecha_limite = datos.fecha_limite

    db.commit()
    db.refresh(proyecto)

    return proyecto

# ── PATCH /proyectos/{id} — Actualizar parcial ────────────────────────
@router.patch(
    '/{proyecto_id}',
    response_model=ProyectoResponse,
    summary='Actualizar campos específicos de un proyecto',
    description='Actualiza uno o más campos de un proyecto existente. Solo los campos proporcionados serán modificados.'
)
def actualizar_parcial(
    proyecto_id: int,
    datos: ProyectoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()

    if not proyecto:
        raise HTTPException(status_code=404, detail='Proyecto no encontrado')

    if proyecto.propietario_id != usuario.id and not usuario.es_admin:
        raise HTTPException(
            status_code=403,
            detail='No tienes permiso para editar este proyecto'
        )

    # exclude_unset=True: solo procesar los campos que el cliente envió explícitamente.
    datos_a_actualizar = datos.model_dump(exclude_unset=True)

    for campo, valor in datos_a_actualizar.items():
        setattr(proyecto, campo, valor)

    db.commit()
    db.refresh(proyecto)

    return proyecto

# ── DELETE /proyectos/{id} — Eliminar ─────────────────────────────────
# status_code=204: éxito sin cuerpo en la respuesta
@router.delete(
    '/{proyecto_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Eliminar un proyecto',
    description='Elimina un proyecto existente por su ID. Esto también eliminará todas las tareas asociadas al proyecto.'
)
def eliminar(
    proyecto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()

    if not proyecto:
        raise HTTPException(status_code=404, detail='Proyecto no encontrado')

    if proyecto.propietario_id != usuario.id and not usuario.es_admin:
        raise HTTPException(
            status_code=403,
            detail='No tienes permiso para eliminar este proyecto'
        )

    db.delete(proyecto)
    db.commit()
    # No devolvemos nada: 204 No Content

# ── GET /proyectos/{id}/tareas ────────────────────────────────────────
from app.schemas import TareaResponse, TareaCreate
from app.models import Tarea

# ── GET /proyectos/{id}/tareas ────────────────────────────────────────
@router.get(
    '/{proyecto_id}/tareas',
    response_model=List[TareaResponse],
    tags=['Proyectos', 'Tareas'],  # Aparece en ambas secciones de Swagger
    summary='Tareas de un proyecto',
    description='Obtiene una lista de tareas asociadas a un proyecto específico, con opciones de filtrado por estado y prioridad.'
)
def tareas_del_proyecto(
    proyecto_id: int,
    estado: Optional[str] = Query(None, description='Filtrar tareas por estado (pendiente, en_progreso, revision, completada)'),
    prioridad: Optional[str] = Query(None, description='Filtrar tareas por prioridad (baja, media, alta, urgente)'),
    db: Session = Depends(get_db)
):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()

    if not proyecto:
        raise HTTPException(404, 'Proyecto no encontrado')

    query = db.query(Tarea).filter_by(proyecto_id=proyecto_id)

    if estado:
        query = query.filter_by(estado=estado)

    if prioridad:
        query = query.filter_by(prioridad=prioridad)

    return query.order_by(Tarea.creado_en.desc()).all()

# ── POST /proyectos/{id}/tareas ───────────────────────────────────────
@router.post(
    '/{proyecto_id}/tareas',
    response_model=TareaResponse,
    status_code=status.HTTP_201_CREATED,
    tags=['Proyectos', 'Tareas'],
    summary='Crear tarea en un proyecto',
    description='Crea una nueva tarea y la asocia a un proyecto existente.'
)
def crear_tarea_en_proyecto(
    proyecto_id: int,
    datos: TareaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()

    if not proyecto:
        raise HTTPException(404, 'Proyecto no encontrado')

    if proyecto.propietario_id != usuario.id and not usuario.es_admin:
        raise HTTPException(
            status_code=403,
            detail='No tienes permiso para crear tareas en este proyecto'
        )


    # Sobrescribir el proyecto_id del schema con el de la URL
    # (tienen que coincidir para mantener la consistencia)
    tarea_data = datos.model_dump()
    tarea_data['proyecto_id'] = proyecto_id

    tarea = Tarea(**tarea_data)

    db.add(tarea)
    db.commit()
    db.refresh(tarea)

    return tarea
