# web/config.py
import os


class Config:
    # Clave secreta para firmar cookies de sesión y tokens CSRF
    # En producción: valor aleatorio largo desde variable de entorno
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-taskmanager-insegura-cambiar'
    DEBUG = True
