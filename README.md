# Projeto Django - Sistema de Gestão de Campanhas de Bônus

## 🚀 Visão Geral
Este projeto é um sistema web desenvolvido com Django para **gestão de campanhas de bônus vinculadas a bancos**, com controle de metas, vigência, repasses e histórico de alterações. Possui controle de permissão por usuário e interface responsiva.

---

## 🛠 Requisitos
- Python 3.10+
- pip (gerenciador de pacotes Python)
- Virtualenv ou `venv`
- PostgreSQL 

---

## 📁 Instalação Local

```bash
# 1. Clone o repositório
$ git clone <link-do-repositorio>
$ cd app_de_bonus

# 2. Crie e ative o ambiente virtual
$ python -m venv venv
$ source venv/bin/activate  # Linux/macOS
# ou venv\Scripts\activate.bat  # Windows

# 3. Instale as dependências
$ pip install -r requirements.txt

# 4. Rode as migrações
$ python manage.py migrate

# 5. Crie um superusuário para acessar o admin
$ python manage.py createsuperuser

# 6. Rode o servidor local
$ python manage.py runserver

# Acesse em: http://127.0.0.1:8000
```

---

## 🧱 Estrutura do Projeto

```
app_de_bonus/
├── campanhas/            # Cadastro de campanhas, bancos, metas
├── historico/            # Registros de alterações no sistema
├── usuarios/             # Login, autenticação e permissões
├── templates/            # HTMLs principais (com Tailwind CSS)
├── static/               # Arquivos estáticos (se houver)
├── app_de_bonus/         # Configurações gerais do projeto Django
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🔐 Acesso e Permissões
- Acesse a área administrativa via `/admin`
- Crie grupos de usuários conforme necessidade:
  - **Administrador**: acesso completo
  - **Gerente**: acesso a edição e criação
  - **Visualizador**: acesso somente leitura

---

## 📃 Principais Funcionalidades
- Cadastro de campanhas vinculadas a bancos
- Formulários condicionais (ex: "possui meta")
- Múltiplos formulários (faixas, repasses, vigência)
- Registro automático de histórico (criação, edição, exclusão)
- Interface responsiva com layout visual limpo

---

## 🛠 Deploy em Produção (recomendações)
- Configure `.env` com:
  - `SECRET_KEY`
  - `DEBUG=False`
  - `ALLOWED_HOSTS=["dominio.com"]`
  - `DATABASE_URL` (caso use PostgreSQL)
- Rode:
```bash
$ python manage.py collectstatic
```
- Use `gunicorn`, `nginx` ou `docker` se aplicável.
- Pode-se adaptar para Heroku, Render, Railway, EC2 ou servidor próprio.

---

## ⚠️ Observações Importantes
- Toda rota de edição e criação exige autenticação
- Algumas funções só aparecem para usuários com permissões específicas
- Menu lateral adapta-se conforme o tipo de usuário

---

## 📊 Apps e Suas Funções
| App        | Função Principal |
|------------|------------------|
| campanhas  | CRUD de campanhas e metas |
| historico  | Registro de ações e alterações |
| usuarios   | Login, permissões e acesso controlado |

---

## 📈 Contato e Suporte
Caso o time de TI precise de apoio para rodar ou publicar o sistema, entrar em contato com o desenvolvedor original:

> Guilherme – [Seu Email ou GitHub]

---

Tudo pronto! Basta seguir os passos acima para executar ou adaptar o deploy.
