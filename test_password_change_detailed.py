#!/usr/bin/env python3
import requests
import json

def test_password_change_detailed():
    base_url = "http://localhost:8000"
    
    # Dados de login
    login_data = {
        "username": "ana.test@bacelar.com",
        "password": "novaSenha123"
    }
    
    print("=== ETAPA 1: LOGIN ===")
    print(f"Enviando dados de login: {login_data}")
    
    # Fazer login
    login_response = requests.post(
        f"{base_url}/api/v1/auth/login",
        data=login_data
    )
    
    print(f"Status do login: {login_response.status_code}")
    print(f"Resposta do login: {login_response.text}")
    
    if login_response.status_code != 200:
        print("Falha no login. Parando teste.")
        return
    
    # Extrair token
    token_data = login_response.json()
    token = token_data["access_token"]
    print(f"Token obtido: {token[:50]}...")
    
    # Headers para requisições autenticadas
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n=== ETAPA 2: VERIFICAR DADOS DO USUÁRIO ===")
    me_response = requests.get(f"{base_url}/api/v1/users/me", headers=headers)
    print(f"Status /users/me: {me_response.status_code}")
    if me_response.status_code == 200:
        user_data = me_response.json()
        print(f"Dados do usuário: {json.dumps(user_data, indent=2)}")
    
    print("\n=== ETAPA 3: TENTAR TROCAR SENHA ===")
    
    # Dados para troca de senha
    password_change_data = {
        "current_password": "novaSenha123",
        "new_password": "senha123"
    }
    
    print(f"Enviando dados de troca de senha: {password_change_data}")
    print(f"Headers: {headers}")
    
    # Tentar trocar senha
    change_response = requests.post(
        f"{base_url}/api/v1/users/me/change-password",
        headers=headers,
        json=password_change_data
    )
    
    print(f"Status da troca de senha: {change_response.status_code}")
    print(f"Resposta da troca de senha: {change_response.text}")
    
    if change_response.status_code == 204:
        print("\n✅ SUCESSO! Senha alterada com sucesso.")
        
        print("\n=== ETAPA 4: TESTAR LOGIN COM NOVA SENHA ===")
        new_login_data = {
            "username": "ana.test@bacelar.com",
            "password": "senha123"
        }
        
        new_login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            data=new_login_data
        )
        
        print(f"Status do novo login: {new_login_response.status_code}")
        print(f"Resposta do novo login: {new_login_response.text}")
        
        if new_login_response.status_code == 200:
            print("✅ Login com nova senha funcionou!")
            
            # Reverter senha para o valor original
            print("\n=== ETAPA 5: REVERTER SENHA ===")
            new_token = new_login_response.json()["access_token"]
            new_headers = {
                "Authorization": f"Bearer {new_token}",
                "Content-Type": "application/json"
            }
            
            revert_data = {
                "current_password": "senha123",
                "new_password": "novaSenha123"
            }
            
            revert_response = requests.post(
                f"{base_url}/api/v1/users/me/change-password",
                headers=new_headers,
                json=revert_data
            )
            
            print(f"Status da reversão: {revert_response.status_code}")
            if revert_response.status_code == 204:
                print("✅ Senha revertida com sucesso!")
            else:
                print(f"❌ Falha na reversão: {revert_response.text}")
        else:
            print("❌ Login com nova senha falhou!")
    else:
        print(f"❌ FALHA na troca de senha: {change_response.text}")
        
        # Debug adicional - vamos ver se há algum problema com encoding
        print("\n=== DEBUG ADICIONAL ===")
        print(f"Dados enviados (raw): {json.dumps(password_change_data)}")
        print(f"Dados enviados (bytes): {json.dumps(password_change_data).encode('utf-8')}")

if __name__ == "__main__":
    test_password_change_detailed()