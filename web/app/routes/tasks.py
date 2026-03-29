# web/app/routes/tasks.py
from flask import Blueprint, render_template
from app.routes.projects import PROYECTOS_PRUEBA

tasks = Blueprint('tasks', __name__, url_prefix='/tareas')

ORDEN = {'urgente': 0, 'alta': 1, 'media': 2, 'baja': 3}

@tasks.route('/')
def mis_tareas():
    # 1. Recopilar todas las tareas de todos los proyectos
    todas = []
    for p in PROYECTOS_PRUEBA:
        for t in p['tareas']:
            # Añadimos el nombre del proyecto a cada tarea
            t = t.copy()
            t['proyecto'] = p['titulo']
            todas.append(t)

    # 2. Ordenar por prioridad
    todas.sort(key=lambda t: ORDEN.get(t['prioridad'], 99))

    # 3. Renderizar la plantilla correcta
    return render_template('tasks/lista.html', tareas=todas)
