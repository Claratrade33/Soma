document.addEventListener("DOMContentLoaded", function () {
    atualizarDados();

    document.getElementById("consultarIA").addEventListener("click", consultarIA);
});

function atualizarDados() {
    fetch("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT")
        .then(response => response.json())
        .then(data => {
            document.getElementById("preco").textContent = parseFloat(data.lastPrice).toFixed(2);
            document.getElementById("variacao").textContent = parseFloat(data.priceChangePercent).toFixed(2) + "%";
            document.getElementById("volume").textContent = parseFloat(data.volume).toFixed(2);
        })
        .catch(error => console.error("Erro ao buscar dados da Binance:", error));
}

function consultarIA() {
    const respostaIA = document.getElementById("resposta-ia");
    respostaIA.innerHTML = "🔄 Consultando Clarinha...";

    fetch('/consultar_mercado')
        .then(response => response.json())
        .then(data => {
            if (data.erro) {
                respostaIA.innerHTML = `<span style="color: red;">❌ ${data.erro}</span>`;
            } else {
                respostaIA.innerHTML = `
                    <b>📊 Estratégia da Clarinha:</b><br><br>
                    ⚡ <b>Entrada:</b> ${data.entrada}<br>
                    🎯 <b>Alvo:</b> ${data.alvo}<br>
                    🛑 <b>Stop:</b> ${data.stop}<br>
                    🌟 <b>Confiança:</b> ${data.confianca}<br><br>
                    🔮 <i>${data.mensagem}</i>
                `;
            }
        })
        .catch(error => {
            console.error("Erro ao consultar IA:", error);
            respostaIA.innerHTML = `<span style="color: red;">Erro ao consultar IA</span>`;
        });
}