document.addEventListener('DOMContentLoaded', function () {
  const sugestaoDiv = document.getElementById("sugestao_ia");
  const status = document.getElementById("status_operacao");

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

  function feedback(botao) {
    if (status) status.innerText = `✅ Comando "${bot
