<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>ClaraVerse Finance 🌙</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Estilo principal -->
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <header>
        <nav>
            <span class="logo">🌙 ClaraVerse Finance</span>
            <ul>
                <li><a href="{{ url_for('index') }}">Início</a></li>
                <li><a href="{{ url_for('painel_operacao') }}">Painel</a></li>
                <li><a href="{{ url_for('configurar') }}">Configurar</a></li>
                <li><a href="{{ url_for('logout') }}">Sair</a></li>
            </ul>
        </nav>
    </header>

    {% if error_msg %}
    <div class="alert danger">{{ error_msg }}</div>
    {% endif %}
    <div class="painel-container">
        <!-- Área para o gráfico (TradingView pode ser embutido aqui depois) -->
        <section class="grafico-section">
            <div id="grafico-candles" style="width:100%;height:340px;background:#18182c;border-radius:24px;margin-bottom:12px;"></div>
            <div class="info-row">
                <span>Par: <b>BTC/USDT</b></span>
                <span>Preço: <span id="preco-ativo">-</span></span>
                <span>RSI: <span id="rsi-ativo">-</span></span>
                <span>Volume: <span id="volume-ativo">-</span></span>
            </div>
        </section>

        <!-- Carteira/Painel de Ordens -->
        <aside class="carteira-section">
            <h2 class="carteira-title">Carteira</h2>
            <div class="carteira-saldo">
                <div>BTC: <span id="saldo-btc">{{ saldo_btc }}</span></div>
                <div>USDT: <span id="saldo-usdt">{{ saldo_usdt }}</span></div>
            </div>
            <input type="number" step="any" min="0" id="qtd_input" placeholder="Quantidade">
            <button class="btn buy" onclick="confirmarOrdem('buy')">Comprar</button>
            <button class="btn sell" onclick="confirmarOrdem('sell')">Vender</button>
            <button class="btn suggest" onclick="confirmarOrdem('suggest')">Sugestão IA</button>
            <button class="btn auto" onclick="confirmarOrdem('auto')">Automático</button>
            <h3 class="historico-title">Histórico de Ordens</h3>
            <ul id="ordens-list"></ul>
        </aside>
    </div>

    <!-- Inclua o JS do painel -->
    <script src="{{ url_for('static', filename='dashboard.js') }}"></script>
</body>
</html>
