from flask import Blueprint
mentor_bp = Blueprint('mentor', __name__, template_folder='templates')
from . import routes
