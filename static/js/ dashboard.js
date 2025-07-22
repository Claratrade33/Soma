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
            position: relative;
        }
        
        /* Partículas de fundo */
        .stars {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }
        
        .star {
            position: absolute;
            width: 2px;
            height: 2px;
            background: #00f7ff;
            border-radius: 50%;
            animation: twinkle 3s infinite;
        }
        
        @keyframes twinkle {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 1; }
        }
        
        .header {
            background: rgba(5, 10, 25, 0.9);
            border-bottom: 2px solid rgba(0, 247, 255, 0.3);
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
            position: relative;
            z-index: 100;
        }
        
        .logo h1 {
            background: linear-gradient(135deg, #00f7ff, #bd00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 24px;
            font-weight: 900;
            animation: glow 2s infinite alternate;
        }
        
        @keyframes glow {
            0% { text-shadow: 0 0 5px rgba(0, 247, 255, 0.5); }
            100% { text-shadow: 0 0 20px rgba(0, 247, 255, 0.8); }
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
            text-decoration: none;
        }
        
        .btn-logout:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 0, 102, 0.4);
        }
        
        .dashboard-container {
            padding: 40px 20px;
            max-width: 1200px;
            margin: 0 auto;
            position: relative;
            z-index: 10;
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
            position: relative;
            overflow: hidden;
        }
        
        .stat-card:hover {
            border-color: #00f7ff;
            box-shadow: 0 0 20px rgba(0, 247, 255, 0.2);
            transform: translateY(-5px);
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 247, 255, 0.1), transparent);
            transition: 0.5s;
        }
        
        .stat-card:hover::before {
            left: 100%;
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
            margin-bottom: 30px;
        }
        
        .section-title {
            color: #00f7ff;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-align: center;
        }
        
        .market-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .market-item {
            background: rgba(0, 20, 40, 0.6);
            border: 1px solid rgba(0, 247, 255, 0.2);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .market-item:hover {
            border-color: #00f7ff;
            background: rgba(0, 30, 60, 0.8);
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
            flex-wrap: wrap;
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
            position: relative;
            overflow: hidden;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 247, 255, 0.4);
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: 0.5s;
        }
        
        .btn:hover::before {
            left: 100%;
        }
        
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        /* Seção de tecnologia alienígena */
        .alien-section {
            background: linear-gradient(135deg, rgba(189, 0, 255, 0.1), rgba(0, 247, 255, 0.1));
            border: 1px solid rgba(189, 0, 255, 0.3);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .alien-title {
            color: #bd00ff;
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 20px;
            text-align: center;
            text-transform: uppercase;
        }
        
        .consciousness-bar {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 20px;
            height: 20px;
            margin-bottom: 10px;
            overflow: hidden;
        }
        
        .consciousness-fill {
            height: 100%;
            background: linear-gradient(90deg, #bd00ff, #00f7ff);
            border-radius: 20px;
            transition: width 1s ease;
            position: relative;
        }
        
        .consciousness-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        /* Loading states */
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        
        .spinner {
            border: 3px solid rgba(0, 247, 255, 0.3);
            border-top: 3px solid #00f7ff;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 15px;
                padding: 15px;
            }
            
            .dashboard-container {
                padding: 20px 10px;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .controls {
                flex-direction: column;
                align-items: center;
            }
            
            .btn {
                width: 200px;
            }
        }
        
        /* Flash messages */
        .flash-messages {
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 1000;
            max-width: 400px;
        }
        
        .flash-message {
            background: rgba(0, 0, 0, 0.9);
            border-left: 4px solid #00f7ff;
            color: #fff;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            animation: slideIn 0.5s ease;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(100%); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .flash-success { border-left-color: #00ff88; }
        .flash-error { border-left-color: #ff0066; }
    </style>
</head>
<body>
    <!-- Partículas de fundo -->
    <div class="stars" id="stars"></div>

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="flash-messages">
                {% for category, message in messages %}
                    <div class="flash-message flash-{{ category }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

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
        <!-- Stats Grid -->
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

        <!-- Seção de Tecnologia Alienígena -->
        <div class="alien-section">
            <div class="alien-title">🛸 Tecnologia Acquaturiana Ativa</div>
            
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>⚡ Ativação Starseed</span>
                    <span>{{ user.starseed_activation }}%</span>
                </div>
                <div class="consciousness-bar">
                    <div class="consciousness-fill" style="width: {{ user.starseed_activation }}%;"></div>
                </div>
            </div>
            
            <div style="text-align: center; color: #bd00ff;">
                🌟 Nível: {{ user.alien_consciousness_level }}
                {% if user.galactic_blessing %}• 🛡️ Bênção Galáctica Ativa{% endif %}
            </div>
        </div>

        <!-- Dados de Mercado -->
        <div class="market-section">
            <div class="section-title">📈 Dados de Mercado em Tempo Real</div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Atualizando dados...</p>
            </div>
            
            <div class="market-grid" id="marketGrid">
                <div class="market-item">
                    <div class="market-label">💹 Preço Atual</div>
                    <div class="market-value pulse-animation" id="currentPrice">${{ "%.2f"|format(market_data.preco) }}</div>
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
                
                <div class="market-item">
                    <div class="market-label">📈 RSI</div>
                    <div class="market-value">{{ "%.1f"|format(market_data.rsi) }}</div>
                </div>
                
                <div class="market-item">
                    <div class="market-label">🎯 Suporte</div>
                    <div class="market-value">${{ "%.2f"|format(market_data.suporte) }}</div>
                </div>
            </div>

            <div class="controls">
                <button class="btn" onclick="refreshMarketData()">🔄 Atualizar Dados</button>
                <button class="btn" onclick="openTradeModal()">⚡ Operar</button>
                <button class="btn" onclick="requestAlienAnalysis()">🔮 Análise Alienígena</button>
                <a href="{{ url_for('configurar') }}" class="btn">⚙️ Configurar</a>
            </div>
        </div>
    </div>

    <script>
        // Criar estrelas de fundo
        function createStars() {
            const starsContainer = document.getElementById('stars');
            for (let i = 0; i < 100; i++) {
                const star = document.createElement('div');
                star.className = 'star';
                star.style.left = Math.random() * 100 + '%';
                star.style.top = Math.random() * 100 + '%';
                star.style.animationDelay = Math.random() * 3 + 's';
                starsContainer.appendChild(star);
            }
        }

        // Atualizar dados de mercado
        function refreshMarketData() {
            const loading = document.getElementById('loading');
            const marketGrid = document.getElementById('marketGrid');
            
            loading.style.display = 'block';
            marketGrid.style.opacity = '0.5';
            
            // Simular chamada API (você pode implementar uma rota real)
            setTimeout(() => {
                location.reload(); // Por enquanto, recarrega a página
            }, 2000);
        }

        // Abrir modal de trading
        function openTradeModal() {
            alert('🛸 Acessando Terminal de Trading Alienígena...\n\n⚡ Funcionalidade em desenvolvimento!\n🚀 Em breve com tecnologia Acquaturiana!');
        }

        // Solicitar análise alienígena
        function requestAlienAnalysis() {
            const btn = event.target;
            btn.innerHTML = '🔮 Consultando Acquaturianos...';
            btn.disabled = true;
            
            fetch('/api/acquaturian_prediction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    symbol: 'BTC/USD',
                    analysis_type: 'quantum_prediction'
                })
            })
            .then(response => response.json())
            .then(data => {
                alert('🛸 ' + data.message);
                btn.innerHTML = '🔮 Análise Alienígena';
                btn.disabled = false;
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('⚠️ Interferência dimensional detectada!');
                btn.innerHTML = '🔮 Análise Alienígena';
                btn.disabled = false;
            });
        }

        // Auto-refresh a cada 30 segundos
        setInterval(() => {
            if (!document.hidden) { // Só atualiza se a aba estiver ativa
                refreshMarketData();
            }
        }, 30000);
        
        // Efeito de entrada
        document.addEventListener('DOMContentLoaded', function() {
            createStars();
            
            const cards = document.querySelectorAll('.stat-card, .market-section, .alien-section');
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

        // Remover mensagens flash após 5 segundos
        setTimeout(() => {
            const flashMessages = document.querySelector('.flash-messages');
            if (flashMessages) {
                flashMessages.style.animation = 'slideOut 0.5s ease';
                setTimeout(() => flashMessages.remove(), 500);
            }
        }, 5000);

        // Atualizar preço em tempo real (simulado)
        setInterval(() => {
            const priceElement = document.getElementById('currentPrice');
            if (priceElement) {
                const currentPrice = parseFloat(priceElement.textContent.replace('$', ''));
                const variation = (Math.random() - 0.5) * 100; // ±50
                const newPrice = currentPrice + variation;
                priceElement.textContent = '$' + newPrice.toFixed(2);
            }
        }, 5000);
    </script>
</body>
</html>