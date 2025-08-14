#!/bin/bash

# Script para inicializar 

echo "🚀 Inicializando repositório Git para o backend..."

# Verificar se já existe um repositório Git
if [ -d ".git" ]; then
    echo "⚠️  Repositório Git já existe!"
    echo "Para reinicializar, execute: rm -rf .git && ./init-git.sh"
    exit 1
fi

# Inicializar Git
git init
echo "✅ Git inicializado"

# Criar .gitignore se não existir
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
PIPFILE.lock

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite3

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Firebase
firebase-credentials.json

# Alembic
# (keep alembic/ directory but ignore specific files if needed)

# Celery
celerybeat-schedule
celerybeat.pid

# Testing
.pytest_cache/
.coverage
htmlcov/

# Temporary files
*.tmp
*.temp
EOF
    echo "✅ .gitignore criado"
fi

# Adicionar todos os arquivos
git add .
echo "✅ Arquivos adicionados ao staging"

# Fazer primeiro commit
git commit -m "Initial commit - Bacelar Advocacia Backend API

- FastAPI backend with authentication
- PostgreSQL database with Alembic migrations
- Celery for background tasks
- Redis for caching and task queue
- Firebase integration for notifications
- Docker support with multi-stage build
- Render deployment configuration
- Comprehensive user and deadline management
- Automated notifications system"

echo "✅ Primeiro commit realizado"

echo ""
echo "🎉 Repositório Git inicializado com sucesso!"
echo ""
echo "Próximos passos:"
echo "1. Crie um repositório no GitHub"
echo "2. Execute os comandos:"
echo "   git remote add origin https://github.com/SEU_USUARIO/bacelar-advocacia-backend.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Depois faça o deploy no Render seguindo as instruções em deploy-render.md"
echo ""