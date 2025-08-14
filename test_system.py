#!/usr/bin/env python3
import requests
import json
import os

# Configurações
BASE_URL = "http://localhost:8000/api/v1"
USER_EMAIL = "admin@teste.com"
USER_PASSWORD = "senha123"
EXCEL_FILE = "planilha_teste.xlsx"

def test_login():
    """Testa o login do usuário"""
    print("🔐 Testando login...")
    
    login_data = {
        "username": USER_EMAIL,
        "password": USER_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login realizado com sucesso!")
            print(f"   Token: {token_data.get('access_token', 'N/A')[:50]}...")
            return token_data.get('access_token')
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def test_excel_import(token):
    """Testa a importação de Excel"""
    print("\n📊 Testando importação de Excel...")
    
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Arquivo {EXCEL_FILE} não encontrado")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        with open(EXCEL_FILE, 'rb') as f:
            files = {'file': (EXCEL_FILE, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            response = requests.post(
                f"{BASE_URL}/excel/import-excel",
                files=files,
                headers=headers
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Importação realizada com sucesso!")
            print(f"   Prazos criados: {result.get('created_count', 0)}")
            print(f"   Erros: {len(result.get('errors', []))}")
            if result.get('errors'):
                for error in result.get('errors', [])[:3]:  # Mostra apenas os 3 primeiros erros
                    print(f"   - {error}")
            return True
        else:
            print(f"❌ Erro na importação: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def test_deadlines_list(token):
    """Testa a listagem de prazos"""
    print("\n📋 Testando listagem de prazos...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/deadlines/",
            headers=headers
        )
        
        if response.status_code == 200:
            deadlines = response.json()
            print(f"✅ Listagem realizada com sucesso!")
            print(f"   Total de prazos: {len(deadlines)}")
            if deadlines:
                print(f"   Primeiro prazo: {deadlines[0].get('title', 'N/A')}")
            return True
        else:
            print(f"❌ Erro na listagem: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na listagem: {e}")
        return False

def main():
    print("🚀 Iniciando testes do sistema...\n")
    
    # Teste 1: Login
    token = test_login()
    if not token:
        print("\n❌ Não foi possível continuar sem o token de acesso")
        return
    
    # Teste 2: Listagem de prazos (antes da importação)
    test_deadlines_list(token)
    
    # Teste 3: Importação Excel
    excel_success = test_excel_import(token)
    
    # Teste 4: Listagem de prazos (após a importação)
    if excel_success:
        test_deadlines_list(token)
    
    print("\n🎉 Testes concluídos!")

if __name__ == "__main__":
    main()