from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), default=2, nullable=False)
    rol = db.relationship('Rol', backref='usuario')
    colaboraciones = db.relationship('Colaborador', back_populates='usuario', cascade="all, delete-orphan")
    
    @property
    def proyectos_asignados(self):
        return [c.proyecto for c in self.colaboraciones]
    
    @property
    def id(self):
        return str(self.id_usuario)

class Proyecto(db.Model):
    __tablename__ = 'proyectos'
    
    id_proyecto = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100), nullable = False)
    descripcion = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default='En progreso') #listo/en proceso/ detenido
    prioridad = db.Column(db.String(10), nullable=False, default='Media') # Alta, media, baja
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_fin = db.Column(db.Date, nullable=True)
    progreso = db.Column(db.Integer, nullable=False, default=0)#0-100%
    colaboradores = db.relationship('Colaborador', back_populates='proyecto', cascade="all, delete-orphan")
    
    @property
    def usuarios_asignados(self):
        return [c.usuario for c in self.colaboraciones]
    
    @property
    def progreso_calculado(self):
        if not self.tareas:
            return 0
        completadas = sum(1 for t in self.tareas if t.completado)
        return int((completadas / len(self.tareas)) * 100) 
    
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'))
        
class Tarea(db.Model):
    __tablename__ = 'tareas'
    
    id_tarea = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    completado = db.Column(db.Boolean, default=False)
    
    id_proyecto = db.Column(db.Integer, db.ForeignKey('proyectos.id_proyecto'), nullable=False)
    proyecto = db.relationship('Proyecto', backref='tareas')
    id_prioridad = db.Column(db.Integer, db.ForeignKey('prioridades.id_prioridad'))
    
class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False )
    proyectos = db.relationship('Proyecto', backref='categoria', lazy=True)
    
class Prioridad(db.Model):
    __tablename__ = 'prioridades'
    id_prioridad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    tareas = db.relationship('Tarea',  backref='prioridad', lazy=True)

class Rol(db.Model):
    __tablename__ ='roles'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True)
    descripcion = db.Column(db.String(100))
   
class Colaborador(db.Model):
    __tablename__ = 'colaboradores'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    id_proyecto = db.Column(db.Integer, db.ForeignKey('proyectos.id_proyecto'))
    rol_colab = db.Column(db.String(20)) # lector/editor
    #Relaciones
    usuario = db.relationship('Usuario', back_populates='colaboraciones')
    proyecto = db.relationship('Proyecto', back_populates='colaboradores')
    
class Etiqueta(db.Model):
    __tablename__ = 'etiquetas'
    id_etiqueta = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    color = db.Column(db.String(7)) #ej: #FF5733

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    id_comentario = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_tarea = db.Column(db.Integer, db.ForeignKey('tareas.id_tarea'), nullable=False)
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='comentarios')
    tarea = db.relationship('Tarea', backref='comentarios')

    def __repr__(self):
        return f'<Comentario {self.id_comentario}>' 
    
class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    
    id_notificacion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    mensaje = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(50))  # 'tarea_pendiente', 'proyecto_vencido', 'colaborador', etc.
    leida = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    relacion_id = db.Column(db.Integer)  # ID de proyecto/tarea relacionada
    accion_url = db.Column(db.String(200))  # URL para redirigir al hacer clic

    usuario = db.relationship('Usuario', backref='notificaciones')

    def __init__(self, id_usuario, mensaje, tipo, relacion_id=None, accion_url=None):
        self.id_usuario = id_usuario
        self.mensaje = mensaje
        self.tipo = tipo
        self.relacion_id = relacion_id
        self.accion_url = accion_url   