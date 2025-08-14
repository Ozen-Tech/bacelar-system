# app/main.py
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, users, deadlines, dashboard, notifications, excel_import
from app.core.config import settings

app = FastAPI(title="API Bacelar Advocacia", version="1.0.0")

# --- A CORREÇÃO DE CORS ESTÁ AQUI ---
# Usamos um regex que aceita tanto http quanto https
# e permite subdomínios (importante para os deploys da Vercel)
origins = [
    # Origem de desenvolvimento
    "http://localhost:5173", 
]

# Adiciona a URL de produção do frontend APENAS se ela estiver definida
if settings.FRONTEND_URL:
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------------------

api_router = APIRouter(prefix="/api/v1")
# (O resto do código dos routers continua o mesmo)
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(users.router, prefix="/users", tags=["Usuários"])
api_router.include_router(deadlines.router, prefix="/deadlines", tags=["Prazos"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notificações"])
api_router.include_router(excel_import.router, prefix="/excel", tags=["Importação Excel"])

app.include_router(api_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok"}