// static/js/dashboard.js

document.addEventListener('DOMContentLoaded', () => {
  const socket = io();

  // Conectar ao WebSocket para atualizações de mercado
  socket.on('connect', () => {
    socket.emit('subscribe_market');
  });

  socket.on('market_update', data => {
    atualizarTabelaCripto(data.crypto);
    atualizarTabelaBrasil(data.brazilian);
  });

  function atualizarTabelaCripto(crypto) {
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

  function atualizarTabelaBrasil(br) {
    const tbody = document.querySelector('#br-table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    for (let sym in br) {
      const d = br[sym];
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

  // === BOTÕES DO PAINEL ===
  document.querySelectorAll('[data-acao]').forEach(botao => {
    botao.addEventListener('click', () => {
      const acao = botao.getAttribute('data-acao');
      fetch('/executar_acao', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ acao })
      })
      .then(res => res.json())
      .then(data => {
        const resposta = document.getElementById('resposta-ia');
        if (resposta) resposta.innerText = data.mensagem || 'Executado';
      })
      .catch(() => alert('Erro ao executar ação'));
    });
  });

  // IA Clarinha - Atualização automática da sugestão
  const sugestao = document.getElementById('sugestao-ia');
  if (sugestao) {
    setInterval(() => {
      fetch('/ia/sugestao')
        .then(res => res.json())
        .then(data => {
          sugestao.innerHTML = `
            <b>🔮 Oráculo:</b> ${data.oraculo.prediction} (${data.oraculo.sentiment})<br>
            <b>🧠 Cosmo:</b> ${data.cosmo.cosmic_signal} (Confiança ${data.cosmo.confidence})<br>
            <b>Risco:</b> ${data.cosmo.risk} | Volume: ${data.cosmo.volume}
          `;
        });
    }, 15000); // Atualiza a cada 15s
  }
});