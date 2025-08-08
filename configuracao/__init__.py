from flask import Blueprint

bp = Blueprint('configuracao', __name__, url_prefix='/configuracao')

from . import rotas
