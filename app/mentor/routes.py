# app/mentor/routes.py
import google.generativeai as genai
from flask import request, jsonify
from flask_login import login_required, current_user
from . import mentor_bp
from app.models import Proyecto

# Configuración temporal de Gemini (para pruebas, luego se puede mover al entorno)
genai.configure(api_key="AIzaSyByzFKXsx_xZ9oZinBO0LfyENAzfYXFUfs", transport="rest")

# Usa un modelo disponible (verificado previamente)
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

@mentor_bp.route('/responder', methods=['POST'])
@login_required
def responder():
    try:
        data = request.get_json()
        mensaje_usuario = data.get('mensaje', '').strip()

        if not mensaje_usuario:
            return jsonify({"error": "Mensaje vacío"}), 400

        # Obtener proyectos del usuario
        proyectos = Proyecto.query.filter_by(id_usuario=current_user.id).all()
        if not proyectos:
            contexto_proyectos = "El usuario no tiene proyectos registrados."
        else:
            contexto_proyectos = "\n".join(
                f"- {p.nombre}: {p.descripcion or 'Sin descripción'}, del {p.fecha_inicio} al {p.fecha_fin}"
                for p in proyectos
            )

        # Crear el prompt completo con contexto
        prompt = f"""
Eres un mentor experto en gestión de proyectos. Tu tarea es orientar a los usuarios según los proyectos que tienen.

Proyectos actuales de {current_user.nombre}:
{contexto_proyectos}

Mensaje del usuario:
"{mensaje_usuario}"

Responde de forma clara, útil y motivadora.
"""

        respuesta = model.generate_content(prompt)
        return jsonify({"respuesta": respuesta.text})

    except Exception as e:
        print("Error durante la exposición IA:", e)
        return jsonify({
            "error": "El mentor tuvo un problema. Intenta nuevamente.",
            "detalle": str(e)
        }), 500
