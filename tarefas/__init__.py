from flask import Blueprint

bp = Blueprint('tarefas', __name__, url_prefix='/tarefas')

from . import rotas
