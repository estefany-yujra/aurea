from flask import render_template, redirect, url_for, flash, request, jsonify, abort, make_response
from flask_login import login_required, current_user
from . import project_bp
from .forms import ProyectoForm, TareasForm
from app.models import Proyecto, db, Tarea 
from app.models import Usuario, Colaborador, Comentario
from collections import Counter
from ..auth.decorators import admin_required
import csv
from flask import make_response
from xhtml2pdf import pisa
import datetime
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
import base64

#para crear un nuevo proyecto
@project_bp.route('/crear_proyecto', methods =['GET', 'POST'])
@login_required
def crear_proyecto():
    form = ProyectoForm()
    if form.validate_on_submit():
        nuevo = Proyecto(
            nombre = form.nombre.data,
            descripcion = form.descripcion.data,
            estado = form.estado.data,
            prioridad = form.prioridad.data,
            fecha_inicio = form.fecha_inicio.data,
            fecha_fin = form.fecha_fin.data,
            id_usuario = current_user.id_usuario,
            categoria = form.categoria.data 
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Proyecto creado con exito!!!','success')
        return redirect(url_for('project.dashboard'))
    return render_template('project/crear_proyecto.html', form=form)

#para ver el proyecto
@project_bp.route('/proyecto/<int:id>', methods=['GET', 'POST'])
@login_required
def ver_proyecto(id):
    proyecto = Proyecto.query.get_or_404(id)
    if not (
    current_user.id_usuario == proyecto.id_usuario or
    any(col.id_usuario == current_user.id_usuario for col in proyecto.colaboradores) or
    current_user.id_rol == 1  # Admin
):
        flash("No puedes acceder a este proyecto", "Danger")
        return redirect(url_for('project.dashboard'))
    
    form = TareasForm()
    if form.validate_on_submit():
        nueva_tarea = Tarea(
            nombre=form.nombre.data,
            id_proyecto=id,
            prioridad = form.prioridad.data
        )
        db.session.add(nueva_tarea)
        db.session.commit()
        flash("Tarea agregada", "success")
        return redirect(url_for('project.ver_proyecto', id=id))
    #obtener colaboradores con informacion de usuario
    colaboradores = db.session.query(Colaborador, Usuario).join(
        Usuario, Colaborador.id_usuario == Usuario.id_usuario
    ).filter(Colaborador.id_proyecto == id).all()
    
    #Preparar datos para pasar a la plantilla
    colaboradores_data = [{
        'id': colab.id,
        'nombre': usuario.nombre,
        'email': usuario.email,
        'rol': colab.rol_colab
    } for colab, usuario in colaboradores]
    
    tareas = proyecto.tareas   
    completadas = sum(1 for t in tareas if t.completado)
    pendientes = len(tareas) - completadas
    
    prioridades = [t.prioridad.nombre for t in tareas if t.prioridad]
    conteo_prioridades = Counter(prioridades)
    sorted_data = sorted(conteo_prioridades.items(), key=lambda x: x[1], reverse=True)
    etiquetas = [item[0] for item in sorted_data]
    valores = [item[1] for item in sorted_data]
    suma_total = sum(valores)
    porcentajes = [round((v / suma_total) * 100, 2) for v in valores] if suma_total else[]
    
    return render_template(
        'project/ver_proyecto.html', 
        proyecto=proyecto, 
        tareas=tareas, 
        form=form,
        completadas=completadas,
        pendientes=pendientes,
        etiquetas=etiquetas,
        valores = valores,
        porcentajes = porcentajes,
        colaboradores=colaboradores_data
    )

#para marcar tarea como completada
@project_bp.route('/tarea/<int:id_tarea>/completar')
@login_required
def completar_tarea(id_tarea):
    tarea = Tarea.query.get_or_404(id_tarea)
    if tarea.proyecto.id_usuario != current_user.id_usuario:
        flash("Acceso no autorizado", "Danger")
        return redirect(url_for('project.dashboard'))
    
    tarea.completado = not tarea.completado
    db.session.commit()
    flash("Tarea actualizada", "success")
    return redirect(url_for('project.ver_proyecto', id=tarea.id_proyecto))

#para eliminar tarea
@project_bp.route('/tarea/<int:id_tarea>/eliminar')
@login_required
def eliminar_tarea(id_tarea):
    tarea = Tarea.query.get_or_404(id_tarea)
    id_proyecto = tarea.id_proyecto
    if tarea.proyecto.id_usuario != current_user.id_usuario:
        flash("No autorizado", "Danger")
        return redirect(url_for('project.dashboard'))
    
    db.session.delete(tarea)
    db.session.commit()
    flash("Tarea elminada", "seccess")
    return redirect(url_for('project.ver_proyecto', id=id_proyecto))

#para editar tarea
@project_bp.route('/tarea/<int:id_tarea>editar', methods=['GET', 'POST'])
@login_required
def editar_tarea(id_tarea):
    tarea = Tarea.query.get_or_404(id_tarea)
    if tarea.proyecto.id_usuario != current_user.id and current_user not in tarea.usuarios and current_user.rol.nombre != 'admin':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('project.dashboard'))
    
    form = TareasForm(obj=tarea)
    if form.validate_on_submit():
        tarea.nombre = form.nombre.data
        db.session.commit()
        flash("Tarea actualizada", "success")
        return redirect(url_for('project.ver_proyecto', id=tarea.id_proyecto))
    
    return render_template('project/editar_tarea.html', form=form, tarea=tarea)

@project_bp.route('/dashboard-graficos')
@login_required
def dashboard_graficos():
    proyectos = Proyecto.query.filter_by(id_usuario=current_user.id_usuario).all()
    nombres = [p.nombre for p in proyectos]
    avances = [p.progreso_calculado for p in proyectos]
    print (nombres)
    print (avances)
    return render_template('project/dashboard_graficos.html', nombres=nombres, avances=avances)

@project_bp.route('/linea-tiempo')
@login_required
def linea_tiempo():
    proyectos = Proyecto.query.filter_by(id_usuario=current_user.id_usuario).all()
    
    datos = []
    for p in proyectos:
        datos.append({
            'nombre': p.nombre,
            'inicio': p.fecha_inicio.strftime('%Y-%m-%d') if p.fecha_inicio else None,
            'fin': p.fecha_fin.strftime('%Y-%m-%d') if p.fecha_fin else None,
            'avance': p.progreso_calculado or 0
        })
    return render_template('project/linea_tiempo.html', proyectos=datos)

@project_bp.route('/admin/usuarios')
@admin_required
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('auth/usuarios.html', usuarios=usuarios)
    
@project_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol.nombre == 'admin':
        proyectos = Proyecto.query.all()
    else:
        proyectos = Proyecto.query.filter(
            (Proyecto.id_usuario == current_user.id) |
            (Proyecto.colaboradores.any(Colaborador.id_usuario == current_user.id))
        ).all()
    
    return render_template('project/dashboard.html', proyectos=proyectos)

@project_bp.route('/proyecto/<int:id>/invitar', methods=['POST'])
@login_required
def invitar_colaborador(id):
    proyecto = Proyecto.query.get_or_404(id)
    if proyecto.id_usuario != current_user.id_usuario:
        abort(403)
        
    email = request.form.get('email')
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('project.ver_projecto', id=id))
    
    nuevo_colab = Colaborador(
        id_usuario = usuario.id_usuario,
        id_proyecto = id,
        rol_colab = 'editor' #o lector
    )
    db.session.add(nuevo_colab)
    db.session.commit()
    flash ( f' !{usuario.nombre} añadido!', 'success')
    return redirect(url_for('project.ver_proyecto', id=id))

@project_bp.route('/colaborador/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_colaborador(id):
    colaborador = Colaborador.query.get_or_404(id)
    proyecto = colaborador.proyecto  # Asumiendo que tienes esta relación
    
    # Verificar que el usuario actual es el dueño del proyecto
    if proyecto.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para esta acción", "danger")
        return redirect(url_for('project.dashboard'))
    
    db.session.delete(colaborador)
    db.session.commit()
    flash("Colaborador eliminado correctamente", "success")
    return redirect(url_for('project.ver_proyecto', id=proyecto.id_proyecto))

@project_bp.route('/project/admin/dashboard')
@admin_required
def admin_dashboard():
    # Obtener todos los usuarios (excepto otros admins )
    usuarios = Usuario.query.filter(Usuario.id_rol != 1).all()  # Asume que 1 = admin
    
    # Obtener estadísticas globales
    total_proyectos = Proyecto.query.count()
    total_tareas = Tarea.query.count()
    
    return render_template('project/admin_dashboard.html', 
                         usuarios=usuarios,
                         total_proyectos=total_proyectos,
                         total_tareas=total_tareas)
    
@project_bp.route('/exportar_estadisticas')
@admin_required
def exportar_estadisticas(): #para administradores
    # Obtener todos los proyectos y tareas
    proyectos = Proyecto.query.all()
    tareas = Tarea.query.all()

    # Crear un CSV temporal en memoria
    output = []
    output.append(['ID Proyecto', 'Nombre Proyecto', 'Estado', 'Progreso', 'Total Tareas', 'Tareas Completadas'])

    for proyecto in proyectos:
        total_tareas = len(proyecto.tareas)
        completadas = sum(1 for t in proyecto.tareas if t.completado)
        output.append([
            proyecto.id_proyecto,
            proyecto.nombre,
            proyecto.estado,
            f"{proyecto.progreso_calculado}%",
            total_tareas,
            completadas
        ])

    # Crear respuesta CSV
    si = csv.StringIO()
    writer = csv.writer(si)
    writer.writerows(output)
    output_csv = si.getvalue()

    response = make_response(output_csv)
    response.headers["Content-Disposition"] = "attachment; filename=estadisticas_proyectos.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@project_bp.route('/estadisticas')
@login_required
def estadisticas():
    # Obtener proyectos del usuario actual
    proyectos = Proyecto.query.filter_by(id_usuario=current_user.id_usuario).all()
    
    total_proyectos = len(proyectos)
    total_tareas = sum(len(p.tareas) for p in proyectos)
    tareas_completadas = sum(
        sum(1 for t in p.tareas if t.completado) for p in proyectos
    )
    tareas_pendientes = total_tareas - tareas_completadas

    # Avance promedio de todos los proyectos del usuario
    avance_promedio = (
        int(sum(p.progreso_calculado for p in proyectos) / total_proyectos)
        if total_proyectos > 0 else 0
    )

    return render_template(
        'project/estadisticas.html',
        total_proyectos=total_proyectos,
        total_tareas=total_tareas,
        tareas_completadas=tareas_completadas,
        tareas_pendientes=tareas_pendientes,
        avance_promedio=avance_promedio
    )

@project_bp.route('/estadisticas/pdf')
@login_required
def exportar_estadisticas_pdf():

    usuario = current_user
    proyectos = Proyecto.query.filter_by(id_usuario=usuario.id_usuario).all()

    # Estadísticas básicas
    total_proyectos = len(proyectos)
    tareas = [t for p in proyectos for t in p.tareas]
    total_tareas = len(tareas)
    completadas = sum(1 for t in tareas if t.completado)
    pendientes = total_tareas - completadas
    promedio = round((completadas / total_tareas) * 100, 1) if total_tareas > 0 else 0

    # Preparar datos para el Pareto (por prioridad)
    prioridades = [t.prioridad.nombre for t in tareas if t.prioridad]
    conteo = {}
    for pr in prioridades:
        conteo[pr] = conteo.get(pr, 0) + 1

    ordenados = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
    etiquetas_ordenadas, valores_ordenados = zip(*ordenados) if ordenados else ([], [])

    # Porcentaje acumulado
    total = sum(valores_ordenados) if valores_ordenados else 1
    porcentajes = [v / total * 100 for v in valores_ordenados]
    acumulado = 0
    porcentaje_acumulado = []
    for p in porcentajes:
        acumulado += p
        porcentaje_acumulado.append(acumulado)

    # Crear gráfica
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(etiquetas_ordenadas, valores_ordenados, color='#C4B5FD')
    ax1.set_ylabel('Cantidad de Tareas', color='#4C1D95')
    ax1.tick_params(axis='y', labelcolor='#4C1D95')

    ax2 = ax1.twinx()
    ax2.plot(etiquetas_ordenadas, porcentaje_acumulado, color='#F59E0B', marker='o')
    ax2.set_ylabel('% Acumulado', color='#F59E0B')
    ax2.tick_params(axis='y', labelcolor='#F59E0B')
    ax2.set_ylim(0, 110)

    plt.title('Diagrama de Pareto - Prioridades de Tareas')
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Convertir imagen a base64
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    grafico_pareto = base64.b64encode(img.read()).decode('utf-8')

    # Renderizar HTML
    html = render_template('project/estadisticas_pdf.html',
        usuario=usuario,
        fecha=datetime.now().strftime('%d/%m/%Y %H:%M'),
        total_proyectos=total_proyectos,
        total_tareas=total_tareas,
        completadas=completadas,
        pendientes=pendientes,
        promedio=promedio,
        grafico_pareto=grafico_pareto
    )

    # Generar PDF
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        return "Error al generar el PDF", 500

    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=estadisticas_aurea.pdf'
    return response

# Ruta para agregar comentario
@project_bp.route('/tarea/<int:id_tarea>/comentar', methods=['POST'])
@login_required
def agregar_comentario(id_tarea):
    tarea = Tarea.query.get_or_404(id_tarea)
    if tarea.proyecto.id_usuario != current_user.id_usuario:
        abort(403)
    
    nuevo_comentario = Comentario(
        texto=request.form.get('texto'),
        id_usuario=current_user.id_usuario,
        id_tarea=id_tarea
    )
    db.session.add(nuevo_comentario)
    db.session.commit()
    flash('Comentario añadido', 'success')
    return redirect(url_for('project.ver_proyecto', id=tarea.id_proyecto))

# Ruta para eliminar comentario (solo admin o autor)
@project_bp.route('/comentario/<int:id_comentario>/eliminar')
@login_required
def eliminar_comentario(id_comentario):
    comentario = Comentario.query.get_or_404(id_comentario)
    if comentario.id_usuario != current_user.id_usuario and current_user.rol.nombre != 'admin':
        abort(403)
    
    db.session.delete(comentario)
    db.session.commit()
    flash('Comentario eliminado', 'info')
    return redirect(url_for('project.ver_proyecto', id=comentario.tarea.id_proyecto))
