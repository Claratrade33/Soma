from flask import Blueprint

bp = Blueprint('comunicacao', __name__, url_prefix='/comunicacao')

from . import rotas
