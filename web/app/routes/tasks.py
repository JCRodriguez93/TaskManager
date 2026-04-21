
# web/app/routes/tasks.py
from flask import Blueprint, render_template
from app.routes.projects import PROYECTOS_PRUEBA
tasks = Blueprint('tasks', __name__)

tasks = Blueprint('tasks', __name__, url_prefix='/tareas')

ORDEN = {'urgente': 0, 'alta': 1, 'media': 2, 'baja': 3}

@tasks.route('/')
def mis_tareas():
    
    todas = []
    for p in PROYECTOS_PRUEBA:
        for t in p['tareas']:
            t = t.copy()
            t['proyecto'] = p['titulo']
            todas.append(t)

    todas.sort(key=lambda t: ORDEN.get(t['prioridad'], 99))

    return render_template('tasks/lista.html', tareas=todas)