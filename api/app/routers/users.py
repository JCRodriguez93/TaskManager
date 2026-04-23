# api/app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Usuario, Proyecto
from app.schemas import UsuarioResponse, ProyectoResponse

router = APIRouter(prefix='/usuarios', tags=['Usuarios'])


@router.get(
    '/',
    response_model=List[UsuarioResponse],
    summary='Listar usuarios activos',
    description='Obtiene una lista de todos los usuarios marcados como activos en el sistema. Útil para poblar selectores de asignación de tareas.'
)
def listar(db: Session = Depends(get_db)):
    return db.query(Usuario).filter_by(activo=True).all()


@router.get(
    '/{usuario_id}',
    response_model=UsuarioResponse,
    summary='Obtener un usuario',
    description='Recupera la información detallada de un usuario específico mediante su ID.'
)
def obtener(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()

    if not usuario:
        raise HTTPException(404, 'Usuario no encontrado')

    return usuario


@router.get(
    '/{usuario_id}/proyectos',
    response_model=List[ProyectoResponse],
    summary='Proyectos de un usuario',
    description='Lista todos los proyectos de los que el usuario especificado es propietario.'
)
def proyectos_de_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()

    if not usuario:
        raise HTTPException(404, 'Usuario no encontrado')

    return db.query(Proyecto).filter_by(propietario_id=usuario_id).all()