# web/app/routes/tasks.py — versión con APIClient
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.forms import TareaForm
from app.api_client import APIClient, APIError

tasks = Blueprint('tasks', __name__)


@tasks.route('/proyectos/<int:pid>/tareas/nueva', methods=['GET', 'POST'])
@login_required
def nueva(pid):
    try:
        proyecto = APIClient.get(f'/proyectos/{pid}')
    except APIError as e:
        flash(e.mensaje, 'error')
        return redirect(url_for('projects.lista'))

    form = TareaForm()

    if form.validate_on_submit():
        try:
            APIClient.post(f'/proyectos/{pid}/tareas', {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data or '',
                'prioridad': form.prioridad.data,
                'estado': form.estado.data,
                'fecha_limite': str(form.fecha_limite.data) if form.fecha_limite.data else None,
                'proyecto_id': pid,
                'asignado_id': current_user.id
            })

            flash('Tarea creada.', 'success')
            return redirect(url_for('projects.detalle', pid=pid))

        except APIError as e:
            flash(e.mensaje, 'error')

    return render_template(
        'tasks/form.html',
        form=form,
        proyecto=proyecto,
        titulo_pagina='Nueva tarea'
    )


@tasks.route('/proyectos/<int:pid>/tareas/<int:tid>/editar', methods=['GET', 'POST'])
@login_required
def editar(pid, tid):
    try:
        proyecto = APIClient.get(f'/proyectos/{pid}')
        tarea = APIClient.get(f'/tareas/{tid}')
    except APIError as e:
        flash(e.mensaje, 'error')
        return redirect(url_for('projects.lista'))

    form = TareaForm(data=tarea)

    if form.validate_on_submit():
        try:
            APIClient.patch(f'/tareas/{tid}', {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'prioridad': form.prioridad.data,
                'estado': form.estado.data,
                'fecha_limite': str(form.fecha_limite.data) if form.fecha_limite.data else None,
            })

            flash('Tarea actualizada.', 'success')
            return redirect(url_for('projects.detalle', pid=pid))

        except APIError as e:
            flash(e.mensaje, 'error')

    return render_template(
        'tasks/form.html',
        form=form,
        proyecto=proyecto,
        titulo_pagina='Editar tarea'
    )


@tasks.route('/proyectos/<int:pid>/tareas/<int:tid>/eliminar', methods=['POST'])
@login_required
def eliminar(pid, tid):
    try:
        APIClient.delete(f'/tareas/{tid}')
        flash('Tarea eliminada.', 'success')
    except APIError as e:
        flash(e.mensaje, 'error')

    return redirect(url_for('projects.detalle', pid=pid))


@tasks.route('/mis-tareas')
@login_required
def mis_tareas():
    try:
        tareas = APIClient.get('/tareas/', params={
            'asignado_id': current_user.id
        })

        return render_template('tasks/lista.html', tareas=tareas)

    except APIError as e:
        flash(e.mensaje, 'error')
        return redirect(url_for('main.index'))
