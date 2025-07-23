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
        <td>${d.change_24h.toFixed(2)}%</td>
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
    for (let sym in br) {
      const d = br[sym];
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${sym}</td>
        <td>${d.price.toFixed(2)}</td>
        <td>${d.change_24h.toFixed(2)}%</td>
        <td>${d.volume_24h}</td>
        <td>${d.rsi.toFixed(1)}</td>
      `;
      tbody.appendChild(tr);
    }
  }

  // Ações dos botões (ENTRADA, STOP, ALVO, AUTOMÁTICO)
  const botoes = document.querySelectorAll('.botao-acao');
  botoes.forEach(botao => {
    botao.addEventListener('click', () => {
      const acao = botao.getAttribute('data-acao');
      fetch('/executar_acao', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ acao })
      })
        .then(res => res.json())
        .then(data => {
          const divResposta = document.getElementById('resposta-ia');
          if (divResposta) {
            divResposta.innerHTML = `
              <h3>🤖 IA Clarinha respondeu:</h3>
              <p><strong>Ação:</strong> ${data.acao}</p>
              <p><strong>Resposta:</strong> ${data.resposta}</p>
            `;
          }
        })
        .catch(err => console.error('Erro ao executar ação:', err));
    });
  });
});