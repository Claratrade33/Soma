document.addEventListener("DOMContentLoaded", function() {
    // Exemplo de como executar uma ordem usando AJAX
    const executarOrdemForm = document.getElementById("executar-ordem-form");

    if (executarOrdemForm) {
        executarOrdemForm.addEventListener("submit", function(event) {
            event.preventDefault(); // Evita o envio padrão do formulário

            const tipo = document.querySelector('input[name="tipo"]:checked').value;
            const simbolo = document.getElementById("simbolo").value;
            const quantidade = document.getElementById("quantidade").value;

            // Chamada AJAX para executar a ordem
            fetch("/executar_ordem", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    tipo: tipo,
                    simbolo: simbolo,
                    quantidade: quantidade
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status) {
                    alert(data.status); // Exibe mensagem de sucesso
                } else {
                    alert("Erro: " + data.erro); // Exibe mensagem de erro
                }
            })
            .catch(error => {
                console.error("Erro:", error);
                alert("Ocorreu um erro ao executar a ordem.");
            });
        });
    }

    // Exemplo de chamada AJAX para obter sugestão da IA
    const iaSugestaoBtn = document.getElementById("ia-sugestao-btn");

    if (iaSugestaoBtn) {
        iaSugestaoBtn.addEventListener("click", function() {
            fetch("/ia_sugestao")
            .then(response => response.json())
            .then(data => {
                // Exibir a sugestão em algum elemento da página
                const sugestaoContainer = document.getElementById("sugestao-container");
                sugestaoContainer.innerHTML = data.mensagem || "Nenhuma sugestão disponível.";
            })
            .catch(error => {
                console.error("Erro:", error);
                alert("Ocorreu um erro ao obter a sugestão.");
            });
        });
    }
});