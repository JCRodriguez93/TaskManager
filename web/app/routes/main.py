# web/app/routes/main.py
from flask import Blueprint, render_template, flash, request, url_for, redirect
from flask_login import login_required, current_user
from app.models import Proyecto, Tarea
from app.models import Usuario
from app.decoradores import solo_admin
from app import db
from app.forms import EditarPerfilForm


main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():

    if current_user.es_admin:
        proyectos = Proyecto.query.all()
    else:
        proyectos = Proyecto.query.filter_by(propietario_id=current_user.id).all()

    proyectos_activos = []
    tareas_urgentes = []

    for p in proyectos:
        total = p.tareas.count()
        completadas = p.tareas.filter_by(estado="completada").count()

        proyectos_activos.append(
            {"titulo": p.titulo, "tareas_total": total, "completadas": completadas}
        )

        urgentes = p.tareas.filter(Tarea.prioridad.in_(["urgente", "alta"])).all()
        for t in urgentes:
            tareas_urgentes.append(
                {"titulo": t.titulo, "proyecto": p.titulo, "prioridad": t.prioridad}
            )

    total_pendientes = sum(
        p["tareas_total"] - p["completadas"] for p in proyectos_activos
    )

    return render_template(
        "index.html",
        tareas_urgentes=tareas_urgentes,
        proyectos_activos=proyectos_activos,
        total_proyectos=len(proyectos_activos),
        total_pendientes=total_pendientes,
    )


@main.route("/admin")
@login_required
@solo_admin
def admin():
    proyectos = Proyecto.query.order_by(Proyecto.creado_en.desc()).all()

    usuarios = Usuario.query.order_by(Usuario.creado_en.asc()).all()

    tareas = Tarea.query.all()

    total_proyectos = len(proyectos)
    total_tareas = len(tareas)
    usuarios_activos = Usuario.query.filter_by(activo=True).count()

    return render_template(
        "admin/panel.html",
        proyectos=proyectos,
        usuarios=usuarios,
        total_proyectos=total_proyectos,
        total_tareas=total_tareas,
        usuarios_activos=usuarios_activos,
    )


@main.route("/admin/usuarios/<int:id>/toggle-activo", methods=["POST"])
@login_required
@solo_admin
def toggle_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    usuario.activo = not usuario.activo

    db.session.commit()

    flash("Estado del usuario " + usuario.nombre + " ha sido actualizado.", "success")
    return redirect(url_for("main.admin"))


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
