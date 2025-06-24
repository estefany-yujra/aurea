from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('Correo electronico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesion')
    
class RegisterForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[DataRequired(), Length(min=3)])
    email = StringField('Correo electronico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

class AdminRegisterForm(FlaskForm):
    nombre = StringField('Nombre Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Comtraseña', validators=[DataRequired(),Length(min=6)])
    rol = SelectField('Rol', choices=[ #solo visible para admins
        ('2', 'Usuario estandar'),
        ('1', 'Administrador')
    ], default = '2')
    submit = SubmitField('Registrar Usuario')  