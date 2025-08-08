from flask import Blueprint

bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')

from . import rotas
