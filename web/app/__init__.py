# web/app/__init__.py
from flask import Flask, render_template
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

from app.models import Usuario


@login_manager.user_loader
def cargar_usuario(user_id):
    return Usuario.query.get(int(user_id))


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Ruta a la que redirigir cuando @login_required falla
    login_manager.login_view = 'auth.login'

    # Mensaje que se muestra al redirigir al login
    login_manager.login_message = 'Inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    # Registrar blueprints
    from app.routes.main import main
    from app.routes.projects import projects
    from app.routes.tasks import tasks
    from app.routes.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(projects)
    app.register_blueprint(tasks)
    app.register_blueprint(auth)

    from app import models  # noqa

    @app.errorhandler(404)
    def no_encontrado(e):
        return render_template('errores/404.html'), 404

    @app.errorhandler(403)
    def prohibido(e):
        return render_template('errores/403.html'), 403

    @app.context_processor
    def inject_api_status():
        try:
            requests.get('http://127.0.0.1:8000/health', timeout=1)
            return {'api_disponible': True}
        except:
            return {'api_disponible': False}

    return app