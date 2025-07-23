<div class="container">
    <h2>📊 Visão de Mercado</h2>

    <table class="tabela" id="crypto-table">
        <thead>
            <tr>
                <th>Moeda</th>
                <th>Preço</th>
                <th>24h</th>
                <th>Volume</th>
                <th>RSI</th>
            </tr>
        </thead>
        <tbody>
            {% for symbol, data in crypto_data.items() %}
            <tr>
                <td>{{ symbol }}</td>
                <td>{{ data.price }}</td>
                <td>{{ data.change_24h }}%</td>
                <td>{{ data.volume_24h }}</td>
                <td>{{ data.rsi }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h3 style="margin-top: 30px;">📚 Últimas Operações</h3>
    <table class="tabela">
        <thead>
            <tr>
                <th>Par</th>
                <th>Tipo</th>
                <th>Entrada</th>
                <th>Saída</th>
                <th>Lucro</th>
                <th>Estratégia</th>
                <th>Horário</th>
            </tr>
        </thead>
        <tbody>
            {% for trade in trades %}
            <tr>
                <td>{{ trade.symbol }}</td>
                <td>{{ trade.side }}</td>
                <td>{{ trade.entry_price }}</td>
                <td>{{ trade.exit_price or '---' }}</td>
                <td>{{ trade.profit_loss or '---' }}</td>
                <td>{{ trade.strategy_used }}</td>
                <td>{{ trade.timestamp.strftime('%d/%m %H:%M') }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h3 style="margin-top: 30px;">💱 Realizar Trade</h3>
    <form method="POST" action="{{ url_for('trade') }}">
        <label for="symbol" style="color: #ccc;">📈 Par de Moeda (ex: BTCUSDT)</label>
        <input type="text" id="symbol" name="symbol" required
               style="width: 100%; padding: 10px; margin-bottom: 15px; border-radius: 5px; border: none;">

        <label for="side" style="color: #ccc;">🔄 Tipo de Operação</label>
        <select id="side" name="side" required
                style="width: 100%; padding: 10px; margin-bottom: 15px; border-radius: 5px; border: none;">
            <option value="BUY">Comprar</option>
            <option value="SELL">Vender</option>
        </select>

        <label for="quantity" style="color: #ccc;">💵 Quantidade</label>
        <input type="number" id="quantity" name="quantity" required min="0.001" step="0.001"
               style="width: 100%; padding: 10px; margin-bottom: 20px; border-radius: 5px; border: none;">

        <button type="submit"
                style="width: 100%; padding: 12px; background-color: #00ffff; color: #000; font-weight: bold; border: none; border-radius: 6px;">
            🚀 Executar Trade
        </button>
    </form>
</div>

<!-- Inclua o JavaScript aqui -->
<script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>