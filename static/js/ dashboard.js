document.addEventListener('DOMContentLoaded', () => {
  obterSugestaoIA();

  const botoes = ['comprar', 'vender', 'stop', 'alvo', 'automatico'];
  botoes.forEach(acao => {
    const botao = document.querySelector(`button[onclick*="${acao}"]`);
    if (botao) {
      botao.addEventListener('click', () => executarOrdem(acao));
    }
  });
});

function obterSugestaoIA() {
  fetch('/sugestao_ia')
    .then(res => res.json())
    .then(data => {
      if (data.erro) {
        document.getElementById('sugestao_ia').innerText = 'Erro ao obter sugestão da IA';
      } else {
        document.getElementById('sugestao_ia').innerHTML = `
          <strong>Entrada:</strong> ${data.entrada}<br>
          <strong>Alvo:</strong> ${data.alvo}<br>
          <strong>Stop:</strong> ${data.stop}<br>
          <strong>Confiança:</strong> ${data.confianca}<br>
          <em>${data.sugestao}</em>
        `;
      }
    })
    .catch(() => {
      document.getElementById('sugestao_ia').innerText = 'Erro na comunicação com a IA.';
    });
}

function executarOrdem(tipo) {
  fetch('/executar_ordem', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tipo })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('status_operacao').innerText = `✅ ${data.status || data.resultado || 'Ordem executada com sucesso'}`;
    obterSugestaoIA();  // Atualiza sugestão após ordem
  })
  .catch(() => {
    document.getElementById('status_operacao').innerText = '❌ Erro ao executar a ordem';
  });
}