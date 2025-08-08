from flask import Blueprint

# Blueprint responsável por autenticação e controle de acesso.
# Não utiliza `url_prefix` para que rotas como `/login` e `/logout`
# fiquem diretamente na raiz da aplicação.
bp = Blueprint("acessos", __name__)

from . import rotas
