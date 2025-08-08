from flask import Blueprint

bp = Blueprint('anjos', __name__, url_prefix='/anjos')

from . import rotas
