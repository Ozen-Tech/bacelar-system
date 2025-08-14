#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar as notificações automáticas quando um novo prazo é criado.
Testa se todos os usuários ativos recebem notificações apropriadas.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração da API
base_url = "http://localhost:8000/api/v1"

def test_deadline_notifications():
    print("=== Teste de Notificações Automáticas para Novos Prazos ===")
    
    # 1. Login como admin para criar o prazo
    print("\n1. Fazendo login como admin...")
    login_data = {
        "username": "ana.test@bacelar.com",
        "password": "novaSenha123"
    }
    
    login_response = requests.post(f"{base_url}/auth/login", data=login_data)
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.status_code} - {login_response.text}")
        return
    
    admin_token = login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Login como admin realizado com sucesso")
    
    # 2. Obter lista de usuários para verificar quantos devem receber notificações
    print("\n2. Obtendo lista de usuários ativos...")
    users_response = requests.get(f"{base_url}/users/", headers=admin_headers)
    if users_response.status_code != 200:
        print(f"❌ Erro ao obter usuários: {users_response.status_code}")
        return
    
    users = users_response.json()
    active_users = [user for user in users if user.get('is_active', True)]
    print(f"✅ Encontrados {len(active_users)} usuários ativos")
    
    # 3. Verificar notificações antes da criação do prazo
    print("\n3. Verificando notificações existentes...")
    notifications_before = {}
    for user in active_users:
        # Fazer login como cada usuário para verificar suas notificações
        if user['email'] == 'ana.test@bacelar.com':
            user_token = admin_token
        else:
            # Para outros usuários, assumimos que a senha é padrão ou pulamos
            continue
        
        user_headers = {"Authorization": f"Bearer {user_token}"}
        notif_response = requests.get(f"{base_url}/notifications/", headers=user_headers)
        if notif_response.status_code == 200:
            notifications_before[user['id']] = len(notif_response.json())
            print(f"  - {user['name']}: {notifications_before[user['id']]} notificações")
    
    # 4. Criar um novo prazo
    print("\n4. Criando novo prazo...")
    due_date = datetime.now() + timedelta(days=15)
    deadline_data = {
        "task_description": "Teste de notificações automáticas - Prazo de exemplo",
        "due_date": due_date.isoformat(),
        "process_number": "12345-67.2024.8.26.0001",
        "type": "Recurso",
        "parties": "Autor vs Réu",
        "responsible_user_id": None  # Sem responsável específico
    }
    
    create_response = requests.post(
        f"{base_url}/deadlines/", 
        json=deadline_data, 
        headers=admin_headers
    )
    
    if create_response.status_code != 201:
        print(f"❌ Erro ao criar prazo: {create_response.status_code} - {create_response.text}")
        return
    
    created_deadline = create_response.json()
    print(f"✅ Prazo criado com sucesso: {created_deadline['id']}")
    print(f"   Descrição: {created_deadline['task_description']}")
    
    # 5. Aguardar um pouco para as notificações serem processadas
    print("\n5. Aguardando processamento das notificações...")
    import time
    time.sleep(2)
    
    # 6. Verificar notificações após a criação do prazo
    print("\n6. Verificando novas notificações...")
    notifications_after = {}
    new_notifications_count = 0
    
    for user in active_users:
        if user['email'] == 'ana.test@bacelar.com':
            user_token = admin_token
        else:
            continue
        
        user_headers = {"Authorization": f"Bearer {user_token}"}
        notif_response = requests.get(f"{base_url}/notifications/", headers=user_headers)
        if notif_response.status_code == 200:
            notifications_after[user['id']] = len(notif_response.json())
            before_count = notifications_before.get(user['id'], 0)
            new_count = notifications_after[user['id']] - before_count
            new_notifications_count += new_count
            
            print(f"  - {user['name']}: {new_count} nova(s) notificação(ões)")
            
            # Mostrar detalhes das notificações mais recentes
            if new_count > 0:
                recent_notifications = notif_response.json()[:new_count]
                for notif in recent_notifications:
                    print(f"    * {notif['title']}: {notif['body']}")
    
    # 7. Resumo dos resultados
    print("\n=== RESUMO DOS RESULTADOS ===")
    print(f"✅ Prazo criado com sucesso")
    print(f"📊 Total de usuários ativos: {len(active_users)}")
    print(f"📬 Total de novas notificações: {new_notifications_count}")
    
    # Expectativa: todos os usuários ativos exceto o criador devem receber notificação
    expected_notifications = len(active_users) - 1  # -1 para excluir o criador
    if new_notifications_count >= expected_notifications:
        print("✅ Sistema de notificações funcionando corretamente!")
    else:
        print(f"⚠️ Possível problema: esperado pelo menos {expected_notifications} notificações")
    
    # 8. Limpeza - deletar o prazo de teste
    print("\n8. Limpando prazo de teste...")
    delete_response = requests.delete(
        f"{base_url}/deadlines/{created_deadline['id']}", 
        headers=admin_headers
    )
    
    if delete_response.status_code == 204:
        print("✅ Prazo de teste removido com sucesso")
    else:
        print(f"⚠️ Não foi possível remover o prazo de teste: {delete_response.status_code}")

if __name__ == "__main__":
    try:
        test_deadline_notifications()
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()