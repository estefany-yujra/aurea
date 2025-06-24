import os
from dotenv import load_dotenv

# Configuración UTF-8 global
os.environ["PYTHONUTF8"] = "1"

# Ruta absoluta del .env
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

# Carga el entorno (sin verificación de BOM porque ya lo solucionamos)
load_dotenv(env_path, encoding='utf-8')

class Config:
    # Claves requeridas (¡asegúrate de que coincidan con .env!)
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-por-defecto-si-falla')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # ¡Corregido el nombre!
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'aurea.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Debug adicional (opcional)
    @classmethod
    def print_config(cls):
        print("🔍 Configuración cargada:")
        print(f" - OPENAI_API_KEY: {cls.OPENAI_API_KEY[:5]}...")
        print(f" - SECRET_KEY: {cls.SECRET_KEY[:5]}...")