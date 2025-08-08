from flask import Blueprint

bp = Blueprint('acessos', __name__, url_prefix='/acessos')

from . import rotas
