#!/usr/bin/env python3
"""
Script para resetar senha de um usuário.
Útil quando o usuário esqueceu a senha ou há problema com o hash.
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user.model import User


def reset_password(email: str, new_password: str, confirm: bool = False):
    """
    Reseta a senha de um usuário.
    
    Args:
        email: Email do usuário
        new_password: Nova senha
        confirm: Se True, não pede confirmação
    """
    db = SessionLocal()
    
    try:
        # Buscar usuário
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ Usuário não encontrado: {email}")
            return False
        
        print(f"👤 Usuário encontrado:")
        print(f"   - ID: {user.id}")
        print(f"   - Nome: {user.name}")
        print(f"   - Email: {user.email}")
        print(f"   - Profile: {user.profile}")
        
        # Confirmar ação
        if not confirm:
            print(f"\n⚠️  ATENÇÃO: Você está prestes a resetar a senha deste usuário!")
            response = input(f"   Digite 'CONFIRMAR' para continuar: ")
            if response != "CONFIRMAR":
                print("❌ Operação cancelada.")
                return False
        
        # Resetar senha
        print(f"\n🔄 Resetando senha...")
        user.password_hash = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Senha resetada com sucesso!")
        print(f"\n📋 Novas credenciais:")
        print(f"   Email: {user.email}")
        print(f"   Senha: {new_password}")
        print(f"\n⚠️  Informe ao usuário para trocar a senha após o primeiro login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao resetar senha: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def list_users():
    """Lista todos os usuários do sistema."""
    db = SessionLocal()
    
    try:
        users = db.query(User).order_by(User.name).all()
        
        print("\n" + "=" * 80)
        print("👥 USUÁRIOS NO SISTEMA")
        print("=" * 80)
        
        if not users:
            print("Nenhum usuário encontrado.")
            return
        
        print(f"\n{'Nome':<30} {'Email':<35} {'Perfil':<15}")
        print("-" * 80)
        
        for user in users:
            print(f"{user.name:<30} {user.email:<35} {user.profile.value:<15}")
        
        print(f"\nTotal: {len(users)} usuário(s)")
        
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")
    finally:
        db.close()


def main():
    """Função principal."""
    print("\n" + "=" * 80)
    print("🔐 RESETAR SENHA DE USUÁRIO - Bacelar Legal Intelligence")
    print("=" * 80)
    
    # Menu de opções
    print("\nOpções:")
    print("1. Resetar senha de um usuário")
    print("2. Listar todos os usuários")
    print("0. Sair")
    
    choice = input("\nEscolha uma opção: ").strip()
    
    if choice == "1":
        # Resetar senha
        email = input("\n📧 Email do usuário: ").strip()
        
        if not email:
            print("❌ Email é obrigatório!")
            return
        
        # Sugerir senha padrão
        print("\n💡 Sugestões de senha:")
        print("   - senha123 (temporária)")
        print("   - novaSenha123 (temporária)")
        print("   - Senha personalizada")
        
        new_password = input("\n🔑 Nova senha: ").strip()
        
        if not new_password:
            print("❌ Senha é obrigatória!")
            return
        
        if len(new_password) < 6:
            print("❌ Senha deve ter pelo menos 6 caracteres!")
            return
        
        # Confirmar senha
        confirm_password = input("🔑 Confirme a nova senha: ").strip()
        
        if new_password != confirm_password:
            print("❌ As senhas não coincidem!")
            return
        
        # Executar reset
        reset_password(email, new_password)
        
    elif choice == "2":
        # Listar usuários
        list_users()
        
    elif choice == "0":
        print("👋 Até logo!")
        return
    else:
        print("❌ Opção inválida!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
