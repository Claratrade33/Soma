document.addEventListener('DOMContentLoaded', () => {
  const socket = io();

  // === Atualização ao conectar ===
  socket.on('connect', () => {
    socket.emit('subscribe_market');
  });

  // === Recebe dados de mercado ===
  socket.on('market_update', (data) => {
    if (data && data.price && document.getElementById('preco_atual')) {
      document.getElementById('preco_atual').innerText = `${parseFloat(data.price).toFixed(2)} USDT`;
    }
    if (data && data.rsi && document.getElementById('rsi_valor')) {
      document.getElementById('rsi_valor').innerText = `${parseFloat(data.rsi).toFixed(2)}`;
    }
    if (data && data.suporte && document.getElementById('suporte_valor')) {
      document.getElementById('suporte_valor').innerText = `${parseFloat(data.suporte).toFixed(2)}`;
    }
    if (data && data.resistencia && document.getElementById('resistencia_valor')) {
      document.getElementById('resistencia_valor').innerText = `${parseFloat(data.resistencia).toFixed(2)}`;
    }
  });

  // === Seleciona botões e elementos ===
  const btnEntrada = document.getElementById('btn_entrada');
  const btnStop = document.getElementById('btn_stop');
  const btnAlvo = document.getElementById('btn_alvo');
  const btnExecutar = document.getElementById('btn_executar');
  const btnAuto = document.getElementById('btn_auto');

  const statusDiv = document.getElementById('status_operacao');
  const iaDiv = document.getElementById('sugestao_ia');

  const atualizarStatus = (mensagem) => {
    if (statusDiv) {
      statusDiv.innerText = mensagem;
      statusDiv.style.color = '#00ff88';
    }
  };

  const exibirSugestaoIA = (sugestao) => {
    if (iaDiv) {
      iaDiv.innerHTML = `
        <div style="border: 1px solid #00ffff; padding: 10px; border-radius: 8px;">
          <p><strong>Sinal:</strong> ${sugestao.sinal}</p>
          <p><strong>Alvo:</strong> ${sugestao.alvo}</p>
          <p><strong>Stop:</strong> ${sugestao.stop}</p>
          <p><strong>Confiança:</strong> ${sugestao.confianca}</p>
        </div>
      `;
    }
  };

  const executarAcao = (acao) => {
    fetch(`/executar_ordem`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ acao })
    })
    .then(res => res.json())
    .then(data => {
      atualizarStatus(data.status || 'Operação realizada');
    })
    .catch(() => {
      atualizarStatus('Erro ao executar operação.');
    });
  };

  // === Ações dos botões ===
  if (btnEntrada) btnEntrada.addEventListener('click', () => executarAcao('entrada'));
  if (btnStop) btnStop.addEventListener('click', () => executarAcao('stop'));
  if (btnAlvo) btnAlvo.addEventListener('click', () => executarAcao('alvo'));
  if (btnExecutar) btnExecutar.addEventListener('click', () => executarAcao('executar'));
  if (btnAuto) btnAuto.addEventListener('click', () => executarAcao('automatico'));

  // === Sugestão da IA Clarinha ===
  fetch('/sugestao_ia')
    .then(res => res.json())
    .then(data => {
      if (data && data.sinal) {
        exibirSugestaoIA(data);
      } else {
        iaDiv.innerHTML = '<p>Nenhuma sugestão disponível no momento.</p>';
      }
    })
    .catch(() => {
      iaDiv.innerHTML = '<p>Erro ao carregar sugestão da IA.</p>';
    });
});