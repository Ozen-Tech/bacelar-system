#!/usr/bin/env python3
# Script para criar contas de usuário no sistema Bacelar Advocacia

import sys
import os
from getpass import getpass
from sqlalchemy.orm import Session

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import base
from app.services import user_service
from app.schemas.user import UserCreate, UserProfile
from app.db.connection import SessionLocal

def create_user_interactive():
    """Cria um usuário de forma interativa"""
    print("\n=== CRIAÇÃO DE USUÁRIO ===")
    
    # Coleta dados do usuário
    name = input("Nome completo: ").strip()
    if not name:
        print("❌ Nome é obrigatório!")
        return False
    
    email = input("Email: ").strip().lower()
    if not email:
        print("❌ Email é obrigatório!")
        return False
    
    # Seleciona o perfil
    print("\nPerfis disponíveis:")
    print("1. Admin (administrador)")
    print("2. Advogado")
    print("3. Estagiário")
    
    profile_choice = input("Escolha o perfil (1-3): ").strip()
    profile_map = {
        '1': UserProfile.ADMIN,
        '2': UserProfile.ADVOGADO,
        '3': UserProfile.ESTAGIARIO
    }
    
    if profile_choice not in profile_map:
        print("❌ Perfil inválido!")
        return False
    
    profile = profile_map[profile_choice]
    
    # Coleta telefone (opcional)
    phone = input("Telefone (opcional): ").strip() or None
    
    # Coleta senha
    password = getpass("Senha (mínimo 6 caracteres): ")
    if len(password) < 6:
        print("❌ Senha deve ter pelo menos 6 caracteres!")
        return False
    
    password_confirm = getpass("Confirme a senha: ")
    if password != password_confirm:
        print("❌ Senhas não coincidem!")
        return False
    
    # Cria o usuário
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
        print(f"\n✅ Usuário criado com sucesso!")
        print(f"   ID: {user.id}")
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

def create_user_batch(users_data):
    """Cria múltiplos usuários em lote"""
    print(f"\n=== CRIAÇÃO EM LOTE ({len(users_data)} usuários) ===")
    
    db = SessionLocal()
    created_count = 0
    
    try:
        for user_data in users_data:
            try:
                # Verifica se o email já existe
                existing_user = user_service.get_user_by_email(db, email=user_data['email'])
                if existing_user:
                    print(f"⚠️  Usuário {user_data['email']} já existe. Pulando...")
                    continue
                
                # Cria o usuário
                user_in = UserCreate(**user_data)
                user = user_service.create_user(db=db, user_in=user_in)
                print(f"✅ Criado: {user.name} ({user.email}) - {user.profile.value}")
                created_count += 1
                
            except Exception as e:
                print(f"❌ Erro ao criar {user_data.get('email', 'usuário')}: {e}")
        
        print(f"\n📊 Resumo: {created_count} usuários criados com sucesso.")
        
    finally:
        db.close()

def create_demo_users():
    """Cria usuários de demonstração"""
    demo_users = [
        {
            'name': 'João Silva',
            'email': 'joao.silva@bacelar.com',
            'password': 'senha123',
            'profile': UserProfile.ADVOGADO,
            'phone': '(11) 99999-1111'
        },
        {
            'name': 'Maria Santos',
            'email': 'maria.santos@bacelar.com',
            'password': 'senha123',
            'profile': UserProfile.ADVOGADO,
            'phone': '(11) 99999-2222'
        },
        {
            'name': 'Pedro Oliveira',
            'email': 'pedro.oliveira@bacelar.com',
            'password': 'senha123',
            'profile': UserProfile.ESTAGIARIO,
            'phone': '(11) 99999-3333'
        },
        {
            'name': 'Ana Costa',
            'email': 'ana.costa@bacelar.com',
            'password': 'senha123',
            'profile': UserProfile.ADMIN,
            'phone': '(11) 99999-4444'
        }
    ]
    
    create_user_batch(demo_users)

def list_users():
    """Lista todos os usuários do sistema"""
    print("\n=== USUÁRIOS CADASTRADOS ===")
    
    db = SessionLocal()
    try:
        users = db.query(user_service.User).all()
        
        if not users:
            print("Nenhum usuário encontrado.")
            return
        
        print(f"\nTotal: {len(users)} usuários\n")
        
        for user in users:
            status = "✅ Ativo" if user.is_active else "❌ Inativo"
            print(f"• {user.name}")
            print(f"  Email: {user.email}")
            print(f"  Perfil: {user.profile.value}")
            print(f"  Status: {status}")
            if user.phone:
                print(f"  Telefone: {user.phone}")
            print(f"  Criado em: {user.created_at.strftime('%d/%m/%Y %H:%M')}")
            print()
        
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")
    finally:
        db.close()

def main():
    """Função principal do script"""
    print("🏛️  BACELAR ADVOCACIA - GERENCIADOR DE USUÁRIOS")
    print("=" * 50)
    
    while True:
        print("\nOpções disponíveis:")
        print("1. Criar usuário (interativo)")
        print("2. Criar usuários de demonstração")
        print("3. Listar usuários")
        print("4. Sair")
        
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        if choice == '1':
            create_user_interactive()
        elif choice == '2':
            confirm = input("\nDeseja criar os usuários de demonstração? (s/N): ").strip().lower()
            if confirm in ['s', 'sim', 'y', 'yes']:
                create_demo_users()
        elif choice == '3':
            list_users()
        elif choice == '4':
            print("\n👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Script interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)