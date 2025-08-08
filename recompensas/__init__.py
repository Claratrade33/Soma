from flask import Blueprint

bp = Blueprint('recompensas', __name__, url_prefix='/recompensas')

from . import rotas
