# web/app/routes/users.py (este no se pide pero lo hago yo para no marearme)
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Proyecto, Tarea, Usuario
from sqlalchemy import case
from app.forms import EditarPerfilForm
from app import db

main = Blueprint('main', __name__)


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
