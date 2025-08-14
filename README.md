# Bacelar Advocacia - Backend API

Sistema de gestão de prazos para escritório de advocacia.

## 🚀 Deploy no Render

### Pré-requisitos
1. Conta no [Render](https://render.com)
2. Repositório GitHub com o código
3. Credenciais do Firebase (para notificações)

### Passos para Deploy

#### 1. Configurar Variáveis de Ambiente
No Render Dashboard, crie um Environment Group chamado `bacelar-env` com as seguintes variáveis:

```env
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
SUPERUSER_EMAIL=admin@bacelar.adv.br
SUPERUSER_PASSWORD=sua_senha_segura
FRONTEND_URL=https://seu-frontend.vercel.app
FIREBASE_CREDENTIALS_JSON={"seu":"json_do_firebase"}
GOOGLE_API_KEY=sua_chave_google_ai
```

#### 2. Criar Serviços no Render

1. **Banco de Dados PostgreSQL**
   - Nome: `bacelar-db`
   - Plano: Basic 256MB ou superior

2. **Redis**
   - Nome: `bacelar-redis`
   - Plano: Free

3. **API Web Service**
   - Nome: `bacelar-api`
   - Environment: Docker
   - Build Command: (automático)
   - Start Command: (definido no Dockerfile)
   - Environment Variables: Link ao grupo `bacelar-env`
   - Database: Link ao `bacelar-db`
   - Redis: Link ao `bacelar-redis`

4. **Celery Worker**
   - Nome: `bacelar-celery-worker`
   - Environment: Docker
   - Docker Command: `celery -A app.worker worker --loglevel=info`
   - Environment Variables: Link ao grupo `bacelar-env`

5. **Celery Beat**
   - Nome: `bacelar-celery-beat`
   - Environment: Docker
   - Docker Command: `celery -A app.worker beat --loglevel=info`
   - Environment Variables: Link ao grupo `bacelar-env`

#### 3. Deploy Automático
O arquivo `render.yaml` está configurado para deploy automático. Basta fazer push para o repositório GitHub conectado.

## 🛠️ Desenvolvimento Local

### Instalação
```bash
# Clone o repositório
git clone <seu-repositorio>
cd bacelar-advocacia

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Execute as migrações
alembic upgrade head

# Crie o superusuário
python -m app.scripts.create_superuser

# Inicie o servidor
uvicorn app.main:app --reload
```

### Docker Compose (Desenvolvimento)
```bash
docker-compose up -d
```

## 📋 Funcionalidades

- ✅ Autenticação JWT
- ✅ Gestão de usuários
- ✅ Gestão de prazos
- ✅ Notificações automáticas
- ✅ Dashboard com estatísticas
- ✅ Upload de anexos
- ✅ Importação de planilhas Excel
- ✅ Integração com Firebase (notificações push)
- ✅ Integração com Google AI (classificação automática)

## 🔧 Tecnologias

- **Framework**: FastAPI
- **Banco de Dados**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrações**: Alembic
- **Autenticação**: JWT
- **Tarefas Assíncronas**: Celery + Redis
- **Notificações**: Firebase Admin SDK
- **IA**: Google Gemini API
- **Deploy**: Docker + Render

## 📝 API Documentation

Após o deploy, a documentação da API estará disponível em:
- Swagger UI: `https://sua-api.onrender.com/docs`
- ReDoc: `https://sua-api.onrender.com/redoc`

## 🔒 Segurança

- Senhas hasheadas com bcrypt
- Tokens JWT com expiração
- CORS configurado
- Validação de dados com Pydantic
- Variáveis de ambiente para credenciais

## 📞 Suporte

Para dúvidas ou problemas, consulte os logs no Render Dashboard ou entre em contato com a equipe de desenvolvimento.