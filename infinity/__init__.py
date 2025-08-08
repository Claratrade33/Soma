from flask import Blueprint

bp = Blueprint('infinity', __name__, url_prefix='/infinity')

from . import rotas
