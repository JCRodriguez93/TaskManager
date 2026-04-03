# web/app/routes/main.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Proyecto, Tarea

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    # Filtrar proyectos según usuario o admin
    if current_user.es_admin:
        proyectos = Proyecto.query.all()
    else:
        proyectos = Proyecto.query.filter_by(propietario_id=current_user.id).all()

    proyectos_activos = []
    tareas_urgentes = []

    for p in proyectos:
        total = p.tareas.count()
        completadas = p.tareas.filter_by(estado='completada').count()
        pendientes = total - completadas
        proyectos_activos.append({
            'titulo': p.titulo,
            'tareas_total': total,
            'completadas': completadas
        })
        # Tareas urgentes
        urgentes = p.tareas.filter(Tarea.prioridad.in_(['urgente', 'alta'])).all()
        for t in urgentes:
            tareas_urgentes.append({
                'titulo': t.titulo,
                'proyecto': p.titulo,
                'prioridad': t.prioridad
            })

    total_pendientes = sum(p['tareas_total'] - p['completadas'] for p in proyectos_activos)

    return render_template(
        'index.html',
        tareas_urgentes=tareas_urgentes,
        proyectos_activos=proyectos_activos,
        total_proyectos=len(proyectos_activos),
        total_pendientes=total_pendientes,
    )