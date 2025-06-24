import random

FRASES_MOTIVACIONALES = [
    "Cada pequeño avance te acerca a tu gran meta.",
    "Hoy es un buen día para construir el futuro que deseas.",
    "No esperes a que las condiciones sean perfectas. Empieza ahora.",
    "Tus ideas valen más cuando las haces realidad.",
    "El éxito no es magia, es trabajo constante y enfoque.",
    "Confía en tu proceso, incluso cuando los resultados tarden en llegar.",
    "Avanza, aunque sea un paso a la vez. Estás progresando.",
    "Cada error es una oportunidad para crecer y mejorar.",
    "La disciplina supera a la motivación cuando esta se acaba.",
    "Tus metas merecen tu esfuerzo. No te rindas.",
    "No tienes que ser el mejor, solo tienes que ser constante.",
    "Cree en ti: eres más capaz de lo que imaginas.",
    "Un día a la vez, un logro a la vez.",
    "Hazlo con pasión o no lo hagas.",
    "Los grandes proyectos nacen de pequeños pasos valientes.",
    # Puedes agregar más si gustas 🌟
    "Sigue construyendo incluso si el camino es lento.",
    "Eres más fuerte que tus dudas.",
    "Hoy también cuenta como progreso."
]

def obtener_frase_aleatoria():
    return random.choice(FRASES_MOTIVACIONALES)