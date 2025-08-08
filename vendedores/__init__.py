from flask import Blueprint

bp = Blueprint('vendedores', __name__, url_prefix='/vendedores')

from . import rotas
