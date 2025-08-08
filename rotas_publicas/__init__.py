from flask import Blueprint

bp = Blueprint('rotas_publicas', __name__, url_prefix='/rotas_publicas')

from . import rotas
