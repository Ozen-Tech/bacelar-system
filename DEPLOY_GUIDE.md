# 🚀 Guia Completo de Deploy - Bacelar Advocacia

Este guia contém todas as instruções para fazer o deploy completo da aplicação Bacelar Advocacia (Backend + Frontend).

## 📋 Visão Geral

- **Backend**: FastAPI + PostgreSQL + Redis + Celery (Deploy no Render)
- **Frontend**: React + TypeScript + Vite (Deploy na Vercel)
- **Integração**: CORS configurado + Variáveis de ambiente

## 🎯 Pré-requisitos

1. ✅ Conta no [GitHub](https://github.com)
2. ✅ Conta no [Render](https://render.com) (para backend)
3. ✅ Conta na [Vercel](https://vercel.com) (para frontend)
4. ✅ Git instalado localmente
5. ✅ Node.js e npm instalados

## 📦 Parte 1: Deploy do Backend (Render)

### 1.1 Preparar Repositório do Backend

```bash
# Navegar para o diretório do backend
cd /Users/ozen/bacelar-advocacia

# Executar script de inicialização do Git
./init-git.sh
```

### 1.2 Criar Repositório no GitHub

1. Acesse [GitHub](https://github.com/new)
2. Crie um repositório chamado `bacelar-advocacia-backend`
3. **NÃO** inicialize com README (já temos os arquivos)
4. Copie a URL do repositório

### 1.3 Conectar ao GitHub

```bash
# Adicionar repositório remoto (substitua pela sua URL)
git remote add origin https://github.com/SEU_USUARIO/bacelar-advocacia-backend.git
git branch -M main
git push -u origin main
```

### 1.4 Deploy no Render

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em **"New"** → **"Blueprint"**
3. Conecte seu repositório GitHub
4. O Render detectará o arquivo `render.yaml`
5. Configure as variáveis de ambiente:

```env
# Segurança (OBRIGATÓRIO - gere uma chave forte)
SECRET_KEY=sua-chave-secreta-de-32-caracteres-ou-mais
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Superusuário (OBRIGATÓRIO)
SUPERUSER_EMAIL=admin@bacelar.com
SUPERUSER_PASSWORD=SuaSenhaSegura123!

# Firebase (OPCIONAL - se usar notificações push)
FIREBASE_CREDENTIALS_PATH=/opt/render/project/src/firebase-credentials.json

# Frontend URL (será preenchido após deploy do frontend)
FRONTEND_URL=https://seu-frontend.vercel.app
```

6. Clique em **"Apply"** para iniciar o deploy
7. Aguarde a criação dos serviços (5-10 minutos)

### 1.5 Verificar Deploy do Backend

Após o deploy, você terá:
- 📊 **PostgreSQL**: Banco de dados
- 🔴 **Redis**: Cache e filas
- 🌐 **API Web Service**: `https://bacelar-api.onrender.com`
- 👷 **Celery Worker**: Tarefas em background
- ⏰ **Celery Beat**: Tarefas agendadas

**Teste a API**: Acesse `https://bacelar-api.onrender.com/docs`

## 🎨 Parte 2: Deploy do Frontend (Vercel)

### 2.1 Preparar Repositório do Frontend

```bash
# Navegar para o diretório do frontend
cd /Users/ozen/bacelar-advocacia-frontend

# Executar script de inicialização do Git
./init-git.sh
```

### 2.2 Criar Repositório no GitHub

1. Acesse [GitHub](https://github.com/new)
2. Crie um repositório chamado `bacelar-advocacia-frontend`
3. **NÃO** inicialize com README
4. Copie a URL do repositório

### 2.3 Conectar ao GitHub

```bash
# Adicionar repositório remoto (substitua pela sua URL)
git remote add origin https://github.com/SEU_USUARIO/bacelar-advocacia-frontend.git
git branch -M main
git push -u origin main
```

### 2.4 Deploy na Vercel

1. Acesse [Vercel Dashboard](https://vercel.com/dashboard)
2. Clique em **"New Project"**
3. Importe seu repositório GitHub
4. Configure:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 2.5 Configurar Variáveis de Ambiente

Na Vercel Dashboard → Settings → Environment Variables:

```env
VITE_API_BASE_URL=https://bacelar-api.onrender.com
```

**⚠️ IMPORTANTE**: Substitua `bacelar-api.onrender.com` pela URL real da sua API do Render.

### 2.6 Fazer Deploy

1. Clique em **"Deploy"**
2. Aguarde o build (2-5 minutos)
3. Sua aplicação estará em: `https://seu-projeto.vercel.app`

## 🔗 Parte 3: Integração Backend + Frontend

### 3.1 Atualizar URL do Frontend no Backend

1. Acesse o Render Dashboard
2. Vá para o serviço da API
3. Em **Environment**, atualize:

```env
FRONTEND_URL=https://seu-projeto.vercel.app
```

4. Salve e aguarde o redeploy automático

### 3.2 Testar Integração

1. ✅ Acesse o frontend deployado
2. ✅ Faça login com as credenciais do superusuário
3. ✅ Teste criar um novo prazo
4. ✅ Verifique se as notificações funcionam
5. ✅ Teste upload de arquivos
6. ✅ Verifique o dashboard com estatísticas

## 🛠️ Comandos Úteis

### Atualizar Backend
```bash
cd /Users/ozen/bacelar-advocacia
git add .
git commit -m "Update: descrição da mudança"
git push
# Deploy automático no Render
```

### Atualizar Frontend
```bash
cd /Users/ozen/bacelar-advocacia-frontend
git add .
git commit -m "Update: descrição da mudança"
git push
# Deploy automático na Vercel
```

## 🚨 Troubleshooting

### Backend não inicia
1. ✅ Verifique as variáveis de ambiente
2. ✅ Confirme se o PostgreSQL foi criado
3. ✅ Verifique os logs no Render
4. ✅ Teste a conexão com o banco

### Frontend não conecta com a API
1. ✅ Verifique se `VITE_API_BASE_URL` está correta
2. ✅ Confirme se o backend está funcionando
3. ✅ Teste a API diretamente: `/docs`
4. ✅ Verifique CORS no backend

### Erro 404 no frontend
1. ✅ Confirme se `vercel.json` existe
2. ✅ Verifique as rotas do React Router
3. ✅ Teste localmente com `npm run preview`

### Notificações não funcionam
1. ✅ Verifique se o Celery Worker está rodando
2. ✅ Confirme se o Redis está conectado
3. ✅ Verifique os logs do worker
4. ✅ Teste criar um prazo manualmente

## 🎉 Deploy Concluído!

### URLs Finais
- 🌐 **Frontend**: `https://seu-projeto.vercel.app`
- 🔧 **API**: `https://bacelar-api.onrender.com`
- 📚 **Documentação**: `https://bacelar-api.onrender.com/docs`

### Credenciais de Acesso
- **Email**: `admin@bacelar.com` (ou o que você configurou)
- **Senha**: A senha que você definiu na variável `SUPERUSER_PASSWORD`

### Próximos Passos
1. 🔒 Configure um domínio personalizado (opcional)
2. 📊 Configure monitoramento e alertas
3. 🔄 Configure backups automáticos
4. 👥 Adicione outros usuários ao sistema
5. 📱 Configure notificações push (Firebase)

---

**🎯 Parabéns! Sua aplicação está no ar e funcionando!** 🚀