document.addEventListener('DOMContentLoaded', () => {
  const botoes = ['entrada', 'stop', 'alvo', 'automatico'];

  botoes.forEach(botao => {
    const el = document.querySelector(`button[onclick="enviarAcao('${botao}')"]`);
    if (el) {
      el.addEventListener('click', () => {
        enviarAcao(botao);
      });
    }
  });
});

function enviarAcao(acao) {
  fetch('/executar_acao', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ acao: acao })
  })
  .then(res => res.json())
  .then(data => {
    const saida = document.getElementById('output-ia');
    if (saida) {
      saida.innerText = data.mensagem || 'Resposta recebida.';
    }
  })
  .catch(err => {
    const saida = document.getElementById('output-ia');
    if (saida) {
      saida.innerText = 'Erro ao enviar ação para IA.';
    }
    console.error('Erro:', err);
  });
}