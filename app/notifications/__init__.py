from flask import Blueprint
from app.models import db, Notificacion, Proyecto, Tarea, Usuario

notifications_bp = Blueprint('notifications', __name__, template_folder='templates')

def crear_notificacion(id_usuario, mensaje, tipo, relacion_id=None, accion_url=None):
    notificacion = Notificacion(
        id_usuario=id_usuario,
        mensaje=mensaje,
        tipo=tipo,
        relacion_id=relacion_id,
        accion_url=accion_url
    )
    db.session.add(notificacion)
    db.session.commit()
    return notificacion

def notificaciones_pendientes():
    """Verifica y crea notificaciones pendientes"""
    try:
        from datetime import datetime, timedelta

        # Proyectos próximos a vencer (3 días antes)
        proyectos = Proyecto.query.filter(
            Proyecto.fecha_fin.between(
                datetime.now().date(),
                datetime.now().date() + timedelta(days=3)
            )
        ).all()

        for proyecto in proyectos:
            crear_notificacion(
                id_usuario=proyecto.id_usuario,
                mensaje=f"⚠️ El proyecto '{proyecto.nombre}' vence en {(proyecto.fecha_fin - datetime.now().date()).days} días",
                tipo='proyecto_vencimiento',
                relacion_id=proyecto.id_proyecto,
                accion_url=f"/project/proyecto/{proyecto.id_proyecto}"
            )
            
    except Exception as e:
        print(f"Error al generar notificaciones: {str(e)}")

# Importar rutas al final para evitar circular imports
from . import routes