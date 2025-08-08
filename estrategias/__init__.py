from flask import Blueprint

bp = Blueprint('estrategias', __name__, url_prefix='/estrategias')

from . import rotas
