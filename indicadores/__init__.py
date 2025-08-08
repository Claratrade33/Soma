from flask import Blueprint

bp = Blueprint('indicadores', __name__, url_prefix='/indicadores')

from . import rotas
