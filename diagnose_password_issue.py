#!/usr/bin/env python3
"""
Script de diagnóstico para problemas com troca de senha.
Verifica se a senha está sendo verificada corretamente.
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.security import verify_password, get_password_hash
from app.db.session import SessionLocal
from app.models.user.model import User


def diagnose_password_issue(email: str, test_password: str):
    """
    Diagnostica problemas com senha de um usuário específico.
    
    Args:
        email: Email do usuário
        test_password: Senha que você acha que está correta
    """
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("🔍 DIAGNÓSTICO DE PROBLEMA COM SENHA")
        print("=" * 60)
        
        # Buscar usuário
        print(f"\n1️⃣  Buscando usuário: {email}")
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ Usuário não encontrado: {email}")
            return
        
        print(f"✅ Usuário encontrado:")
        print(f"   - ID: {user.id}")
        print(f"   - Nome: {user.name}")
        print(f"   - Email: {user.email}")
        print(f"   - Profile: {user.profile}")
        print(f"   - Ativo: {user.is_active}")
        
        # Verificar hash da senha
        print(f"\n2️⃣  Verificando hash da senha no banco:")
        print(f"   - Hash armazenado: {user.password_hash[:50]}...")
        print(f"   - Tamanho do hash: {len(user.password_hash)} caracteres")
        
        # Testar senha fornecida
        print(f"\n3️⃣  Testando senha fornecida: '{test_password}'")
        is_valid = verify_password(test_password, user.password_hash)
        
        if is_valid:
            print(f"   ✅ A senha '{test_password}' está CORRETA!")
        else:
            print(f"   ❌ A senha '{test_password}' está INCORRETA!")
        
        # Testar algumas variações comuns
        print(f"\n4️⃣  Testando variações comuns da senha:")
        variations = [
            test_password,
            test_password.strip(),  # Remove espaços
            test_password.lower(),  # Minúsculas
            test_password.upper(),  # Maiúsculas
        ]
        
        for variation in variations:
            is_valid = verify_password(variation, user.password_hash)
            status = "✅" if is_valid else "❌"
            print(f"   {status} Senha: '{variation}'")
        
        # Gerar novo hash para comparação
        print(f"\n5️⃣  Gerando novo hash para a senha de teste:")
        new_hash = get_password_hash(test_password)
        print(f"   - Novo hash: {new_hash[:50]}...")
        print(f"   - Tamanho: {len(new_hash)} caracteres")
        
        # Verificar se o novo hash funciona
        print(f"\n6️⃣  Verificando se novo hash funciona:")
        is_valid_new = verify_password(test_password, new_hash)
        if is_valid_new:
            print(f"   ✅ Novo hash funciona corretamente")
        else:
            print(f"   ❌ PROBLEMA: Novo hash não funciona!")
        
        # Opção para resetar senha
        print(f"\n" + "=" * 60)
        print(f"💡 SUGESTÕES:")
        print("=" * 60)
        
        if not is_valid:
            print(f"❌ A senha atual no banco parece estar incorreta.")
            print(f"\n   Opções:")
            print(f"   1. Use o script 'reset_user_password.py' para resetar a senha")
            print(f"   2. Verifique se você está usando a senha correta")
            print(f"   3. Confira se há espaços extras na senha")
            
            response = input(f"\n❓ Deseja resetar a senha de '{email}' para '{test_password}'? (s/n): ")
            if response.lower() == 's':
                user.password_hash = get_password_hash(test_password)
                db.commit()
                print(f"✅ Senha resetada com sucesso!")
                
                # Verificar novamente
                is_valid_after = verify_password(test_password, user.password_hash)
                if is_valid_after:
                    print(f"✅ Verificação: A senha agora funciona!")
                else:
                    print(f"❌ ERRO: Ainda há problema com a senha!")
        else:
            print(f"✅ A senha está correta no banco de dados.")
            print(f"   Se você não consegue trocar a senha, o problema pode ser:")
            print(f"   - Erro no frontend (enviando senha incorreta)")
            print(f"   - Problema com encoding de caracteres")
            print(f"   - Cache do navegador")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔐 DIAGNÓSTICO DE SENHA - Bacelar Legal Intelligence")
    print("=" * 60)
    
    # Solicitar informações do usuário
    email = input("\n📧 Digite o email do usuário: ").strip()
    test_password = input("🔑 Digite a senha que você acha que está correta: ").strip()
    
    if not email or not test_password:
        print("\n❌ Email e senha são obrigatórios!")
        sys.exit(1)
    
    diagnose_password_issue(email, test_password)
