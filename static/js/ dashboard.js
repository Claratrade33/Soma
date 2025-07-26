document.addEventListener('DOMContentLoaded', () => {
  let modoAutomatico = false;
  let intervaloIA;

  async function chamarIA() {
    try {
      const resposta = await fetch('/ia');
      const dados = await resposta.json();
      document.getElementById('sugestao_ia').innerText = `
🔁 Sinal: ${dados.sinal}
🎯 Alvo: ${dados.alvo}
🛑 Stop: ${dados.stop}
📊 Confiança: ${dados.confianca}
      `.trim();
    } catch (erro) {
      document.getElementById('sugestao_ia').innerText = 'Erro ao buscar sugestão da IA.';
    }
  }

  async function executarOrdem(tipo) {
    if (tipo === 'automatico') {
      modoAutomatico = !modoAutomatico;
      const status = document.getElementById('status_operacao');
      if (modoAutomatico) {
        status.innerText = '🤖 Modo Automático ativado!';
        intervaloIA = setInterval(() => {
          chamarIA();
          fetch('/executar_ordem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo: 'auto' })
          });
        }, 60000); // a cada 60 segundos
      } else {
        clearInterval(intervaloIA);
        status.innerText = '❌ Modo Automático desativado.';
      }
      return;
    }

    try {
      const resposta = await fetch('/executar_ordem', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tipo })
      });

      const dados = await resposta.json();
      document.getElementById('status_operacao').innerText = `✅ ${dados.status}`;
    } catch (erro) {
      document.getElementById('status_operacao').innerText = 'Erro ao executar ordem.';
    }
  }

  // Torna as funções globais para os botões do HTML
  window.executarOrdem = executarOrdem;
});
