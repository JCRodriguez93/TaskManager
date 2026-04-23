# web/app/forms.py
from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField,
    DateField, PasswordField, BooleanField, SubmitField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, ValidationError


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
    
    def validate_fecha_limite(self, field):
        """La fecha límite no puede ser en el pasado."""
        if field.data and field.data < date.today():
            raise ValidationError(
                'La fecha límite no puede ser anterior a hoy.'
            )

    def validate_titulo(self, field):
        """El título no puede ser genérico."""
        titulos_no_permitidos = ['proyecto', 'nuevo', 'test', 'prueba']

        if field.data and field.data.lower().strip() in titulos_no_permitidos:
            raise ValidationError(
                f'"{field.data}" es demasiado genérico. '
                'Por favor, elige un título más descriptivo.'
            )


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


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión (lo usaremos en U05)."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    recordarme = BooleanField('Recordarme')
    submit = SubmitField('Iniciar sesión')


class RegistroForm(FlaskForm):
    """Formulario de registro de nuevos usuarios (lo usaremos en U05)."""
    nombre = StringField(
        'Nombre',
        validators=[DataRequired(), Length(min=2, max=80)]
    )
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(),
            Length(min=8,
                   message='La contraseña debe tener al menos 8 caracteres.')
        ]
    )
    confirmar = PasswordField(
        'Confirmar contraseña',
        validators=[
            EqualTo('password',
                    message='Las contraseñas no coinciden.')
        ]
    )
    submit = SubmitField('Crear cuenta')
  
class EditarPerfilForm(FlaskForm):
    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(min=2, max=50)
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(message="El email es obligatorio"),
            Email()
        ]
    )

    password_actual = PasswordField(
        'Contraseña actual',
        validators=[
            DataRequired(message="Debes introducir tu contraseña actual")
        ]
    )

    password_nuevo = PasswordField(
        'Nueva contraseña',
        validators=[
            Optional(),
            Length(min=6, message="Mínimo 6 caracteres")
        ]
    )

    confirmar_nuevo = PasswordField(
        'Confirmar nueva contraseña',
        validators=[
            Optional(),
            EqualTo('password_nuevo', message="Las contraseñas no coinciden")
        ]
    )

    submit = SubmitField('Guardar cambios')
