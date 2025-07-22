// static/js/Dashboard.js

document.addEventListener('DOMContentLoaded', () => {
  // 1) Conexão WebSocket (Socket.IO)
  const socket = io();  // exige <script src="/socket.io/socket.io.js"></script> no base.html

  socket.on('connect', () => {
    console.log('WebSocket conectado');
    socket.emit('subscribe_market');
  });

  socket.on('market_update', data => {
    updateCryptoTable(data.crypto);
    updateBrTable(data.brazilian);
  });

  socket.on('error', err => {
    console.error('Socket error:', err);
  });


  // 2) Funções para atualização de tabelas
  function updateCryptoTable(crypto) {
    const tbody = document.querySelector('#crypto-table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    for (let sym in crypto) {
      const d = crypto[sym];
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${sym}</td>
        <td>${d.price.toFixed(2)}</td>
        <td>${d.change_24h.toFixed(2)}</td>
        <td>${d.volume_24h}</td>
        <td>${d.rsi.toFixed(1)}</td>
      `;
      tbody.appendChild(tr);
    }
  }

  function updateBrTable(br) {
    const tbody = document.querySelector('#br-table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    for (let idx in br) {
      const d = br[idx];
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${idx}</td>
        <td>${d.price.toFixed(2)}</td>
        <td>${d.change_percent.toFixed(2)}</td>
      `;
      tbody.appendChild(tr);
    }
  }


  // 3) Chamada de análise inteligente
  const analyzeForm = document.getElementById('analyze-form');
  if (analyzeForm) {
    analyzeForm.addEventListener('submit', async e => {
      e.preventDefault();
      const symbol = analyzeForm.elements['symbol'].value;
      try {
        const res = await fetch('/api/intelligent_analysis', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ symbol })
        });
        const body = await res.json();
        if (body.success) {
          displayAnalysis(body);
        } else {
          alert('Erro na análise: ' + body.error);
        }
      } catch (err) {
        console.error(err);
        alert('Falha na requisição de análise');
      }
    });
  }

  function displayAnalysis(data) {
    const out = document.getElementById('analysis-output');
    if (!out) return;
    out.innerHTML = `
      <pre>${JSON.stringify(data, null, 2)}</pre>
    `;
  }


  // 4) Chamada de execução de trade
  const tradeForm = document.getElementById('trade-form');
  if (tradeForm) {
    tradeForm.addEventListener('submit', async e => {
      e.preventDefault();
      const symbol = tradeForm.elements['symbol'].value;
      const side   = tradeForm.elements['side'].value;
      const qty    = tradeForm.elements['quantity'].value;
      try {
        const res = await fetch('/api/execute_trade', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ symbol, side, quantity: qty })
        });
        const body = await res.json();
        if (body.success) {
          alert(`Trade executado: P&L = ${body.pnl.toFixed(2)}`);
          // opcional: recarregar estatísticas / tabela de trades
          loadUserTrades();
        } else {
          alert('Erro no trade: ' + body.error);
        }
      } catch (err) {
        console.error(err);
        alert('Falha na requisição de trade');
      }
    });
  }

  // 5) Carregar últimas operações
  async function loadUserTrades() {
    try {
      const res = await fetch('/api/user_trades');
      const arr = await res.json();
      const tbody = document.querySelector('#trades-table tbody');
      if (!tbody) return;
      tbody.innerHTML = '';
      arr.forEach(t => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${new Date(t.timestamp).toLocaleTimeString()}</td>
          <td>${t.symbol}</td>
          <td>${t.side}</td>
          <td>${t.quantity}</td>
          <td>${t.entry_price.toFixed(2)}</td>
          <td style="color:${t.profit_loss>=0?'green':'red'}">
            ${t.profit_loss.toFixed(2)}
          </td>
        `;
        tbody.appendChild(tr);
      });
    } catch (e) { console.error(e) }
  }

  // Executa ao carregar a página
  loadUserTrades();
});