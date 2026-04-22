# web/app/routes/projects.py — versión con base de datos
from flask import Blueprint, render_template, flash, redirect, url_for, \
    request, abort
from app import db
from app.models import Proyecto, Tarea
from app.forms import ProyectoForm, BusquedaForm

projects = Blueprint('projects', __name__, url_prefix='/proyectos')
from flask_login import login_required, current_user


@projects.route('/')
@login_required
def lista():
    q = request.args.get('q', '').strip()
    pagina = request.args.get('pagina', 1, type=int)

    # Los admins ven todos los proyectos; los usuarios normales solo los suyos
    if current_user.es_admin:
        query = Proyecto.query
    else:
        query = Proyecto.query.filter_by(propietario_id=current_user.id)

    if q:
        query = query.filter(
            db.or_(
                Proyecto.titulo.ilike(f'%{q}%'),
                Proyecto.descripcion.ilike(f'%{q}%')
            )
        )

    paginacion = query.order_by(Proyecto.creado_en.desc()) \
        .paginate(page=pagina, per_page=10, error_out=False)

    return render_template(
        'projects/lista.html',
        proyectos=paginacion.items,
        paginacion=paginacion,
        q=q,
        form_busqueda=BusquedaForm()
    )


@projects.route('/<int:pid>')
@login_required
def detalle(pid):
    proyecto = Proyecto.query.get_or_404(pid)
    tareas = proyecto.tareas.order_by(Tarea.creado_en.desc()).all()
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
        proyecto = Proyecto(
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            fecha_limite=form.fecha_limite.data,
            propietario_id = current_user.id # ← Usar el usuario autenticado
        )
        db.session.add(proyecto)
        db.session.commit()
        flash(f'Proyecto "{proyecto.titulo}" creado.', 'success')
        return redirect(url_for('projects.lista'))
    return render_template(
        'projects/form.html',
        form=form,
        titulo_pagina='Nuevo proyecto'
    )


@projects.route('/<int:pid>/editar', methods=['GET', 'POST'])
@login_required
def editar(pid):
    proyecto = Proyecto.query.get_or_404(pid)

    # Verificar que el usuario tiene permiso sobre este proyecto
    if proyecto.propietario_id != current_user.id and not current_user.es_admin:
        abort(403)  # Prohibido — devuelve la página de error 403

    form = ProyectoForm(obj=proyecto)

    if form.validate_on_submit():
        form.populate_obj(proyecto)
        db.session.commit()

        flash('Proyecto actualizado.', 'success')
        return redirect(url_for('projects.detalle', pid=pid))

    return render_template(
        'projects/form.html',
        form=form,
        titulo_pagina=f'Editar: {proyecto.titulo}'
    )


# Solo el propietario o un admin puede eliminar su proyecto
@projects.route('/<int:pid>/eliminar', methods=['POST'])
@login_required
def eliminar(pid):
    proyecto = Proyecto.query.get_or_404(pid)

    # Verificar propiedad manualmente (más claro que un decorador genérico)
    if proyecto.propietario_id != current_user.id and not current_user.es_admin:
        abort(403)

    db.session.delete(proyecto)
    db.session.commit()

    flash('Proyecto eliminado.', 'success')
    return redirect(url_for('projects.lista'))