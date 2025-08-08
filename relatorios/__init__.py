from flask import Blueprint

bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')

from . import rotas
