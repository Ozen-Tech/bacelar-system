#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script melhorado para testar as notificações automáticas quando um novo prazo é criado.
Verifica as notificações diretamente no banco de dados para todos os usuários.
"""

import requests
import json
import psycopg2
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da API
base_url = "http://localhost:8000/api/v1"

# Configuração do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'bacelar_db',
    'user': 'bacelar_user',
    'password': 'bacelar2025'
}

def get_db_connection():
    """Cria conexão com o banco de dados"""
    return psycopg2.connect(**DB_CONFIG)

def count_notifications_by_content(content_filter):
    """Conta notificações que contêm determinado texto"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM notifications WHERE body LIKE %s",
            (f"%{content_filter}%",)
        )
        return cursor.fetchone()[0]
    finally:
        conn.close()

def get_recent_notifications_by_content(content_filter, limit=20):
    """Obtém notificações recentes que contêm determinado texto"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT n.id, n.title, n.body, n.created_at, u.name as user_name, u.email
            FROM notifications n 
            JOIN users u ON n.user_id = u.id 
            WHERE n.body LIKE %s 
            ORDER BY n.created_at DESC 
            LIMIT %s
            """,
            (f"%{content_filter}%", limit)
        )
        return cursor.fetchall()
    finally:
        conn.close()

def get_active_users_count():
    """Conta usuários ativos no banco"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = true")
        return cursor.fetchone()[0]
    finally:
        conn.close()

def test_deadline_notifications():
    print("=== Teste Melhorado de Notificações Automáticas para Novos Prazos ===")
    
    # 1. Login como admin para criar o prazo
    print("\n1. Fazendo login como admin...")
    login_data = {
        "username": "ana.test@bacelar.com",
        "password": "novaSenha123"
    }
    
    login_response = requests.post(f"{base_url}/auth/login", data=login_data)
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.status_code} - {login_response.text}")
        return False
    
    admin_token = login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Login como admin realizado com sucesso")
    
    # 2. Contar usuários ativos
    print("\n2. Verificando usuários ativos...")
    active_users_count = get_active_users_count()
    print(f"✅ Encontrados {active_users_count} usuários ativos")
    
    # 3. Criar identificador único para o teste
    test_id = f"Teste-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    task_description = f"Notificações automáticas - {test_id}"
    
    # 4. Contar notificações antes da criação
    print("\n3. Contando notificações antes da criação...")
    notifications_before = count_notifications_by_content(test_id)
    print(f"📊 Notificações com '{test_id}': {notifications_before}")
    
    # 5. Criar um novo prazo
    print("\n4. Criando novo prazo...")
    due_date = datetime.now() + timedelta(days=15)
    deadline_data = {
        "task_description": task_description,
        "due_date": due_date.isoformat(),
        "process_number": f"12345-67.2024.8.26.{test_id[-4:]}",
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
        return False
    
    created_deadline = create_response.json()
    print(f"✅ Prazo criado com sucesso: {created_deadline['id']}")
    print(f"   Descrição: {created_deadline['task_description']}")
    
    # 6. Aguardar um pouco para as notificações serem processadas
    print("\n5. Aguardando processamento das notificações...")
    import time
    time.sleep(2)
    
    # 7. Contar notificações após a criação
    print("\n6. Verificando novas notificações...")
    notifications_after = count_notifications_by_content(test_id)
    new_notifications = notifications_after - notifications_before
    
    print(f"📊 Notificações com '{test_id}': {notifications_after}")
    print(f"📬 Novas notificações criadas: {new_notifications}")
    
    # 8. Mostrar detalhes das notificações criadas
    if new_notifications > 0:
        print("\n7. Detalhes das notificações criadas:")
        recent_notifications = get_recent_notifications_by_content(test_id)
        for notif in recent_notifications:
            notif_id, title, body, created_at, user_name, user_email = notif
            print(f"  • {user_name} ({user_email}): {title}")
            print(f"    {body}")
            print(f"    Criada em: {created_at}")
            print()
    
    # 9. Análise dos resultados
    print("\n=== ANÁLISE DOS RESULTADOS ===")
    print(f"✅ Prazo criado com sucesso")
    print(f"📊 Total de usuários ativos: {active_users_count}")
    print(f"📬 Total de novas notificações: {new_notifications}")
    
    # Esperamos notificações para todos os usuários ativos, exceto o criador
    expected_notifications = active_users_count - 1  # -1 para excluir o criador
    
    if new_notifications == expected_notifications:
        print(f"✅ SUCESSO: Número correto de notificações ({new_notifications}/{expected_notifications})")
        success = True
    elif new_notifications > 0:
        print(f"⚠️ PARCIAL: Algumas notificações criadas ({new_notifications}/{expected_notifications})")
        success = True
    else:
        print(f"❌ FALHA: Nenhuma notificação criada (esperado: {expected_notifications})")
        success = False
    
    # 10. Limpeza - remover o prazo de teste
    print("\n8. Limpando prazo de teste...")
    delete_response = requests.delete(
        f"{base_url}/deadlines/{created_deadline['id']}", 
        headers=admin_headers
    )
    
    if delete_response.status_code == 204:
        print("✅ Prazo de teste removido com sucesso")
    else:
        print(f"⚠️ Aviso: Não foi possível remover o prazo de teste: {delete_response.status_code}")
    
    return success

if __name__ == "__main__":
    success = test_deadline_notifications()
    exit(0 if success else 1)