// static/js/dashboard.js
async function executarOrdem(tipo) {
    try {
        const resposta = await fetch('/executar_ordem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo })
        });
        const resultado = await resposta.json();
        if (resposta.ok) {
            alert(`✅ Ordem ${tipo.toUpperCase()} executada com sucesso!`);
        } else {
            alert(`🚨 Erro: ${resultado.erro}`);
        }
    } catch (e) {
        alert(`🚨 Falha na comunicação: ${e.message}`);
    }
}

function ativarAuto() {
    alert("🤖 Modo automático ativado!");
}
