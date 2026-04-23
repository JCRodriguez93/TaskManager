# api/app/schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, TypeVar, Generic
from datetime import datetime, date

# ═══════════════════════════════════════════════════
# PROYECTO
# ═══════════════════════════════════════════════════

class ProyectoBase(BaseModel):
    """Campos comunes a todos los schemas de Proyecto."""

    titulo: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description='Título del proyecto'
    )
    descripcion: Optional[str] = Field(None, max_length=500)
    fecha_limite: Optional[date] = None


class ProyectoCreate(ProyectoBase):
    """Schema para crear un proyecto. Hereda de ProyectoBase."""
    model_config = {
        "json_schema_extra": {
            "example": {
                "titulo": "Rediseño de la intranet",
                "descripcion": "Actualizar la intranet corporativa con nuevas funcionalidades y una interfaz moderna.",
                "fecha_limite": "2025-12-31"
            }
        }
    }


class ProyectoUpdate(BaseModel):
    """Schema para actualizar un proyecto. Todos los campos son opcionales."""

    model_config = {
        "json_schema_extra": {
            "example": {
                "titulo": "Rediseño de la intranet (v2)",
                "descripcion": "Actualización de la intranet corporativa, fase 2: integración con CRM.",
                "estado": "en_progreso",
                "fecha_limite": "2026-06-30"
            }
        }
    }
    titulo: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    fecha_limite: Optional[date] = None


class ProyectoResponse(ProyectoBase):
    """Schema para la respuesta con campos calculados/BD."""

    id: int
    estado: str
    creado_en: datetime
    propietario_id: int
    progreso: int = 0  # calculado, no almacenado

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════
# TAREA
# ═══════════════════════════════════════════════════

class TareaBase(BaseModel):
    titulo: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description='Título de la tarea'
    )
    descripcion: Optional[str] = Field(None, max_length=500)
    prioridad: str = Field(
        'media',
        pattern='^(baja|media|alta|urgente)$',
        description='Nivel de prioridad de la tarea'
    )
    estado: str = Field(
        'pendiente',
        pattern='^(pendiente|en_progreso|revision|completada)$',
        description='Estado actual de la tarea'
    )
    fecha_limite: Optional[date] = None


class TareaCreate(TareaBase):
    proyecto_id: int
    asignado_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "titulo": "Desarrollar módulo de autenticación",
                "descripcion": "Implementar el sistema de login y registro de usuarios.",
                "prioridad": "alta",
                "estado": "en_progreso",
                "fecha_limite": "2024-07-15",
                "proyecto_id": 1,
                "asignado_id": 2
            }
        }
    }


class TareaUpdate(BaseModel):
    model_config = {
        "json_schema_extra": {
            "example": {
                "titulo": "Refactorizar módulo de autenticación",
                "prioridad": "urgente",
                "estado": "revision",
                "asignado_id": 3
            }
        }
    }
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    asignado_id: Optional[int] = None
    fecha_limite: Optional[date] = None


class TareaResponse(TareaBase):
    id: int
    proyecto_id: int
    asignado_id: Optional[int]
    creado_en: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════
# USUARIO
# ═══════════════════════════════════════════════════

class UsuarioCreate(BaseModel):
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description='Nombre completo del usuario'
    )
    email: EmailStr = Field(..., description='Correo electrónico único del usuario')
    password: str = Field(..., min_length=8, description='Contraseña del usuario (mínimo 8 caracteres)')

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan.perez@example.com",
                "password": "passwordSegura123"
            }
        }
    }


class UsuarioResponse(BaseModel):
    """Nunca incluir contraseña en respuestas."""

    id: int
    nombre: str
    email: str
    rol: str
    creado_en: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════
# RESPUESTA PAGINADA (genérica)
# ═══════════════════════════════════════════════════

T = TypeVar('T')


class RespuestaPaginada(BaseModel, Generic[T]):
    total: int
    pagina: int
    paginas: int
    items: List[T]

# ═══════════════════════════════════════════════════
# ESTADÍSTICAS
# ═══════════════════════════════════════════════════

class EstadisticasResponse(BaseModel):
    total_proyectos: int
    proyectos_activos: int
    proyectos_pausados: int
    total_tareas: int
    tareas_pendientes: int
    tareas_en_progreso: int
    tareas_completadas: int
    total_usuarios: int

    class Config:
        from_attributes = True