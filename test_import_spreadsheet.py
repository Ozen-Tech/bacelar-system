#!/usr/bin/env python3
"""
Script de teste para o endpoint de importação de planilhas.

Uso:
    python test_import_spreadsheet.py
"""

import requests
import json
from pathlib import Path

# Configurações
API_URL = "http://localhost:8000"  # Altere para URL de produção se necessário
LOGIN_ENDPOINT = f"{API_URL}/api/v1/auth/login"
IMPORT_ENDPOINT = f"{API_URL}/api/v1/excel/import-spreadsheet"

# Credenciais de teste (usuário ADMIN)
TEST_ADMIN_EMAIL = "admin@bacelar.com"  # Ajuste conforme necessário
TEST_ADMIN_PASSWORD = "senha123"  # Ajuste conforme necessário

# Arquivo de teste
TEST_FILE = "planilha_exemplo_importacao.csv"


def login(email: str, password: str) -> str:
    """Faz login e retorna o token JWT."""
    print(f"🔐 Fazendo login com {email}...")
    
    response = requests.post(
        LOGIN_ENDPOINT,
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login realizado com sucesso!")
        return token
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(response.text)
        raise Exception("Falha no login")


def import_spreadsheet(token: str, file_path: str):
    """Importa planilha usando o endpoint."""
    print(f"\n📤 Importando planilha: {file_path}...")
    
    if not Path(file_path).exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": open(file_path, "rb")}
    
    response = requests.post(IMPORT_ENDPOINT, headers=headers, files=files)
    
    print(f"\n📊 Status da resposta: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ IMPORTAÇÃO CONCLUÍDA!")
        print(f"📈 Resultado: {result['message']}")
        print(f"✅ Prazos importados: {result['imported_count']}")
        print(f"❌ Erros: {result['error_count']}")
        
        if result['imported_deadlines']:
            print(f"\n📋 Primeiros prazos importados:")
            for deadline in result['imported_deadlines'][:3]:
                print(f"  - {deadline['task_description']}")
                print(f"    ID: {deadline['id']}")
                print(f"    Vencimento: {deadline['due_date']}")
                print(f"    Classificação: {deadline['classification']}")
                print()
        
        if result['errors']:
            print(f"\n⚠️  Erros encontrados:")
            for error in result['errors']:
                print(f"  - Linha {error['linha']}: {error['erro']}")
                print(f"    Descrição: {error['descricao']}")
                print()
        
        return result
    else:
        print(f"\n❌ ERRO NA IMPORTAÇÃO!")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None


def test_invalid_file(token: str):
    """Testa envio de arquivo inválido."""
    print("\n🧪 Testando envio de arquivo inválido...")
    
    # Cria um arquivo de texto temporário
    with open("arquivo_invalido.txt", "w") as f:
        f.write("Este não é um arquivo Excel/CSV válido")
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": open("arquivo_invalido.txt", "rb")}
    
    response = requests.post(IMPORT_ENDPOINT, headers=headers, files=files)
    
    if response.status_code == 400:
        print("✅ Validação de tipo de arquivo funcionou corretamente!")
        print(f"   Mensagem: {response.json()['detail']}")
    else:
        print(f"⚠️  Resposta inesperada: {response.status_code}")
    
    # Remove arquivo temporário
    Path("arquivo_invalido.txt").unlink()


def test_missing_columns(token: str):
    """Testa planilha com colunas faltando."""
    print("\n🧪 Testando planilha com colunas faltando...")
    
    # Cria CSV sem colunas obrigatórias
    with open("planilha_incompleta.csv", "w") as f:
        f.write("apenas_coluna,outra_coluna\n")
        f.write("valor1,valor2\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": open("planilha_incompleta.csv", "rb")}
    
    response = requests.post(IMPORT_ENDPOINT, headers=headers, files=files)
    
    if response.status_code == 400:
        print("✅ Validação de colunas obrigatórias funcionou!")
        print(f"   Mensagem: {response.json()['detail']}")
    else:
        print(f"⚠️  Resposta inesperada: {response.status_code}")
    
    # Remove arquivo temporário
    Path("planilha_incompleta.csv").unlink()


def main():
    """Função principal."""
    print("=" * 60)
    print("🧪 TESTE DO ENDPOINT DE IMPORTAÇÃO DE PLANILHAS")
    print("=" * 60)
    
    try:
        # 1. Fazer login
        token = login(TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD)
        
        # 2. Importar planilha válida
        result = import_spreadsheet(token, TEST_FILE)
        
        # 3. Testes de validação
        test_invalid_file(token)
        test_missing_columns(token)
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES CONCLUÍDOS!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
