from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv

conectores_bp = Blueprint('conectores', __name__)
load_dotenv()

@conectores_bp.route('/conectores')
def painel_conectores():
    return render_template('conectores/painel_conectores.html')

@conectores_bp.route('/conectores/configurar-api', methods=['GET', 'POST'])
def configurar_api():
    """Exibe e processa o formulário para atualizar as chaves de API.

    Esta rota permite que o usuário informe as chaves da Binance e
    também a chave da OpenAI. As chaves são salvas no arquivo `.env`
    do projeto para que outras partes da aplicação possam utilizá-las.
    """
    if request.method == 'POST':
        nova_key = request.form.get('api_key')
        nova_secret = request.form.get('api_secret')
        nova_openai = request.form.get('openai_key')

        # Verifica se todas as chaves foram preenchidas
        if not (nova_key and nova_secret and nova_openai):
            flash('Preencha todos os campos.', 'danger')
        else:
            # Prepara as linhas do arquivo .env. Esta abordagem
            # sobrescreve apenas as variáveis relevantes. Caso
            # existam outras variáveis, elas podem ser adicionadas
            # manualmente abaixo.
            lines = [
                f"BINANCE_API_KEY={nova_key}",
                f"BINANCE_API_SECRET={nova_secret}",
                "BINANCE_BASE_URL=https://api.binance.com",
                f"OPENAI_API_KEY={nova_openai}",
            ]
            with open('.env', 'w') as env_file:
                env_file.write('\n'.join(lines) + '\n')

            flash('Chaves atualizadas com sucesso.', 'success')
            return redirect(url_for('conectores.painel_conectores'))

    return render_template('conectores/configurar_api.html')
