#!/usr/bin/env python3
# Script rápido para criar usuário via linha de comando
# Uso: python quick_create_user.py "Nome" "email@exemplo.com" "senha" "perfil" ["telefone"]
# Perfis: admin, advogado, estagiario

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import base
from app.services import user_service
from app.schemas.user import UserCreate, UserProfile
from app.db.connection import SessionLocal

def create_user_quick(name, email, password, profile_str, phone=None):
    """Cria um usuário rapidamente"""
    
    # Mapeia string do perfil para enum
    profile_map = {
        'admin': UserProfile.ADMIN,
        'advogado': UserProfile.ADVOGADO,
        'estagiario': UserProfile.ESTAGIARIO
    }
    
    profile_str = profile_str.lower()
    if profile_str not in profile_map:
        print(f"❌ Perfil '{profile_str}' inválido. Use: admin, advogado ou estagiario")
        return False
    
    profile = profile_map[profile_str]
    
    db = SessionLocal()
    try:
        # Verifica se o email já existe
        existing_user = user_service.get_user_by_email(db, email=email)
        if existing_user:
            print(f"❌ Usuário com email {email} já existe!")
            return False
        
        # Cria o usuário
        user_in = UserCreate(
            email=email,
            password=password,
            name=name,
            profile=profile,
            phone=phone
        )
        
        user = user_service.create_user(db=db, user_in=user_in)
        print(f"✅ Usuário criado com sucesso!")
        print(f"   Nome: {user.name}")
        print(f"   Email: {user.email}")
        print(f"   Perfil: {user.profile.value}")
        if user.phone:
            print(f"   Telefone: {user.phone}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return False
    finally:
        db.close()

def show_usage():
    """Mostra como usar o script"""
    print("\n🏛️  BACELAR ADVOCACIA - CRIAÇÃO RÁPIDA DE USUÁRIO")
    print("=" * 55)
    print("\nUso:")
    print('  python quick_create_user.py "Nome" "email@exemplo.com" "senha" "perfil" ["telefone"]')
    print("\nPerfis disponíveis:")
    print("  • admin      - Administrador")
    print("  • advogado   - Advogado")
    print("  • estagiario - Estagiário")
    print("\nExemplos:")
    print('  python quick_create_user.py "João Silva" "joao@bacelar.com" "senha123" "advogado"')
    print('  python quick_create_user.py "Maria Admin" "maria@bacelar.com" "senha123" "admin" "(11) 99999-1111"')
    print()

def main():
    """Função principal"""
    if len(sys.argv) < 5:
        show_usage()
        print("❌ Argumentos insuficientes!")
        sys.exit(1)
    
    if len(sys.argv) > 6:
        show_usage()
        print("❌ Muitos argumentos!")
        sys.exit(1)
    
    name = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    profile = sys.argv[4]
    phone = sys.argv[5] if len(sys.argv) == 6 else None
    
    # Validações básicas
    if not name.strip():
        print("❌ Nome não pode estar vazio!")
        sys.exit(1)
    
    if not email.strip() or '@' not in email:
        print("❌ Email inválido!")
        sys.exit(1)
    
    if len(password) < 6:
        print("❌ Senha deve ter pelo menos 6 caracteres!")
        sys.exit(1)
    
    # Cria o usuário
    success = create_user_quick(name, email.lower(), password, profile, phone)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Script interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)