async function executarAcao(acao) {
    try {
        const resposta = await fetch('/executar_acao', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ acao: acao })
        });

        const resultado = await resposta.json();

        if (resultado.status) {
            alert(resultado.status);
            location.reload(); // Atualiza o saldo simulado
        } else {
            alert(resultado.erro || "Erro desconhecido.");
        }

    } catch (error) {
        alert("Erro ao executar ação: " + error);
    }
}

async function obterSugestaoIA() {
    const respostaDiv = document.getElementById("resposta-ia");
    respostaDiv.innerHTML = "🔄 Clarinha está analisando...";

    try {
        const resposta = await fetch('/obter_sugestao_ia', {
            method: 'GET'
        });
        const json = await resposta.json();

        if (json.erro) {
            respostaDiv.innerHTML = "⚠️ " + json.erro;
            return;
        }

        respostaDiv.innerHTML = `
            <div class="ia-sugestao">
                <p>⚡ <strong>Entrada:</strong> ${json.entrada}</p>
                <p>🎯 <strong>Alvo:</strong> ${json.alvo}</p>
                <p>🛑 <strong>Stop:</strong> ${json.stop}</p>
                <p>🌟 <strong>Confiança:</strong> ${json.confianca}</p>
                <p>📢 <strong>Mensagem:</strong> ${json.mensagem}</p>
            </div>
        `;

    } catch (error) {
        respostaDiv.innerHTML = "❌ Erro ao consultar a IA: " + error;
    }
}