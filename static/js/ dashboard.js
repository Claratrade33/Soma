document.addEventListener("DOMContentLoaded", () => {
  const statusDiv = document.getElementById("status_operacao");
  const sugestaoDiv = document.getElementById("sugestao_ia");

  function atualizarStatus(mensagem) {
    statusDiv.textContent = mensagem;
  }

  function atualizarSugestao(dados) {
    if (dados.sugestao && typeof dados.sugestao === "object") {
      sugestaoDiv.innerHTML = `
        <p>📈 Sinal: <strong>${dados.sugestao.sinal}</strong></p>
        <p>🎯 Alvo: <strong>${dados.sugestao.alvo}</strong></p>
        <p>🛑 Stop: <strong>${dados.sugestao.stop}</strong></p>
        <p>🤖 Confiança: <strong>${(dados.sugestao.confianca * 100).toFixed(1)}%</strong></p>
      `;
    } else {
      sugestaoDiv.innerHTML = `<p>${dados.sugestao || 'Sugestão não disponível.'}</p>`;
    }
  }

  function enviarOrdem(acao) {
    fetch("/executar_ordem", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ acao: acao }),
    })
      .then((res) => res.json())
      .then((dados) => {
        atualizarStatus(dados.mensagem);
        atualizarSugestao(dados);
      })
      .catch((err) => {
        atualizarStatus("❌ Erro de conexão com o servidor.");
        console.error(err);
      });
  }

  // Botões
  document.getElementById("btn_entrada").addEventListener("click", () => enviarOrdem("ENTRADA"));
  document.getElementById("btn_stop").addEventListener("click", () => enviarOrdem("STOP"));
  document.getElementById("btn_alvo").addEventListener("click", () => enviarOrdem("ALVO"));
  document.getElementById("btn_executar").addEventListener("click", () => enviarOrdem("EXECUTAR"));
  document.getElementById("btn_auto").addEventListener("click", () => enviarOrdem("AUTOMATICO"));
});
