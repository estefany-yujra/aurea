from app import create_app, db
from app.models import Categoria, Prioridad, Rol, Usuario
from app import db
from app.models import Notificacion

app = create_app()

with app.app_context():
    db.create_all()
    
    # Valores predeterminados
    if not Categoria.query.first():
        categorias = ['Educacion', 'Trabajo', 'Salud', 'Creatividad']
        for nombre in categorias:
            db.session.add(Categoria(nombre=nombre))
            
    if not Prioridad.query.first():
        prioridades = ['Alta', 'Media', 'Baja']
        for nombre in prioridades:
            db.session.add(Prioridad(nombre=nombre))
    if not Rol.query.first():
        roles = [
            Rol(nombre='admin', descripcion = 'Administrador del Sistema'),
            Rol(nombre='usuario', descripcion='Usuario estandar')
        ]
        db.session.add_all(roles)
        
    db.session.commit()     
    print("Tablas creadas y valores añadidos.")