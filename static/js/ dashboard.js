document.addEventListener('DOMContentLoaded', () => {
  const socket = io();

  // Conecta e assina o canal de dados
  socket.on('connect', () => {
    socket.emit('subscribe_market');
  });

  // Recebe dados do mercado e atualiza a tabela de cripto
  socket.on('market_update', data => {
    updateCryptoTable(data.crypto);
  });

  function updateCryptoTable(crypto) {
    const tbody = document.querySelector('#crypto-table tbody');
    if (!tbody) return;

    tbody.innerHTML = '';
    for (let symbol in crypto) {
      const d = crypto[symbol];
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${symbol}</td>
        <td>${d.price.toFixed(2)}</td>
        <td>${d.change_24h.toFixed(2)}%</td>
        <td>${d.volume_24h}</td>
        <td>${d.rsi.toFixed(1)}</td>
      `;
      tbody.appendChild(tr);
    }
  }

  // Mostra alerta de conexão
  socket.on('connect_error', () => {
    alert("Erro de conexão com o servidor. Verifique sua internet.");
  });
});