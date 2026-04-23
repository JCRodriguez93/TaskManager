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
    descripcion: Optional[str] = Field(
        None,
        max_length=500,
        description='Descripción detallada del propósito y alcance del proyecto'
    )
    fecha_limite: Optional[date] = Field(
        None,
        description='Fecha estimada de finalización del proyecto'
    )


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
    titulo: Optional[str] = Field(None, min_length=3, max_length=100, description='Nuevo título del proyecto')
    descripcion: Optional[str] = Field(None, description='Nueva descripción del proyecto')
    estado: Optional[str] = Field(
        None,
        description='Estado del proyecto: activo, pausado o completado'
    )
    fecha_limite: Optional[date] = Field(
        None,
        description='Nueva fecha límite del proyecto'
    )


class ProyectoResponse(ProyectoBase):
    """Schema para la respuesta con campos calculados/BD."""

    id: int = Field(..., description='ID único del proyecto en la base de datos')
    estado: str = Field(..., description='Estado actual del proyecto')
    creado_en: datetime = Field(..., description='Fecha y hora de creación')
    propietario_id: int = Field(..., description='ID del usuario propietario del proyecto')
    progreso: int = Field(0, description='Porcentaje de progreso calculado basado en tareas completadas')

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
    descripcion: Optional[str] = Field(
        None,
        max_length=500,
        description='Detalles sobre lo que se debe realizar en esta tarea'
    )
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
    fecha_limite: Optional[date] = Field(
        None,
        description='Fecha límite para completar la tarea'
    )


class TareaCreate(TareaBase):
    proyecto_id: int = Field(..., description='ID del proyecto al que pertenece la tarea')
    asignado_id: Optional[int] = Field(None, description='ID del usuario asignado a la tarea')

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
    titulo: Optional[str] = Field(None, description='Nuevo título de la tarea')
    descripcion: Optional[str] = Field(None, description='Nueva descripción de la tarea')
    prioridad: Optional[str] = Field(
        None,
        description='Nueva prioridad: baja, media, alta o urgente'
    )
    estado: Optional[str] = Field(
        None,
        description='Nuevo estado: pendiente, en_progreso, revision o completada'
    )
    asignado_id: Optional[int] = Field(None, description='ID del usuario al que se le asigna la tarea')
    fecha_limite: Optional[date] = Field(
        None,
        description='Nueva fecha límite de la tarea'
    )


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
    total: int = Field(..., description='Total de registros encontrados')
    pagina: int = Field(..., description='Página actual')
    paginas: int = Field(..., description='Total de páginas disponibles')
    items: List[T] = Field(..., description='Lista de elementos de la página actual')

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

# api/app/schemas.py — añadir
from pydantic import BaseModel

class TokenResponse(BaseModel):
    """Respuesta del endpoint de login."""
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RefreshRequest(BaseModel):
    """Petición para renovar el access token."""
    refresh_token: str


class AccessTokenResponse(BaseModel):
    """Respuesta del endpoint de refresh."""
    access_token: str
    token_type: str = 'bearer'