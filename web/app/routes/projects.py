# web/app/routes/projects.py — versión con APIClient
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.forms import ProyectoForm, BusquedaForm
from app.api_client import APIClient, APIError, manejar_api_error

projects = Blueprint('projects', __name__, url_prefix='/proyectos')

# No tiene sentido que si le quito el filtro del autor o el administrador, 
# el usuario vea proyectos de otros usuarios. 
# Pero esto pide la tarea que se copie.

@projects.route('/')
@login_required
@manejar_api_error('main.index')
def lista():
    q = request.args.get('q', '').strip()
    pagina = request.args.get('pagina', 1, type=int)

    params = {'pagina': pagina, 'tamano': 10}

    if q:
        params['q'] = q

    # Llamada a la API — devuelve el objeto RespuestaPaginada como dict
    respuesta = APIClient.get('/proyectos/', params=params)

    return render_template(
        'projects/lista.html',
        proyectos=respuesta['items'],
        paginacion=respuesta,
        q=q,
        form_busqueda=BusquedaForm()
    )


@projects.route('/<int:pid>')
@login_required
@manejar_api_error('projects.lista')
def detalle(pid):
    proyecto = APIClient.get(f'/proyectos/{pid}')
    tareas = APIClient.get(f'/proyectos/{pid}/tareas')

    return render_template(
        'projects/detalle.html',
        proyecto=proyecto,
        tareas=tareas
    )


@projects.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    form = ProyectoForm()

    if form.validate_on_submit():
        try:
            proyecto = APIClient.post('/proyectos/', {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'fecha_limite': str(form.fecha_limite.data) if form.fecha_limite.data else None
            })

            flash(f'Proyecto "{proyecto["titulo"]}" creado.', 'success')
            return redirect(url_for('projects.lista'))

        except APIError as e:
            flash(e.mensaje, 'error')

    return render_template(
        'projects/form.html',
        form=form,
        titulo_pagina='Nuevo proyecto'
    )


@projects.route('/<int:pid>/editar', methods=['GET', 'POST'])
@login_required
def editar(pid):
    try:
        proyecto = APIClient.get(f'/proyectos/{pid}')
    except APIError as e:
        flash(e.mensaje, 'error')
        return redirect(url_for('projects.lista'))

    # Pre-rellenar el formulario con los datos actuales del proyecto
    form = ProyectoForm(data=proyecto)

    if form.validate_on_submit():
        try:
            APIClient.patch(f'/proyectos/{pid}', {
                'titulo': form.titulo.data,
                'descripcion': form.descripcion.data,
                'fecha_limite': str(form.fecha_limite.data) if form.fecha_limite.data else None
            })

            flash('Proyecto actualizado.', 'success')
            return redirect(url_for('projects.detalle', pid=pid))

        except APIError as e:
            flash(e.mensaje, 'error')

    return render_template(
        'projects/form.html',
        form=form,
        titulo_pagina=f'Editar: {proyecto["titulo"]}'
    )


@projects.route('/<int:pid>/eliminar', methods=['POST'])
@login_required
def eliminar(pid):
    try:
        APIClient.delete(f'/proyectos/{pid}')
        flash('Proyecto eliminado.', 'success')
    except APIError as e:
        flash(e.mensaje, 'error')

    return redirect(url_for('projects.lista'))
