// static/dashboard.js

document.addEventListener('DOMContentLoaded', () => {
  const sugestaoIa = document.getElementById('sugestao_ia');
  const statusOperacao = document.getElementById('status_operacao');

  // Exibe mensagens no painel
  function exibirStatus(mensagem, tipo = 'ok') {
    statusOperacao.textContent = mensagem;
    statusOperacao.style.color = tipo === 'erro' ? 'red' : '#00ff88';
  }

  // Função principal de execução de ordens
  window.executarOrdem = function (tipo) {
    exibirStatus(`⏳ Enviando ordem: ${tipo.toUpperCase()}...`);

    fetch('/executar_ordem', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ tipo: tipo })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'ok') {
        exibirStatus(`✅ Ordem ${tipo.toUpperCase()} executada com sucesso.`);
      } else {
        exibirStatus(`❌ Erro: ${data.erro}`, 'erro');
      }
    })
    .catch(error => {
      console.error(error);
      exibirStatus('❌ Erro de conexão com o servidor.', 'erro');
    });
  };
});