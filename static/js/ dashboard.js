document.addEventListener("DOMContentLoaded", () => {
  const sugDiv = document.querySelector(".sugestao-ia pre");

  fetch("/sugestao_ia")
    .then(res => res.json())
    .then(data => {
      if (data && !data.erro) {
        sugDiv.innerText = JSON.stringify(data, null, 2);
      } else {
        sugDiv.innerText = "⚠️ IA não respondeu. Verifique suas chaves.";
      }
    })
    .catch(() => {
      sugDiv.innerText = "⚠️ Erro ao obter sugestão da IA.";
    });
});