# TaskManager

Aplicación TaskManager de la asignatura 'Optativa' (Python) - tarea 01

## Tecnologías

### ===== WEB =====

| Package           | Version |
|------------------|---------|
| blinker           | 1.9.0   |
| click             | 8.3.1   |
| colorama          | 0.4.6   |
| Flask             | 3.1.3   |
| greenlet          | 3.3.2   |
| itsdangerous      | 2.2.0   |
| Jinja2            | 3.1.6   |
| MarkupSafe        | 3.0.3   |
| SQLAlchemy        | 2.0.48  |
| typing_extensions | 4.15.0  |
| Werkzeug          | 3.1.6   |
| WTForms           | 3.2.1   |

### ===== API =====

| Package             | Version |
|--------------------|---------|
| annotated-doc       | 0.0.4   |
| annotated-types     | 0.7.0   |
| anyio               | 4.12.1  |
| click               | 8.3.1   |
| colorama            | 0.4.6   |
| fastapi             | 0.135.2 |
| h11                 | 0.16.0  |
| idna                | 3.11    |
| pydantic            | 2.12.5  |
| pydantic_core       | 2.41.5  |
| starlette           | 1.0.0   |
| typing-inspection   | 0.4.2   |
| typing_extensions   | 4.15.0  |
| uvicorn             | 0.42.0  |

## Arquitectura

### web
El servicio Flask: sirve las páginas HTML que el usuario ve en el navegador.
Gestiona las sesiones (quién está conectado), renderiza los formularios y muestra los
datos en plantillas HTML. Es el 'frontend' del lado del servidor.
### api
El servicio FastAPI: expone los datos en formato JSON a través de endpoints
REST. No genera HTML: solo recibe peticiones y devuelve datos. Lo puede consumir el
frontend Flask, una app móvil, o cualquier otro cliente.

## Requisitos

* Python 3.11.x o superior
* pip 23.2.1
* git version 2.52.0

## Instalación

### Estructura del servicio Flask (web/)
```powershell
md web/app/routes
md web/app/templates/auth
md web/app/templates/projects
md web/app/templates/tasks
md web/app/templates/errores
md web/app/static/css
md web/app/static/js

ni web/app/__init__.py, web/app/models.py, web/app/forms.py
ni web/app/routes/__init__.py, web/app/routes/main.py
ni web/app/routes/auth.py, web/app/routes/projects.py, web/app/routes/tasks.py
ni web/config.py, web/run.py, web/requirements.txt
```
### Estructura del servicio FastAPI (api/)
```powershell

md api/app/routers

ni api/app/__init__.py, api/app/models.py, api/app/schemas.py
ni api/app/database.py, api/app/security.py
ni api/app/routers/auth.py, api/app/routers/projects.py, api/app/routers/tasks.py
ni api/main.py, api/requirements.txt
```
