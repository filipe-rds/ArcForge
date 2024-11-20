# ArchForge

**ArchForge** é um framework web em Python minimalista e extensível, projetado para facilitar o desenvolvimento de aplicações usando boas práticas de programação e princípios como **GRASP** e **SOLID**.

## Funcionalidades

- Gerenciamento de dados com suporte a CRUD (Create, Read, Update, Delete).
- Migrações automáticas para PostgreSQL.
- Suporte a validações de dados e chaves estrangeiras.

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/archforge.git
   cd archforge
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente para o banco de dados:
   ```bash
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=seu_banco
   export DB_USER=seu_usuario
   export DB_PASSWORD=sua_senha
   ```
