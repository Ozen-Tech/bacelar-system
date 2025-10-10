#!/usr/bin/env python3
"""
Script de teste simplificado para troca de senha.
Testa todo o fluxo de troca de senha passo a passo.
"""

import requests
import json
from typing import Optional


class PasswordChangeTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        
    def login(self, email: str, password: str) -> bool:
        """Faz login e armazena o token."""
        print(f"\n🔐 Fazendo login com {email}...")
        
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            data={
                "username": email,
                "password": password
            }
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            print(f"   ✅ Login bem-sucedido!")
            print(f"   Token: {self.token[:30]}...")
            return True
        else:
            print(f"   ❌ Falha no login!")
            print(f"   Resposta: {response.text}")
            return False
    
    def get_user_info(self) -> dict:
        """Busca informações do usuário logado."""
        print(f"\n👤 Buscando informações do usuário...")
        
        if not self.token:
            print(f"   ❌ Token não disponível. Faça login primeiro.")
            return {}
        
        response = requests.get(
            f"{self.base_url}/api/v1/users/me",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print(f"   ✅ Usuário encontrado:")
            print(f"      - Nome: {user.get('name')}")
            print(f"      - Email: {user.get('email')}")
            print(f"      - Perfil: {user.get('profile')}")
            return user
        else:
            print(f"   ❌ Erro ao buscar usuário")
            print(f"   Resposta: {response.text}")
            return {}
    
    def change_password(self, current_password: str, new_password: str) -> bool:
        """Tenta trocar a senha."""
        print(f"\n🔄 Tentando trocar senha...")
        print(f"   Senha atual: {current_password}")
        print(f"   Nova senha: {new_password}")
        
        if not self.token:
            print(f"   ❌ Token não disponível. Faça login primeiro.")
            return False
        
        payload = {
            "current_password": current_password,
            "new_password": new_password
        }
        
        print(f"\n   Payload enviado: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{self.base_url}/api/v1/users/me/change-password",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        print(f"\n   Status da resposta: {response.status_code}")
        print(f"   Headers da resposta: {dict(response.headers)}")
        
        if response.status_code == 204:
            print(f"   ✅ Senha alterada com sucesso!")
            return True
        elif response.status_code == 400:
            print(f"   ❌ Senha atual incorreta!")
            try:
                error = response.json()
                print(f"   Detalhe: {error.get('detail')}")
            except:
                print(f"   Resposta: {response.text}")
            return False
        else:
            print(f"   ❌ Erro inesperado!")
            print(f"   Resposta: {response.text}")
            return False
    
    def test_full_flow(self, email: str, old_password: str, new_password: str):
        """Testa o fluxo completo de troca de senha."""
        print("=" * 70)
        print("🧪 TESTE COMPLETO DE TROCA DE SENHA")
        print("=" * 70)
        
        # Passo 1: Login com senha antiga
        if not self.login(email, old_password):
            print("\n❌ TESTE FALHOU: Não foi possível fazer login")
            return False
        
        # Passo 2: Verificar informações do usuário
        user = self.get_user_info()
        if not user:
            print("\n❌ TESTE FALHOU: Não foi possível buscar dados do usuário")
            return False
        
        # Passo 3: Trocar senha
        if not self.change_password(old_password, new_password):
            print("\n❌ TESTE FALHOU: Não foi possível trocar a senha")
            print("\n💡 DICAS:")
            print("   1. Verifique se a senha atual está correta")
            print("   2. Use o script 'diagnose_password_issue.py' para diagnosticar")
            print("   3. Verifique os logs do backend para mais detalhes")
            return False
        
        # Passo 4: Tentar login com nova senha
        print(f"\n🔐 Testando login com a NOVA senha...")
        if not self.login(email, new_password):
            print("\n❌ TESTE FALHOU: Login com nova senha não funcionou!")
            print("   A senha foi alterada, mas algo deu errado.")
            return False
        
        # Passo 5: Reverter senha (opcional)
        print(f"\n🔄 Revertendo senha para o valor original...")
        if self.change_password(new_password, old_password):
            print(f"\n✅ Senha revertida com sucesso!")
        else:
            print(f"\n⚠️  Não foi possível reverter a senha")
            print(f"   A senha atual do usuário é: {new_password}")
        
        print("\n" + "=" * 70)
        print("✅ TESTE COMPLETO EXECUTADO COM SUCESSO!")
        print("=" * 70)
        return True


def main():
    """Função principal."""
    print("\n" + "=" * 70)
    print("🔐 TESTE DE TROCA DE SENHA - Bacelar Legal Intelligence")
    print("=" * 70)
    
    # Configurar URL da API
    api_url = input("\n🌐 URL da API (deixe em branco para http://localhost:8000): ").strip()
    if not api_url:
        api_url = "http://localhost:8000"
    
    # Solicitar credenciais
    email = input("\n📧 Email do usuário: ").strip()
    old_password = input("🔑 Senha ATUAL: ").strip()
    new_password = input("🔑 Nova senha (para teste): ").strip()
    
    if not email or not old_password or not new_password:
        print("\n❌ Todos os campos são obrigatórios!")
        return
    
    # Executar teste
    tester = PasswordChangeTest(base_url=api_url)
    tester.test_full_flow(email, old_password, new_password)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
