from flask import Blueprint

bp = Blueprint('inteligencia', __name__, url_prefix='/inteligencia')

from . import rotas
