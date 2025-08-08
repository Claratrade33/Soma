from flask import Blueprint

bp = Blueprint('conectores', __name__, url_prefix='/conectores')

from . import rotas
