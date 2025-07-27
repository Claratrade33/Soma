// static/js/dashboard.js

document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    socket.on('connect', () => {
        socket.emit('subscribe_market');
    });

    socket.on('market_update', data => {
        updateCryptoTable(data.crypto);
        updateBrTable(data.brazilian);
    });

    function updateCryptoTable(crypto) {
        const tbody = document.querySelector('#crypto-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        for (let sym in crypto) {
            const d = crypto[sym];
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${sym}</td>
                <td>${d.price.toFixed(2)}</td>
                <td>${d.change_24h.toFixed(2)}%</td>
                <td>${d.volume_24h}</td>
                <td>${d.rsi.toFixed(1)}</td>
            `;
            tbody.appendChild(tr);
        }
    }

    function updateBrTable(br) {
        const tbody = document.querySelector('#br-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        for (let sym in br) {
            const d = br[sym];
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${sym}</td>
                <td>${d.price.toFixed(2)}</td>
                <td>${d.change_24h.toFixed(2)}%</td>
                <td>${d.volume_24h}</td>
                <td>${d.rsi.toFixed(1)}</td>
            `;
            tbody.appendChild(tr);
        }
    }
});

// Funções de Comandos Inteligentes
function executarEntrada() {
    alert("📥 Comando de ENTRADA enviado! IA Clarinha iniciando operação...");
    // Aqui pode ser feita chamada POST para rota de execução real
}

function executarStop() {
    alert("🛑 STOP acionado! A operação foi finalizada pela IA Clarinha.");
}

function executarAlvo() {
    alert("🎯 Alvo atingido! A IA Clarinha encerrou a operação com sucesso.");
}

function configurar() {
    window.location.href = "/configurar";
}

function ativarAuto() {
    alert("🤖 Modo automático ativado! A IA Clarinha está operando em tempo real.");
}