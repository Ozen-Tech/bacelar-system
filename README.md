# 🏛️ Bacelar Legal Intelligence

> Sistema completo de gestão de prazos jurídicos com inteligência artificial integrada

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Sobre o Projeto

O **Bacelar Legal Intelligence** é uma solução completa para escritórios de advocacia, desenvolvida para otimizar o gerenciamento de prazos processuais e automatizar tarefas administrativas através de inteligência artificial.

### ✨ Principais Funcionalidades

- 📅 **Gestão Inteligente de Prazos** - Controle completo de deadlines com alertas automáticos
- 🤖 **IA Integrada** - Classificação automática de documentos e sugestões inteligentes
- 📊 **Dashboard Analítico** - Visualizações em tempo real com métricas importantes
- 📱 **Notificações Push** - Alertas via Firebase Cloud Messaging
- 📄 **Exportação Avançada** - Relatórios em Excel e PDF com marca d'água
- 👥 **Gestão de Usuários** - Sistema completo de autenticação e autorização
- 📎 **Anexos de Documentos** - Upload e gerenciamento de arquivos
- 🔍 **Filtros Avançados** - Busca e filtragem inteligente de dados
- 📈 **Histórico Completo** - Rastreamento de todas as alterações

## 🛠️ Stack Tecnológica

### Backend
- **FastAPI** - Framework web moderno e de alta performance
- **SQLAlchemy** - ORM para Python com suporte a async
- **PostgreSQL** - Banco de dados relacional robusto
- **Alembic** - Migrações de banco de dados
- **Celery** - Processamento de tarefas assíncronas
- **Redis** - Cache e message broker
- **OpenAI API** - Integração com inteligência artificial
- **Firebase Admin** - Notificações push

### Frontend
- **React 18** - Biblioteca para interfaces de usuário
- **TypeScript** - Superset tipado do JavaScript
- **Vite** - Build tool moderna e rápida
- **Tailwind CSS** - Framework CSS utility-first
- **Recharts** - Biblioteca de gráficos para React
- **Lucide React** - Ícones modernos e consistentes
- **React Router** - Roteamento para SPAs

### DevOps & Deploy
- **Docker** - Containerização da aplicação
- **Docker Compose** - Orquestração de containers
- **Render** - Plataforma de deploy em nuvem
- **GitHub Actions** - CI/CD automatizado

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis
- Docker (opcional)

### 🐳 Instalação com Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/bacelar-advocacia.git
cd bacelar-advocacia

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Execute com Docker Compose
docker-compose up -d

# Execute as migrações
docker-compose exec api alembic upgrade head

# Crie um superusuário
docker-compose exec api python app/scripts/create_superuser.py
```

### 💻 Instalação Manual

#### Backend

```bash
# Instale as dependências Python
pip install -r requirements.txt

# Configure o banco de dados
export DATABASE_URL="postgresql://user:password@localhost/bacelar_db"

# Execute as migrações
alembic upgrade head

# Inicie o servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
# Navegue para o diretório frontend
cd ../bacelar-advocacia-frontend

# Instale as dependências
npm install

# Configure as variáveis de ambiente
cp .env.example .env.local
# Edite o arquivo .env.local

# Inicie o servidor de desenvolvimento
npm run dev
```

## 🔧 Configuração

### Variáveis de Ambiente

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost/bacelar_db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
FIREBASE_CREDENTIALS_JSON={"your":"firebase-config"}
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
SUPERUSER_EMAIL=admin@bacelar.adv.br
SUPERUSER_PASSWORD=your-secure-password
FRONTEND_URL=http://localhost:5173
```

#### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_CONFIG=your-firebase-config-json
```

## 📱 Funcionalidades Detalhadas

### 🎯 Dashboard Inteligente
- Métricas em tempo real de prazos
- Gráficos interativos de status
- Cards informativos com estatísticas
- Filtros dinâmicos por período

### ⚡ Gestão de Prazos
- Criação e edição de prazos processuais
- Classificação automática por urgência
- Atribuição de responsáveis
- Histórico completo de alterações
- Anexos de documentos
- Importação via Excel

### 🔔 Sistema de Notificações
- Alertas automáticos por email
- Notificações push no navegador
- Configuração personalizada de lembretes
- Central de notificações integrada

### 📊 Relatórios e Exportação
- Exportação para Excel com formatação
- Geração de PDFs profissionais
- Marca d'água automática "BACELAR LEGAL INTELLIGENCE"
- Filtros avançados para relatórios
- Ações em lote para múltiplos prazos

### 🤖 Inteligência Artificial
- Classificação automática de documentos
- Sugestões de prazos baseadas em histórico
- Análise de padrões processuais
- Otimização de fluxos de trabalho

## 🏗️ Arquitetura

```
bacelar-advocacia/
├── app/                    # Backend FastAPI
│   ├── api/               # Endpoints da API
│   │   └── endpoints/     # Rotas organizadas
│   ├── core/              # Configurações centrais
│   ├── db/                # Configuração do banco
│   ├── models/            # Modelos SQLAlchemy
│   │   ├── user/          # Modelo de usuários
│   │   ├── deadline/      # Modelo de prazos
│   │   ├── notification/  # Modelo de notificações
│   │   ├── attachment/    # Modelo de anexos
│   │   └── history/       # Modelo de histórico
│   ├── schemas/           # Schemas Pydantic
│   ├── services/          # Lógica de negócio
│   └── scripts/           # Scripts utilitários
├── alembic/               # Migrações do banco
├── bacelar-advocacia-frontend/  # Frontend React
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   │   ├── Dashboard/ # Componentes do dashboard
│   │   │   ├── Forms/     # Formulários
│   │   │   └── Layout/    # Layout da aplicação
│   │   ├── pages/         # Páginas da aplicação
│   │   ├── services/      # Serviços de API
│   │   ├── context/       # Contextos React
│   │   └── styles/        # Estilos CSS
├── docker-compose.yml     # Orquestração Docker
└── requirements.txt       # Dependências Python
```

## 🧪 Testes

```bash
# Testes do backend
pytest

# Testes do frontend
cd bacelar-advocacia-frontend
npm test

# Coverage
pytest --cov=app
```

## 📈 Performance

- **Backend**: FastAPI com performance superior a Flask/Django
- **Frontend**: Vite para builds ultra-rápidos
- **Database**: PostgreSQL com índices otimizados
- **Cache**: Redis para cache de sessões e dados frequentes
- **Async**: Operações assíncronas para melhor performance

## 🔒 Segurança

- Autenticação JWT com refresh tokens
- Criptografia de senhas com bcrypt
- Validação de dados com Pydantic
- Sanitização de inputs
- Rate limiting nas APIs
- CORS configurado adequadamente
- Validação de permissões por perfil

## 🚀 Deploy

### Render (Produção)

#### 1. Configurar Variáveis de Ambiente
No Render Dashboard, crie um Environment Group chamado `bacelar-env`:

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

1. **PostgreSQL Database**
   - Nome: `bacelar-db`
   - Plano: Basic 256MB+

2. **Redis**
   - Nome: `bacelar-redis`
   - Plano: Free

3. **API Web Service**
   - Nome: `bacelar-api`
   - Environment: Docker
   - Environment Variables: Link ao grupo `bacelar-env`

4. **Celery Worker**
   - Nome: `bacelar-celery-worker`
   - Docker Command: `celery -A app.worker worker --loglevel=info`

### Docker em Produção

```bash
# Build das imagens
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Métricas e Monitoramento

- Logs estruturados com FastAPI
- Monitoramento de performance
- Alertas automáticos de erro
- Métricas de uso da aplicação

## 🔄 CI/CD

- GitHub Actions para deploy automático
- Testes automatizados em PRs
- Build e deploy contínuo
- Rollback automático em caso de falha

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Desenvolvedor

**Desenvolvido por:** Especialista em Desenvolvimento Full Stack
- **Tecnologias:** Python, FastAPI, React, TypeScript, PostgreSQL
- **Especialidades:** Sistemas jurídicos, IA, Arquitetura de software
- **Experiência:** Desenvolvimento de soluções empresariais complexas

## 🤝 Contribuições

Contribuições são sempre bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para suporte técnico:

1. Verifique a documentação
2. Consulte as issues existentes
3. Crie uma nova issue se necessário
4. Entre em contato para consultoria

---

<div align="center">
  <strong>🏛️ Desenvolvido com ❤️ para otimizar a gestão jurídica 🏛️</strong>
  <br><br>
  <em>"Transformando a advocacia através da tecnologia e inteligência artificial"</em>
</div>