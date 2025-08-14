#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import verify_password, get_password_hash
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_user_password():
    # Conectar ao banco PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        database="bacelar_db",
        user="bacelar_user",
        password="bacelar2025"
    )
    cursor = conn.cursor()
    
    # Buscar o usuário ana.test@bacelar.com
    cursor.execute("SELECT email, password_hash FROM users WHERE email = %s", ('ana.test@bacelar.com',))
    result = cursor.fetchone()
    
    if result:
        email, stored_hash = result
        print(f"Usuário encontrado: {email}")
        print(f"Hash armazenado: {stored_hash[:50]}...")
        
        # Testar verificação da senha
        test_password = "senha123"
        is_valid = verify_password(test_password, stored_hash)
        print(f"Senha '{test_password}' é válida: {is_valid}")
        
        # Gerar um novo hash para comparação
        new_hash = get_password_hash(test_password)
        print(f"Novo hash gerado: {new_hash[:50]}...")
        
        # Verificar se o novo hash funciona
        new_hash_valid = verify_password(test_password, new_hash)
        print(f"Novo hash é válido: {new_hash_valid}")
        
    else:
        print("Usuário ana.test@bacelar.com não encontrado")
    
    conn.close()

if __name__ == "__main__":
    check_user_password()