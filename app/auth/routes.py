from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth_bp
from .forms import LoginForm, RegisterForm
from app.models import db, Usuario
from app import login_manager
from .decorators import admin_required
from .forms import AdminRegisterForm
from app.utils.motivacion import obtener_frase_aleatoria

@login_manager.user_loader
def load_user(user_id):
    frase = obtener_frase_aleatoria()
    flash(obtener_frase_aleatoria(), 'motivacion')
    print("LOAD USER - user_id recibido:", user_id)
    try:
        return Usuario.query.get(int(user_id))
    except Exception as e:
        print("Error al cargar usuario:", e)
        return None


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and check_password_hash(usuario.contraseña, form.password.data):
            login_user(usuario)

            # ✅ Mostrar notificaciones pendientes
            notificaciones = [n.mensaje for n in usuario.notificaciones if not n.leida][:3]
            for notif in notificaciones:
                flash(notif, 'info')  # Puedes usar 'warning' si quieres que se destaque más

            # ✅ Mostrar frase motivacional
            frase = obtener_frase_aleatoria()
            flash(frase, 'success')

            return redirect(url_for('project.dashboard'))

        flash('Correo o contraseña incorrectos', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_pass = generate_password_hash(form.password.data)
        nuevo_usuario = Usuario(nombre=form.nombre.data, email=form.email.data, contraseña=hash_pass, id_rol=2)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Registro exitoso, Ahora puedes iniciar sesion.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/admin/registrar-usuario', methods=['GET', 'POST'])
@admin_required #solo accesible para admins
def registrar_usuario_admin():
    form = AdminRegisterForm()
    if form.validate_on_submit():
        usuario = Usuario(
            nombre = form.nombre.data,
            email=form.email.data,
            contraseña = generate_password_hash(form.password.data),
            id_rol = int(form.rol.data) #rol seleccionado en el formulario
        )
        db.session.add(usuario)
        db.session.commit()
        flash(f'Usuario {form.nombre.data} registrado como {"Admin" if form.rol.data == "1" else "Usuario"}', 'success')
        return redirect(url_for('auth.registrar_usuario_admin'))
    return render_template('auth/registro_admin.html', form=form)

@auth_bp.route('/bienvenida')
@login_required
def bienvenida():
    # Mostrar notificaciones recientes (máx 3)
    notificaciones = [n.mensaje for n in current_user.notificaciones if not n.leida][:3]
    for notif in notificaciones:
        flash(notif, 'info')

    # Frase motivacional
    from app.utils.motivacion import obtener_frase_aleatoria
    flash(obtener_frase_aleatoria(), 'success')

    return render_template('bienvenida.html')