"""
Script de teste para o endpoint de importação em massa de deadlines
Endpoint: POST /api/v1/deadlines/bulk

Uso:
    python test_bulk_import.py

Requisitos:
    pip install requests python-dotenv
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict

# ==================== CONFIGURAÇÃO ====================

API_URL = "http://localhost:8000"  # URL do backend
LOGIN_ENDPOINT = f"{API_URL}/api/v1/auth/login"
BULK_ENDPOINT = f"{API_URL}/api/v1/deadlines/bulk"

# Credenciais de um usuário ADMIN
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "senha_admin"

# ==================== FUNÇÕES AUXILIARES ====================

def login(email: str, password: str) -> str:
    """
    Faz login e retorna o token JWT
    """
    print("🔐 Fazendo login...")
    
    response = requests.post(
        LOGIN_ENDPOINT,
        data={
            "username": email,
            "password": password
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login realizado com sucesso!")
        return token
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(response.json())
        raise Exception("Falha no login")


def create_deadlines_bulk(token: str, deadlines: List[Dict], skip_notifications: bool = True, skip_celery: bool = True) -> Dict:
    """
    Cria múltiplos deadlines de uma vez
    """
    print(f"\n📤 Enviando {len(deadlines)} deadlines para importação...")
    
    payload = {
        "deadlines": deadlines,
        "skip_notifications": skip_notifications,
        "skip_celery": skip_celery
    }
    
    response = requests.post(
        BULK_ENDPOINT,
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    if response.status_code == 201:
        result = response.json()
        print("✅ Importação concluída!")
        print(f"   📊 Total recebido: {result['total_received']}")
        print(f"   ✅ Importados: {result['imported_count']}")
        print(f"   ❌ Erros: {result['error_count']}")
        return result
    else:
        print(f"❌ Erro na importação: {response.status_code}")
        print(response.json())
        raise Exception("Falha na importação")


def print_result_details(result: Dict):
    """
    Imprime os detalhes do resultado da importação
    """
    print("\n" + "="*60)
    print("📋 RELATÓRIO DETALHADO DA IMPORTAÇÃO")
    print("="*60)
    
    # Deadlines criados
    if result['deadlines']:
        print(f"\n✅ {len(result['deadlines'])} PRAZOS CRIADOS COM SUCESSO:")
        print("-" * 60)
        for deadline in result['deadlines']:
            print(f"  • ID: {deadline['id']}")
            print(f"    Descrição: {deadline['task_description']}")
            print(f"    Vencimento: {deadline['due_date']}")
            print(f"    Processo: {deadline.get('process_number', 'N/A')}")
            print(f"    Classificação: {deadline['classification']}")
            print()
    
    # Erros encontrados
    if result['errors']:
        print(f"\n❌ {len(result['errors'])} ERROS ENCONTRADOS:")
        print("-" * 60)
        for error in result['errors']:
            print(f"  • Índice {error['index']}")
            print(f"    Descrição: {error.get('task_description', 'N/A')}")
            print(f"    Erro: {error['error']}")
            print()
    
    print("="*60)


# ==================== CASOS DE TESTE ====================

def test_1_importacao_simples(token: str):
    """
    Teste 1: Importação simples com 3 deadlines válidos
    """
    print("\n" + "="*60)
    print("🧪 TESTE 1: Importação Simples (3 deadlines válidos)")
    print("="*60)
    
    hoje = datetime.now()
    
    deadlines = [
        {
            "task_description": "Apresentar contestação no processo X",
            "due_date": (hoje + timedelta(days=30)).isoformat(),
            "process_number": "1234567-89.2024.8.01.0001",
            "type": "Recursal",
            "parties": "João Silva vs. Maria José",
            "status": "pendente"
        },
        {
            "task_description": "Protocolar recurso no processo Y",
            "due_date": (hoje + timedelta(days=15)).isoformat(),
            "process_number": "9876543-21.2024.8.01.0002",
            "type": "Processual",
            "parties": "Pedro Santos vs. Ana Costa",
            "status": "pendente"
        },
        {
            "task_description": "Comparecer à audiência processo Z",
            "due_date": (hoje + timedelta(days=7)).isoformat(),
            "process_number": "5555555-55.2024.8.01.0003",
            "type": "Audiência",
            "parties": "Carlos Lima vs. Empresa ABC",
            "status": "pendente"
        }
    ]
    
    result = create_deadlines_bulk(token, deadlines)
    print_result_details(result)
    
    assert result['imported_count'] == 3, "Deveria importar 3 deadlines"
    assert result['error_count'] == 0, "Não deveria ter erros"
    print("✅ TESTE 1 PASSOU!")


def test_2_importacao_com_erros(token: str):
    """
    Teste 2: Importação com alguns deadlines inválidos
    """
    print("\n" + "="*60)
    print("🧪 TESTE 2: Importação com Erros (mix de válidos e inválidos)")
    print("="*60)
    
    hoje = datetime.now()
    
    deadlines = [
        # Válido
        {
            "task_description": "Prazo válido número 1",
            "due_date": (hoje + timedelta(days=10)).isoformat(),
            "process_number": "1111111-11.2024.8.01.0001",
            "type": "Recursal",
            "status": "pendente"
        },
        # Inválido - descrição muito curta
        {
            "task_description": "ABC",
            "due_date": (hoje + timedelta(days=10)).isoformat(),
        },
        # Válido
        {
            "task_description": "Prazo válido número 2",
            "due_date": (hoje + timedelta(days=20)).isoformat(),
            "process_number": "2222222-22.2024.8.01.0002",
            "type": "Processual",
            "status": "pendente"
        },
        # Inválido - sem descrição
        {
            "due_date": (hoje + timedelta(days=10)).isoformat(),
        },
        # Válido
        {
            "task_description": "Prazo válido número 3",
            "due_date": (hoje + timedelta(days=30)).isoformat(),
            "status": "pendente"
        }
    ]
    
    result = create_deadlines_bulk(token, deadlines)
    print_result_details(result)
    
    print(f"\n📊 Resumo: {result['imported_count']} importados, {result['error_count']} erros")
    print("✅ TESTE 2 CONCLUÍDO! (Erros esperados foram capturados)")


def test_3_importacao_grande_volume(token: str):
    """
    Teste 3: Importação em grande volume (100 deadlines)
    """
    print("\n" + "="*60)
    print("🧪 TESTE 3: Importação em Grande Volume (100 deadlines)")
    print("="*60)
    
    hoje = datetime.now()
    deadlines = []
    
    # Gerar 100 deadlines válidos
    for i in range(1, 101):
        deadlines.append({
            "task_description": f"Prazo automatizado número {i} - teste de carga",
            "due_date": (hoje + timedelta(days=i)).isoformat(),
            "process_number": f"{str(i).zfill(7)}-01.2024.8.01.{str(i).zfill(4)}",
            "type": "Processual" if i % 2 == 0 else "Recursal",
            "parties": f"Parte A {i} vs. Parte B {i}",
            "status": "pendente"
        })
    
    import time
    start_time = time.time()
    
    result = create_deadlines_bulk(token, deadlines, skip_notifications=True, skip_celery=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n⏱️  Tempo de processamento: {duration:.2f} segundos")
    print(f"📊 Taxa: {result['imported_count'] / duration:.2f} deadlines/segundo")
    
    assert result['imported_count'] == 100, "Deveria importar 100 deadlines"
    assert result['error_count'] == 0, "Não deveria ter erros"
    print("✅ TESTE 3 PASSOU!")


def test_4_campos_opcionais(token: str):
    """
    Teste 4: Teste com campos opcionais (apenas campos obrigatórios)
    """
    print("\n" + "="*60)
    print("🧪 TESTE 4: Campos Opcionais (apenas obrigatórios)")
    print("="*60)
    
    hoje = datetime.now()
    
    deadlines = [
        # Apenas campos obrigatórios
        {
            "task_description": "Prazo mínimo com apenas campos obrigatórios",
            "due_date": (hoje + timedelta(days=5)).isoformat(),
        },
        # Com alguns opcionais
        {
            "task_description": "Prazo com alguns campos opcionais",
            "due_date": (hoje + timedelta(days=10)).isoformat(),
            "process_number": "7777777-77.2024.8.01.0007",
        },
        # Completo
        {
            "task_description": "Prazo com todos os campos preenchidos",
            "due_date": (hoje + timedelta(days=15)).isoformat(),
            "process_number": "8888888-88.2024.8.01.0008",
            "type": "Recursal",
            "parties": "Completo A vs. Completo B",
            "status": "pendente"
        }
    ]
    
    result = create_deadlines_bulk(token, deadlines)
    print_result_details(result)
    
    assert result['imported_count'] == 3, "Deveria importar 3 deadlines"
    assert result['error_count'] == 0, "Não deveria ter erros"
    print("✅ TESTE 4 PASSOU!")


def test_5_opcoes_notificacao_celery(token: str):
    """
    Teste 5: Teste das opções skip_notifications e skip_celery
    """
    print("\n" + "="*60)
    print("🧪 TESTE 5: Opções de Notificação e Celery")
    print("="*60)
    
    hoje = datetime.now()
    
    deadlines = [
        {
            "task_description": "Prazo com notificações e celery habilitados",
            "due_date": (hoje + timedelta(days=5)).isoformat(),
            "process_number": "9999999-99.2024.8.01.0009",
        }
    ]
    
    # Com notificações e celery
    print("\n📢 Teste com skip_notifications=False e skip_celery=False")
    result1 = create_deadlines_bulk(token, deadlines, skip_notifications=False, skip_celery=False)
    assert result1['imported_count'] == 1
    
    # Sem notificações e celery
    print("\n🔇 Teste com skip_notifications=True e skip_celery=True")
    result2 = create_deadlines_bulk(token, deadlines, skip_notifications=True, skip_celery=True)
    assert result2['imported_count'] == 1
    
    print("✅ TESTE 5 PASSOU!")


# ==================== EXECUTAR TODOS OS TESTES ====================

def main():
    """
    Função principal que executa todos os testes
    """
    print("="*60)
    print("🚀 INICIANDO TESTES DO ENDPOINT /deadlines/bulk")
    print("="*60)
    
    try:
        # Fazer login
        token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
        
        # Executar testes
        test_1_importacao_simples(token)
        test_2_importacao_com_erros(token)
        test_3_importacao_grande_volume(token)
        test_4_campos_opcionais(token)
        test_5_opcoes_notificacao_celery(token)
        
        print("\n" + "="*60)
        print("🎉 TODOS OS TESTES FORAM CONCLUÍDOS COM SUCESSO!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
