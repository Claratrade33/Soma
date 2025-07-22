<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClaraVerse • Quantum Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: radial-gradient(circle at 20% 80%, #120a2a 0%, #000510 50%, #0a0a0f 100%);
            font-family: 'Orbitron', monospace;
            color: #e0f8ff;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(5, 10, 25, 0.9);
            border-bottom: 2px solid rgba(0, 247, 255, 0.3);
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
        }
        
        .logo h1 {
            background: linear-gradient(135deg, #00f7ff, #bd00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 24px;
            font-weight: 900;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .welcome {
            color: #00f7ff;
            font-weight: 700;
        }
        
        .btn-logout {
            background: linear-gradient(135deg, #ff0066, #ff6600);
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 700;
            cursor: pointer;
            font-family: 'Orbitron', monospace;
            transition: all 0.3s ease;
        }
        
        .btn-logout:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 0, 102, 0.4);
        }
        
        .dashboard-container {
            padding: 40px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: rgba(5, 10, 25, 0.8);
            border: 1px solid rgba(0, 247, 255, 0.3);
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            border-color: #00f7ff;
            box-shadow: 0 0 20px rgba(0, 247, 255, 0.2);
            transform: translateY(-5px);
        }
        
        .stat-label {
            color: #a0d2ff;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 900;
            background: linear-gradient(135deg, #00f7ff, #bd00ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .market-section {
            background: rgba(5, 10, 25, 0.8);
            border: 1px solid rgba(0, 247, 255, 0.3);
            border-radius: 12px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }
        
        .section-title {
            color: #00f7ff;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .market-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .market-item {
            background: rgba(0, 20, 40, 0.6);
            border: 1px solid rgba(0, 247, 255, 0.2);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        
        .market-label {
            color: #a0d2ff;
            font-size: 11px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        
        .market-value {
            font-size: 18px;
            font-weight: 700;
            color: #00ff88;
        }
        
        .positive { color: #00ff88; }
        .negative { color: #ff0066; }
        
        .controls {
            display: flex;
            gap: 15px;
            margin-top: 30px;
            justify-content: center;
        }
        
        .btn {
            background: linear-gradient(135deg, #00f7ff, #bd00ff);
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            color: #000;
            font-weight: 700;
            cursor: pointer;
            font-family: 'Orbitron', monospace;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 247, 255, 0.4);
        }
        
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <h1>🌌 ClaraVerse</h1>
        </div>
        <div class="user-info">
            <span class="welcome">Bem-vindo, {{ user.username }}! 🚀</span>
            <a href="{{ url_for('logout') }}" class="btn-logout">Sair</a>
        </div>
    </div>

    <div class="dashboard-container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">💰 Saldo Atual</div>
                <div class="stat-value">${{ "%.2f"|format(user.saldo_simulado) }}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">📈 BTC Preço</div>
                <div class="stat-value">${{ "%.0f"|format(market_data.preco) }}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">📊 Variação 24h</div>
                <div class="stat-value {% if market_data.variacao > 0 %}positive{% else %}negative{% endif %}">
                    {{ "%.2f"|format(market_data.variacao) }}%
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">🎯 Status</div>
                <div class="stat-value">{% if user.is_premium %}👑 PREMIUM{% else %}🔓 BÁSICO{% endif %}</div>
            </div>
        </div>

        <div class="market-section">
            <div class="section-title">📈 Dados de Mercado em Tempo Real</div>
            
            <div class="market-grid">
                <div class="market-item">
                    <div class="market-label">💹 Preço Atual</div>
                    <div class="market-value pulse-animation">${{ "%.2f"|format(market_data.preco) }}</div>
                </div>
                
                <div class="market-item">
                    <div class="market-label">📊 Volume 24h</div>
                    <div class="market-value">{{ market_data.volume }}</div>
                </div>
                
                <div class="market-item">
                    <div class="market-label">🔺 Alta 24h</div>
                    <div class="market-value positive">${{ "%.2f"|format(market_data.high_24h) }}</div>
                </div>
                
                <div class="market-item">
                    <div class="market-label">🔻 Baixa 24h</div>
                    <div class="market-value negative">${{ "%.2f"|format(market_data.low_24h) }}</div>
                </div>
            </div>

            <div class="controls">
                <button class="btn" onclick="refreshMarketData()">🔄 Atualizar Dados</button>
                <a href="#" class="btn">⚡ Operar</a>
                <a href="#" class="btn">🔮 Análise IA</a>
                <a href="#" class="btn">⚙️ Configurar</a>
            </div>
        </div>
    </div>

    <script>
        function refreshMarketData() {
            fetch('/api/dados_mercado')
                .then(response => response.json())
                .then(data => {
                    location.reload();
                })
                .catch(error => console.error('Erro:', error));
        }

        // Auto-refresh a cada 30 segundos
        setInterval(refreshMarketData, 30000);
        
        // Efeito de entrada
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.stat-card, .market-section');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        });
    </script>
</body>
</html>