# IMS Doações — MVP de Gestão de Doações e Atendimentos

Projeto acadêmico desenvolvido por **Carlos Henrique Dias dos Santos** para a disciplina de **Projeto de Software**.

O MVP foi concebido para apoiar o fluxo de cadastro de famílias, controle de estoque e registro de entregas de alimentos no contexto do **Instituto Mãos Solidárias (IMS)**. Este repositório é um projeto acadêmico e **não representa um produto oficial nem uma declaração institucional do IMS**.

## Objetivo

Centralizar operações essenciais do atendimento social em uma aplicação web simples, responsiva e rastreável, reduzindo a dependência de registros dispersos e apoiando o controle das entregas e do estoque.

## ODS relacionado

**ODS 2 — Fome Zero e Agricultura Sustentável.** O software não resolve a insegurança alimentar de forma isolada; sua contribuição é operacional, apoiando organização, rastreabilidade e distribuição de alimentos no contexto local.

## Escopo do MVP

- autenticação de usuários autorizados;
- cadastro e consulta de famílias;
- consulta de itens e saldos de estoque;
- registro de entradas e saídas de estoque;
- registro de entrega vinculada à família;
- atualização transacional do estoque;
- tela de confirmação com itens e saldos atualizados;
- interface responsiva e requisitos básicos de acessibilidade.

Fora do escopo inicial: integração automática com WhatsApp, aplicativo móvel nativo, sistema financeiro/contábil e relatórios avançados.

## Arquitetura e tecnologias

- **Python 3.12** como padrão tecnológico principal;
- **Django 5.2 LTS**;
- **Bootstrap 5.3**;
- **PostgreSQL** como banco-alvo de implantação;
- arquitetura monolítica em camadas;
- autenticação do Django com **Argon2** como hasher preferencial;
- GitHub Actions para Integração Contínua.

Para facilitar a demonstração local, quando `DATABASE_URL` não está definido o projeto utiliza SQLite. O ambiente-alvo e o pipeline de CI utilizam PostgreSQL.

## Entidades principais

- `Family`: cadastro mínimo da família;
- `Item`: produto e saldo de estoque;
- `Delivery`: atendimento/entrega;
- `DeliveryItem`: itens de uma entrega;
- `StockMovement`: histórico de entradas e saídas.

## Executar localmente

### 1. Criar ambiente virtual

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Opção rápida com SQLite

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

### 3. Executar com PostgreSQL

```bash
docker compose up -d db
cp .env.example .env
export DATABASE_URL='postgresql://ims:ims@localhost:5432/ims'
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

> Não publique senhas, `.env`, credenciais ou chaves no GitHub.

## Testes automatizados

```bash
python manage.py test
```

Os testes verificam, entre outros pontos:

- exigência de autenticação;
- entrada de estoque;
- bloqueio de saída com saldo insuficiente;
- registro atômico de entrega;
- baixa correta dos itens no estoque;
- criação do histórico de entrega e movimentações.

## Integração Contínua

O workflow `.github/workflows/ci.yml` executa automaticamente em `push` e `pull_request` para `main`:

1. sobe PostgreSQL;
2. instala as dependências;
3. valida se existem migrações pendentes;
4. aplica migrações;
5. executa a suíte de testes.

## Segurança e acessibilidade

Medidas planejadas/implementadas no MVP:

- senhas armazenadas por hash robusto com Argon2;
- proteção CSRF nativa do Django;
- ORM para evitar concatenação direta de SQL;
- escape de templates contra XSS;
- autenticação exigida nas telas do MVP;
- cookies seguros em ambiente de produção;
- rótulos associados aos campos;
- foco visível;
- áreas de interação com pelo menos 44 px de altura;
- mensagens de sucesso/erro em texto, sem depender apenas de cor;
- layout responsivo para computador e smartphone.

## Fluxo central

1. usuário autenticado pesquisa a família;
2. seleciona **Registrar entrega**;
3. informa itens e quantidades;
4. o servidor valida disponibilidade;
5. a entrega, seus itens e as movimentações de estoque são gravados em transação única;
6. a tela de resultado informa o atendimento e os saldos atualizados.

## Dados de demonstração

O comando abaixo cria somente dados fictícios:

```bash
python manage.py seed_demo
```

Exemplos: `Maria Exemplo`, Arroz, Feijão e Macarrão.

## Versionamento sugerido para a atividade

O desenvolvimento pode ser demonstrado com branches e Pull Requests, por exemplo:

- `main` — versão estável;
- `feat/registro-entregas` — melhoria do fluxo central;
- Pull Request da branch de feature para `main`, com execução do CI antes do merge.

## Autor

**Carlos Henrique Dias dos Santos**
