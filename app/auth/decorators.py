from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from app.models import Usuario, Proyecto, Colaborador

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol.nombre != 'admin':
            flash('Acceso restringido a administradores', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def editor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import Proyecto, Colaborador  # Importar aquí para evitar circular imports
        
        # Obtener el proyecto_id de los argumentos de la ruta (ej: /proyecto/<int:id>)
        proyecto_id = kwargs.get('id')
        if not proyecto_id:
            abort(404)
        
        proyecto = Proyecto.query.get_or_404(proyecto_id)
        
        # Verificar si el usuario es:
        # 1. El dueño del proyecto O
        # 2. Un colaborador con rol 'editor'
        es_editor = (
            proyecto.id_usuario == current_user.id_usuario or
            Colaborador.query.filter_by(
                id_proyecto=proyecto.id_proyecto,
                id_usuario=current_user.id_usuario,
                rol_colab='editor'
            ).first() is not None
        )
        
        if not es_editor:
            flash('Requieres permisos de editor', 'danger')
            abort(403)
            
        return f(*args, **kwargs)
    return decorated_function

def acceso_proyecto_requerido(permiso_necesario):
    def decorator(f):
        @wraps(f)
        def decorated_function(project_id, *args, **kwargs):
            # Verificar si es el dueño del proyecto
            proyecto = Proyecto.query.get_or_404(project_id)
            if proyecto.id_usuario == current_user.id_usuario:
                return f(project_id, *args, **kwargs)
                
            # Verificar si es colaborador
            colaboracion = Colaborador.query.filter_by(
                id_usuario=current_user.id_usuario,
                id_proyecto=project_id
            ).first()
            
            if not colaboracion:
                flash("No tienes acceso a este proyecto", "danger")
                return redirect(url_for('project.dashboard'))
                
            # Verificar permisos específicos
            if permiso_necesario == 'editar' and colaboracion.rol_colab != 'editor':
                flash("No tienes permisos de edición", "warning")
                return redirect(url_for('project.ver_proyecto', id=project_id))
                
            return f(project_id, *args, **kwargs)
        return decorated_function
    return decorator