from clarinha_core import clarinha_responder

# Exemplo de pergunta intuitiva do usuário
pergunta = "O mercado está favorável para entrar em Ethereum hoje?"
simbolo = "ETHUSDT"
gerar_imagem = True  # Gera uma imagem simbólica junto

resposta = clarinha_responder(pergunta, simbolo, gerar_imagem)

print("🪄 Resposta filosófica:")
print(resposta["resposta_guardian"])
print("\n📊 Análise técnica:")
print(resposta["analise_operacional"])
print("\n🎨 Imagem oracular:")
print(resposta["imagem_oracular"])
