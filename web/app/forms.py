# web/app/forms.py
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField,
    DateField, PasswordField, BooleanField, SubmitField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, ValidationError
from datetime import date


class ProyectoForm(FlaskForm):
    """Formulario para crear y editar proyectos."""
    titulo = StringField(
        'Título del proyecto',
        validators=[
            DataRequired(message='El título es obligatorio.'),
            Length(min=3, max=100,
                   message='El título debe tener entre 3 y 100 caracteres.')
        ]
    )
    descripcion = TextAreaField(
        'Descripción',
        validators=[
            Optional(),
            Length(max=500,
                   message='La descripción no puede superar los 500 caracteres.')
        ]
    )
    fecha_limite = DateField(
        'Fecha límite',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    submit = SubmitField('Guardar proyecto')

    def validate_fecha_limite(self, campo):
        if campo.data and campo.data < date.today():
            raise ValidationError("La fecha límite no puede ser en el pasado.")

    def validate_titulo(self, campo):
        titulo = campo.data.strip().lower()

        if not titulo:
            raise ValidationError("El título no puede estar vacío o ser solo espacios.")

        genericos = {"proyecto", "nuevo", "test", "prueba"}

        if titulo in genericos:
            raise ValidationError(f'"{campo.data}" es demasiado genérico. Elige un título más descriptivo.')


class TareaForm(FlaskForm):
    """Formulario para crear y editar tareas."""

    def __init__(self, proyecto=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto

    titulo = StringField(
        'Título de la tarea',
        validators=[DataRequired(), Length(min=3, max=200)]
    )
    descripcion = TextAreaField(
        'Descripción',
        validators=[Optional()]
    )
    prioridad = SelectField(
        'Prioridad',
        choices=[
            ('baja', 'Baja'),
            ('media', 'Media'),
            ('alta', 'Alta'),
            ('urgente', 'Urgente'),
        ],
        default='media'
    )
    estado = SelectField(
        'Estado',
        choices=[
            ('pendiente', 'Pendiente'),
            ('en_progreso', 'En progreso'),
            ('revision', 'En revisión'),
            ('completada', 'Completada'),
        ],
        default='pendiente'
    )
    fecha_limite = DateField(
        'Fecha límite',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    submit = SubmitField('Guardar tarea')


    def validate_titulo(self, campo):
        titulo = campo.data.strip().lower()

        if self.proyecto:
            for tarea in self.proyecto["tareas"]:
                if tarea["titulo"].strip().lower() == titulo:
                    raise ValidationError("Ya existe una tarea con ese título en este proyecto.")


class BusquedaForm(FlaskForm):
    """Formulario de búsqueda de proyectos y tareas."""
    q = StringField(
        'Buscar',
        validators=[
            DataRequired(),
            Length(min=2,
                   message='Escribe al menos 2 caracteres para buscar.')
        ]
    )
    submit = SubmitField('Buscar')


class RegistroForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        validators=[
            DataRequired(),
            Length(
                min=2, max=80, message="El nombre debe tener entre 2 y 80 caracteres"
            ),
        ],
    )
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired(), Email(message="Email no válido.")],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(), Length(min=8, message="Mínimo 8 caracteres.")],
    )
    confirmar = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )
    submit = SubmitField("Crear cuenta")


class LoginForm(FlaskForm):
    email = StringField("Correo electrónico", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    recordarme = BooleanField("Recordarme en este dispositivo")
    submit = SubmitField("Iniciar sesión")
