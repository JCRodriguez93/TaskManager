# api/main.py — versión completa

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import projects, tasks, estadisticas
import logging
import traceback

logging.basicConfig(
    filename='errores.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


app = FastAPI(
    title='TaskManager API',
    description='''
## API REST para TaskManager
Gestiona proyectos, tareas y usuarios.
La documentación completa está disponible en /docs.
''',
    version='1.0.0'
)

# api/main.py — añadir después de crear la instancia app
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

app = FastAPI(title='TaskManager API', version='1.0.0')

# ── Manejador para errores de validación Pydantic (422) ──────────────
# Se activa cuando el cliente envía datos con tipos incorrectos o
# campos obligatorios que faltan.
@app.exception_handler(RequestValidationError)
async def error_validacion(request: Request, exc: RequestValidationError):
    errores = []

    for error in exc.errors():
        # loc es la localización del error (campo, índice de lista, etc.)
        campo = ' → '.join(str(parte) for parte in error['loc'][1:])
        errores.append({
            'campo': campo or 'body',
            'mensaje': error['msg'],
            'tipo': error['type']
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'error': 'Error de validación',
            'detalle': errores
        }
    )

# ── Manejador para errores de integridad de BD (409) ──────────────────
# Se activa cuando se viola una restricción de la BD
# (email duplicado, violación de clave única, etc.).
@app.exception_handler(IntegrityError)
async def error_integridad(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            'error': 'Conflicto de datos',
            'detalle': 'Un registro con esos datos ya existe'
        }
    )

# ── Manejador para errores internos del servidor (500) ─────────────────
# Última línea de defensa: captura cualquier excepción no manejada.
@app.exception_handler(Exception)
async def error_interno(request: Request, exc: Exception):
    # En producción: registrar el error en los logs (no mostrarlo al cliente)
    # Guardar en archivo log
    traza = traceback.format_exc()
    logging.error(f"""
        URL: {request.url}
        Método: {request.method}
        Error: {str(exc)}
        Traceback:
        {traza}
        """)
    # import logging; logging.error(f'Error inesperado: {exc}')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'error': 'Error interno del servidor'}
    )

# CORS: permitir peticiones desde el frontend Flask (puerto 5000)
# Sin esto, el navegador bloqueará las peticiones de Flask a FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5000',
        'http://127.0.0.1:5000',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Registrar routers con prefijo de versión en la URL
app.include_router(projects.router, prefix='/api/v1')
app.include_router(tasks.router, prefix='/api/v1')
app.include_router(estadisticas.router, prefix="/api/v1")


@app.get('/', tags=['Estado'])
def root():
    return {
        'mensaje': 'TaskManager API v1.0',
        'documentacion': '/docs'
    }


@app.get('/health', tags=['Estado'])
def health():
    return {'status': 'ok'}
