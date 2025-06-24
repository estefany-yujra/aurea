from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from config import Config
from .models import db
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import atexit
import logging  
from .models import Notificacion 

# Configuración inicial
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Ruta por defecto para login
scheduler = None  # Variable global para el scheduler

# Cargar variables de entorno
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.start()
    
    # Inicialización de extensiones
    login_manager.init_app(app)
    
    # Configuración del logger
    if app.config.get('ENV') != 'production':
        logging.basicConfig(level=logging.INFO)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Rutas básicas
    @app.route('/bienvenida')
    def bienvenida():
        return redirect(url_for('auth.bienvenida'))
  
    @app.route('/')
    def home():
        return redirect(url_for('bienvenida'))
    
    # Filtro personalizado para el tiempo transcurrido
    app.jinja_env.filters['time_ago'] = time_ago
    
    # Configuración del scheduler
    def start_scheduler():
        with app.app_context():
            from .notifications import notificaciones_pendientes
            
            # Elimina jobs existentes para evitar duplicados
            scheduler.remove_all_jobs()
            
            # Agrega el job con contexto
            scheduler.add_job(
                notificaciones_pendientes,
                'interval',
                hours=1,
                id='notificaciones_job'
            )

    # Inicia el scheduler cuando la app esté lista
    @app.route('/healthcheck')
    def healthcheck():
        return 'OK', 200

    # Inicialización diferida para evitar problemas en reloads
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        start_scheduler()

    return app

def register_blueprints(app):
    """Registra todos los blueprints de la aplicación"""
    from .auth import auth_bp
    from .project import project_bp
    from .notifications import notifications_bp
    from .mentor import mentor_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(project_bp, url_prefix='/project')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(mentor_bp, url_prefix='/mentor')


def time_ago(value):
    """Filtro de Jinja2 para mostrar tiempo transcurrido"""
    now = datetime.now()
    diff = now - value
    
    if diff.days > 365:
        return f'hace {diff.days // 365} años'
    if diff.days > 30:
        return f'hace {diff.days // 30} meses'
    if diff.days > 0:
        return f'hace {diff.days} días'
    if diff.seconds > 3600:
        return f'hace {diff.seconds // 3600} horas'
    if diff.seconds > 60:
        return f'hace {diff.seconds // 60} minutos'
    return 'hace unos segundos'