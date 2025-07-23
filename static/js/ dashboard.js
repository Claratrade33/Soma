document.addEventListener('DOMContentLoaded', () => {
  const socket = io();

  socket.on('connect', () => {
    socket.emit('subscribe_market');
  });

  socket.on('market_update', data => {
    updateCryptoTable(data.crypto);
    updateBrTable(data.brazilian);
  });

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
        <td>-</td>
        <td>-</td>
        <td>-</td>
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
        <td>-</td>
      `;
      tbody.appendChild(tr);
    }
  }

  const analyzeForm = document.getElementById('analyze-form');
  if (analyzeForm) {
    analyzeForm.addEventListener('submit', async e => {
      e.preventDefault();
      const symbol = analyzeForm.symbol.value;
      const res = await fetch('/api/intelligent_analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol })
      });
      const body = await res.json();
      document.getElementById('analysis-output').innerText =
        JSON.stringify(body, null, 2);
    });
  }

  const tradeForm = document.getElementById('trade-form');
  if (tradeForm) {
    tradeForm.addEventListener('submit', async e => {
      e.preventDefault();
      const symbol = tradeForm.symbol.value;
      const side = tradeForm.side.value;
      const qty = tradeForm.quantity.value;
      const res = await fetch('/api/execute_trade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, side, quantity: qty })
      });
      const b = await res.json();
      alert(b.success ? `✅ P&L: ${b.pnl.toFixed(2)}` : `❌ Erro: ${b.error}`);
    });
  }
});