from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from app.models import Categoria
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Prioridad

def categorias():
    return Categoria.query.all()

class ProyectoForm(FlaskForm):
    nombre = StringField('Nombre del proyecto', validators=[DataRequired(), Length(min=3)])
    descripcion = TextAreaField('Descripcion', validators=[Length(max=300)])
    estado = SelectField('Estado', choices=[('En proceso', 'En proceso'), ('listo', 'listo'), ('Detenido', 'Detenido')])
    prioridad = SelectField('Prioridad', choices=[('Alta', 'Alta'), ('Media', 'Media'), ('Baja', 'Baja')])
    fecha_inicio = DateField('Fecha de inicio')
    fecha_fin = DateField('Fecha de fin')
    submit = SubmitField('Crear Proyecto')  
    categoria = QuerySelectField('Categoria', query_factory=categorias, get_label='nombre', allow_blank=True)

def prioridades():
    return Prioridad.query.all()
  
class TareasForm(FlaskForm):
    nombre = StringField('Nueva tarea', validators=[DataRequired()])
    submit = SubmitField('Agregar')
    prioridad = QuerySelectField('Prioridad', query_factory=prioridades, get_label='nombre', allow_blank=True)
    
    