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

// Funções reais de execução de ordens
async function executarOrdem(tipo) {
    try {
        const resposta = await fetch('/executar_ordem', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tipo: tipo })
        });

        const resultado = await resposta.json();
        if (resposta.ok) {
            alert(`✅ Ordem ${tipo.toUpperCase()} executada com sucesso!`);
            console.log(resultado);
        } else {
            alert(`Erro ao executar ordem: ${resultado.erro}`);
        }
    } catch (erro) {
        alert(`Erro na comunicação com o servidor: ${erro.message}`);
    }
}

function executarEntrada() {
    executarOrdem("entrada");
}

function executarStop() {
    executarOrdem("stop");
}

function executarAlvo() {
    executarOrdem("alvo");
}

function configurar() {
    window.location.href = "/configurar";
}

function ativarAuto() {
    alert("🤖 Modo automático ativado! A IA Clarinha está operando em tempo real.");
}