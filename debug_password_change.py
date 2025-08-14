#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import verify_password, get_password_hash
from app.services import user_service
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def debug_password_change():
    # Conectar ao banco PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        database="bacelar_db",
        user="bacelar_user",
        password="bacelar2025"
    )
    cursor = conn.cursor()
    
    # Buscar o usuário ana.test@bacelar.com
    cursor.execute("SELECT id, email, password_hash FROM users WHERE email = %s", ('ana.test@bacelar.com',))
    result = cursor.fetchone()
    
    if result:
        user_id, email, stored_hash = result
        print(f"Usuário encontrado: {email} (ID: {user_id})")
        print(f"Hash armazenado: {stored_hash[:50]}...")
        
        # Testar verificação da senha atual
        current_password = "senha123"
        print(f"\nTestando senha atual: '{current_password}'")
        is_current_valid = verify_password(current_password, stored_hash)
        print(f"Senha atual é válida: {is_current_valid}")
        
        # Simular o que acontece no endpoint
        print("\n=== Simulando endpoint change_password ===")
        
        # Criar um objeto mock do usuário
        class MockUser:
            def __init__(self, user_id, email, password_hash):
                self.id = user_id
                self.email = email
                self.password_hash = password_hash
        
        mock_user = MockUser(user_id, email, stored_hash)
        
        # Testar a função change_password diretamente
        print(f"Testando verify_password('{current_password}', '{stored_hash[:30]}...')")
        direct_verify = verify_password(current_password, mock_user.password_hash)
        print(f"Resultado da verificação direta: {direct_verify}")
        
        # Testar com diferentes variações da senha
        test_passwords = ["senha123", "Senha123", "SENHA123", "senha123 ", " senha123"]
        print("\n=== Testando variações da senha ===")
        for test_pwd in test_passwords:
            result = verify_password(test_pwd, stored_hash)
            print(f"'{test_pwd}' -> {result}")
            
    else:
        print("Usuário ana.test@bacelar.com não encontrado")
    
    conn.close()

if __name__ == "__main__":
    debug_password_change()