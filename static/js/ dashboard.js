// static/js/dashboard.js

document.addEventListener('DOMContentLoaded', () => {
  const status = document.getElementById('status_operacao');
  const sugestao = document.getElementById('sugestao_ia');

  async function enviarAcao(acao) {
    status.innerText = `Enviando comando: ${acao}...`;

    try {
      const resposta = await fetch(`/executar_ordem`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ acao })
      });

      const dados = await resposta.json();
      status.innerText = dados.mensagem || "Comando executado.";
      if (dados.sugestao) {
        sugestao.innerHTML = `<p>${dados.sugestao}</p>`;
      }
    } catch (erro) {
      status.innerText = "Erro ao enviar comando.";
    }
  }

  document.getElementById('btn_entrada')?.addEventListener('click', () => enviarAcao("ENTRADA"));
  document.getElementById('btn_stop')?.addEventListener('click', () => enviarAcao("STOP"));
  document.getElementById('btn_alvo')?.addEventListener('click', () => enviarAcao("ALVO"));
  document.getElementById('btn_executar')?.addEventListener('click', () => enviarAcao("EXECUTAR"));
  document.getElementById('btn_auto')?.addEventListener('click', () => enviarAcao("AUTOMATICO"));
});
