# app/main.py
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, users, deadlines, dashboard, notifications, excel_import
from app.core.config import settings

app = FastAPI(
    title="API Bacelar Advocacia",
    version="1.0.0",
    description="Sistema de Gestão de Prazos Jurídicos com IA"
)

# CONFIGURAÇÃO DE CORS PARA RAILWAY + VERCEL
# ============================================

# Lista de origens permitidas
origins = [
    # Origem de desenvolvimento
    "http://localhost:5173",
    # Origem de produção (Vercel)
    "https://bacelar-advocacia-frontend.vercel.app",
]

# Se a URL da Vercel for fornecida, também aceita subdomínios
# Isso permite que os preview deployments funcionem
if "vercel.app" in settings.FRONTEND_URL:
    # Extrai o domínio base e aceita qualquer subdomínio
    # Ex: https://meu-app.vercel.app -> aceita https://*.vercel.app
    base_domain = settings.FRONTEND_URL.split("//")[1].split(".")[0]
    origins.append(f"https://{base_domain}-*.vercel.app")

# Configuração do middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista de origens permitidas
    allow_credentials=True,  # Permite envio de cookies/credenciais
    allow_methods=["*"],     # Permite todos os métodos HTTP (GET, POST, PUT, DELETE, etc)
    allow_headers=["*"],     # Permite todos os headers
    expose_headers=["*"],    # Expõe todos os headers nas respostas
)

# ============================================
# CONFIGURAÇÃO DE ROTAS
# ============================================

api_router = APIRouter(prefix="/api/v1")

# Registra todos os routers
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(users.router, prefix="/users", tags=["Usuários"])
api_router.include_router(deadlines.router, prefix="/deadlines", tags=["Prazos"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notificações"])
api_router.include_router(excel_import.router, prefix="/excel", tags=["Importação Excel"])

# Inclui o router principal na aplicação
app.include_router(api_router)

# ============================================
# ENDPOINTS DE SAÚDE E INFORMAÇÃO
# ============================================

@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raiz - verifica se a API está online"""
    return {
        "status": "ok",
        "message": "API Bacelar Advocacia está online!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint de health check para monitoramento"""
    return {
        "status": "healthy",
        "service": "bacelar-api"
    }

# ============================================
# STARTUP EVENT (Opcional)
# ============================================

@app.on_event("startup")
async def startup_event():
    """Executado quando a aplicação inicia"""
    print("🚀 API Bacelar Advocacia iniciada com sucesso!")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 Frontend URL: {settings.FRONTEND_URL}")
    print(f"🌐 CORS configurado para: {origins}")

@app.on_event("shutdown")
async def shutdown_event():
    """Executado quando a aplicação é encerrada"""
    print("👋 API Bacelar Advocacia encerrada")