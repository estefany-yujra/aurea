from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Notificacion
from . import notifications_bp

@notifications_bp.route('/notificaciones')
@login_required
def ver_notificaciones():
    notificaciones = current_user.notificaciones.order_by(
        Notificacion.leida,
        Notificacion.fecha_creacion.desc()
    ).all()
    return render_template('notifications/notificaciones.html', notificaciones=notificaciones)

@notifications_bp.route('/notificacion/<int:id>/leer')
@login_required
def marcar_leida(id):
    notificacion = Notificacion.query.get_or_404(id)
    if notificacion.id_usuario != current_user.id_usuario:
        abort(403)
    
    notificacion.leida = True
    db.session.commit()
    
    if notificacion.accion_url:
        return redirect(notificacion.accion_url)
    return redirect(url_for('notifications.ver_notificaciones'))