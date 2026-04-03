# web/app/routes/tasks.py
from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from app import db
from app.models import Proyecto, Tarea
from app.forms import TareaForm
from flask_login import login_required, current_user

tasks = Blueprint('tasks', __name__)

@tasks.route('/proyectos/<int:pid>/tareas/nueva', methods=['GET', 'POST'])
@login_required
def nueva(pid):
    proyecto = Proyecto.query.get_or_404(pid)
    if proyecto.propietario_id != current_user.id and not current_user.es_admin:
        abort(403)
    form = TareaForm()

    if form.validate_on_submit():
        nueva_tarea = Tarea(
            titulo=form.titulo.data,
            descripcion=form.descripcion.data or '',
            prioridad=form.prioridad.data,
            estado=form.estado.data,
            fecha_limite=form.fecha_limite.data,
            proyecto_id=pid
        )

        db.session.add(nueva_tarea)
        db.session.commit()

        flash(f'Tarea "{nueva_tarea.titulo}" creada.', 'success')
        return redirect(url_for('projects.detalle', pid=pid))

    return render_template(
        'tasks/form.html',
        form=form,
        proyecto=proyecto,
        titulo_pagina=f'Nueva tarea en {proyecto.titulo}'
    )

@tasks.route('/proyectos/<int:pid>/tareas/<int:tid>/editar', methods=['GET', 'POST'])
@login_required
def editar(pid, tid):
    proyecto = Proyecto.query.get_or_404(pid)
    if proyecto.propietario_id != current_user.id and not current_user.es_admin:
        abort(403)
    tarea = Tarea.query.get_or_404(tid)

    if tarea.proyecto_id != pid:
        abort(404)

    form = TareaForm(obj=tarea)

    if form.validate_on_submit():
        form.populate_obj(tarea)
        db.session.commit()

        flash('Tarea actualizada.', 'success')
        return redirect(url_for('projects.detalle', pid=pid))

    return render_template(
        'tasks/form.html',
        form=form,
        proyecto=proyecto,
        titulo_pagina='Editar tarea'
    )

@tasks.route('/proyectos/<int:pid>/tareas/<int:tid>/eliminar', methods=['POST'])
@login_required
def eliminar(pid, tid):
    proyecto = Proyecto.query.get_or_404(pid)
    if proyecto.propietario_id != current_user.id and not current_user.es_admin:
        abort(403)
    tarea = Tarea.query.get_or_404(tid)

    if tarea.proyecto_id != pid:
        abort(404)

    db.session.delete(tarea)
    db.session.commit()

    flash('Tarea eliminada.', 'success')
    return redirect(url_for('projects.detalle', pid=pid))

@login_required
@tasks.route('/mis-tareas')
def mis_tareas():
    # Si admin, ve todas las tareas; si no, solo de sus proyectos
    if current_user.es_admin:
        tareas = Tarea.query.all()
    else:
        tareas = Tarea.query.join(Proyecto).filter(Proyecto.propietario_id == current_user.id).all()

    # Ordenar por prioridad
    orden = {'urgente': 0, 'alta': 1, 'media': 2, 'baja': 3}
    tareas = sorted(tareas, key=lambda t: orden.get(t.prioridad, 99))

    return render_template('tasks/lista.html', tareas=tareas)
