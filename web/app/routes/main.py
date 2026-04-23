# web/app/routes/main.py

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Proyecto, Tarea, Usuario
from sqlalchemy import case
# Uso de los decoradores en las rutas:
from app.decoradores import solo_admin
from app import db
from app.forms import EditarPerfilForm

main = Blueprint('main', __name__)


@main.route('/')
@login_required
def index():
    # Proyectos del usuario autenticado
    mis_proyectos = (
        Proyecto.query
        .filter_by(propietario_id=current_user.id)
        .order_by(Proyecto.creado_en.desc())
        .all()
    )

    # Orden por prioridad
    orden_prioridad = case(
        (Tarea.prioridad == 'urgente', 0),
        (Tarea.prioridad == 'alta', 1),
        (Tarea.prioridad == 'media', 2),
        else_=3
    )

    # Tareas asignadas al usuario, ordenadas por prioridad
    mis_tareas_urgentes = (
        Tarea.query
        .filter_by(asignado_id=current_user.id)
        .filter(Tarea.estado != 'completada')
        .order_by(orden_prioridad)
        .limit(5)
        .all()
    )

    # Estadísticas personalizadas
    stats = {
        'total_proyectos': len(mis_proyectos),
        'proyectos_activos': sum(
            1 for p in mis_proyectos if p.estado == 'activo'
        ),
        'tareas_pendientes': (
            Tarea.query
            .join(Proyecto)
            .filter(Proyecto.propietario_id == current_user.id)
            .filter(Tarea.estado != 'completada')
            .count()
        ),
        'tareas_completadas': (
            Tarea.query
            .join(Proyecto)
            .filter(Proyecto.propietario_id == current_user.id)
            .filter(Tarea.estado == 'completada')
            .count()
        ),
    }

    return render_template(
        'index.html',
        mis_proyectos=mis_proyectos,
        mis_tareas_urgentes=mis_tareas_urgentes,
        stats=stats
    )



# Solo admins pueden acceder al panel de administración
@main.route('/admin')
@login_required
@solo_admin
def admin():

    todos_proyectos = (
        Proyecto.query
        .order_by(Proyecto.creado_en.desc())
        .all()
    )

    todos_usuarios = (
        Usuario.query
        .order_by(Usuario.creado_en.desc())
        .all()
    )

    stats = {
        'total_proyectos': Proyecto.query.count(),
        'total_tareas': Tarea.query.count(),
        'usuarios_activos': Usuario.query.filter_by(activo=True).count()
    }

    return render_template(
        'admin/panel.html',
        proyectos=todos_proyectos,
        usuarios=todos_usuarios,
        stats=stats
    )

@main.route('/admin/usuarios/<int:id>/toggle-activo', methods=['POST'])
@login_required
@solo_admin
def toggle_activo(id):
    usuario = Usuario.query.get_or_404(id)

    # Evitar que un admin se desactive a sí mismo (por si las moscas)
    if usuario.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta.', 'error')
        return redirect(url_for('main.admin'))

    # cambiar el estado activo del usuario
    usuario.activo = not usuario.activo
    db.session.commit()

    flash('Estado del usuario actualizado.', 'success')
    return redirect(url_for('main.admin'))

@main.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    usuario = current_user
    form = EditarPerfilForm()

    if request.method == "GET":
        form.nombre.data = usuario.nombre
        form.email.data = usuario.email

    if form.validate_on_submit():

        if not usuario.check_password(form.password_actual.data):
            flash("La contraseña actual es incorrecta.", "error")
            return redirect(url_for("main.perfil"))

        if form.email.data != usuario.email:
            existe = Usuario.query.filter_by(email=form.email.data).first()
            if existe:
                flash("Ese email ya está en uso.", "error")
                return redirect(url_for("main.perfil"))

        usuario.nombre = form.nombre.data
        usuario.email = form.email.data

        if form.password_nuevo.data:
            usuario.set_password(form.password_nuevo.data)

        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("main.perfil"))

    stats = {
        "proyectos_creados": Proyecto.query.filter_by(
            propietario_id=usuario.id
        ).count(),
        "tareas_completadas": Tarea.query.join(Proyecto)
        .filter(Proyecto.propietario_id == usuario.id, Tarea.estado == "completada")
        .count(),
    }

    return render_template("perfil.html", usuario=usuario, stats=stats, form=form)
