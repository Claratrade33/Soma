document.addEventListener('DOMContentLoaded', function () {
  const sugestaoDiv = document.getElementById("sugestao_ia");
  const status = document.getElementById("status_operacao");

  // Atualiza sugestão da IA se estiver carregando
  if (sugestaoDiv && sugestaoDiv.innerText.includes("Carregando")) {
    fetch("/painel_operacao")
      .then(r => r.text())
      .then(html => {
        const temp = document.createElement("div");
        temp.innerHTML = html;
        const novaSugestao = temp.querySelector("#sugestao_ia");
        if (novaSugestao) {
          sugestaoDiv.innerHTML = novaSugestao.innerHTML;
        }
      });
  }

  // Feedback ao clicar nos botões
  function feedback(mensagem) {
    if (status) status.innerText = `✅ ${mensagem}`;
  }

  window.executarOrdem = function(tipo) {
    fetch("/executar_ordem", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tipo })
    })
    .then(res => res.json())
    .then(data => {
      feedback(`Ordem de ${tipo.toUpperCase()} enviada`);
    })
    .catch(err => {
      feedback("Erro ao executar ordem");
    });
  }

  window.ativarModoAutomatico = function() {
    fetch("/ativar_automatico", { method: "POST" })
      .then(res => res.json())
      .then(data => {
        feedback("Modo automático ativado");
      })
      .catch(err => {
        feedback("Erro ao ativar automático");
      });
  }
});
