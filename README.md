# Constroiverse

Constroiverse é um ecossistema em desenvolvimento que pretende conectar
clientes, profissionais e fornecedores da construção civil em um único
ambiente digital. A proposta é oferecer um "iFood da construção" com
inteligência artificial para orçamentos, logística e gestão de obras.

Este repositório contém um protótipo inicial em Flask utilizado para
autenticação, armazenamento local de usuários e execução de rotas
simples. O objetivo desta etapa é fornecer um esqueleto funcional sobre
o qual os módulos específicos de cada perfil (cliente, mestre de obra,
lojista, engenheiro etc.) possam ser construídos.

## 🚀 Funcionalidades previstas

- **IA Clarice** – integrações futuras com a API da OpenAI para
  responder dúvidas, auxiliar em orçamentos e sugerir materiais.
- **Painéis por perfil** – telas diferentes para clientes, lojistas e
  profissionais da obra.
- **Financeiro** – controle de orçamento, previsão de gastos e cálculo
  de ROI por obra.
- **Logística** – uso da API do Google Maps para rotas de entrega e
  visualização em tempo real.
- **Orçamentos dinâmicos** – geração de propostas com base em listas de
  insumos ou upload de projetos.

## 🛠 Instalação

1. Crie um ambiente virtual e instale as dependências:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copie o arquivo de exemplo de variáveis de ambiente e ajuste os
   valores:

   ```bash
   cp .env.example .env
   ```

3. Execute a aplicação Flask:

   ```bash
   flask --app app.py run
   ```

## 📦 Estrutura

```
static/        # arquivos estáticos (CSS, JS)
templates/     # páginas HTML
app.py         # rotas básicas e autenticação
users.json     # armazenamento local de usuários (criptografado)
orders.json    # histórico de ordens executadas
```

## 🔑 Variáveis de ambiente

O arquivo `.env.example` lista as principais chaves utilizadas pelo
projeto. Preencha-as com os valores corretos antes de executar em
produção.

## 🔭 Próximos passos

- CRUD completo de obras, tarefas e profissionais.
- Integração real com OpenAI e Google Maps.
- Autenticação JWT e banco PostgreSQL.
- Painéis específicos para cada perfil de usuário.
- Automação de pedidos para fornecedores parceiros.

## 📝 Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo
`LICENSE` (a ser criado) para mais informações.

