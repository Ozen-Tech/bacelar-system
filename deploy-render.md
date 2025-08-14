# Deploy Manual no Render

## Pré-requisitos
1. Conta no [Render](https://render.com)
2. Repositório GitHub com o código do backend
3. Arquivo `render.yaml` já configurado

## Passos para Deploy

### 1. Criar Repositório GitHub
```bash
# No diretório do backend
cd /Users/ozen/bacelar-advocacia

# Inicializar git (se ainda não foi feito)
git init
git add .
git commit -m "Initial commit - Backend API"

# Adicionar repositório remoto (substitua pela sua URL)
git remote add origin https://github.com/SEU_USUARIO/bacelar-advocacia-backend.git
git branch -M main
git push -u origin main
```

### 2. Deploy no Render
1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em "New" → "Blueprint"
3. Conecte seu repositório GitHub
4. O Render detectará automaticamente o arquivo `render.yaml`
5. Configure as variáveis de ambiente:

```env
# Banco de dados (será criado automaticamente)
DATABASE_URL=postgresql://...

# Segurança
SECRET_KEY=sua-chave-secreta-super-forte-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Superusuário
SUPERUSER_EMAIL=admin@bacelar.com
SUPERUSER_PASSWORD=senha-super-segura

# Redis (será criado automaticamente)
CELERY_BROKER_URL=redis://...
CELERY_RESULT_BACKEND=redis://...

# Firebase (opcional)
FIREBASE_CREDENTIALS_PATH=/opt/render/project/src/firebase-credentials.json

# Frontend URL (após deploy do frontend)
FRONTEND_URL=https://seu-frontend.vercel.app
```

6. Clique em "Apply" para iniciar o deploy

### 3. Verificar Deploy
- PostgreSQL: Será criado automaticamente
- Redis: Será criado automaticamente  
- API Web Service: Rodará na porta 8000
- Celery Worker: Para tarefas em background
- Celery Beat: Para tarefas agendadas

### 4. URL da API
Após o deploy, sua API estará disponível em:
```
https://bacelar-api.onrender.com
```

## Comandos Úteis

### Verificar logs
```bash
# No Render Dashboard
# Vá para seu serviço → Logs
```

### Executar migrações manualmente
```bash
# No Render Shell (se necessário)
alembic upgrade head
```

### Criar superusuário
```bash
# Será criado automaticamente na inicialização
# Verifique os logs para confirmar
```

## Troubleshooting

### Erro de conexão com banco
- Verifique se a `DATABASE_URL` está correta
- Confirme se o PostgreSQL foi criado

### Erro de Redis
- Verifique se o Redis foi criado
- Confirme as URLs do Celery

### Erro de migrações
- Verifique os logs do deploy
- Execute `alembic upgrade head` manualmente

### Erro de CORS
- Configure a `FRONTEND_URL` corretamente
- Verifique as configurações de CORS no código

## Próximos Passos
1. ✅ Deploy do backend concluído
2. 🔄 Deploy do frontend na Vercel
3. 🔄 Configurar URL da API no frontend
4. 🔄 Testar integração completa