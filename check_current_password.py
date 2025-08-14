#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import verify_password

# Hash atual do banco de dados
current_hash = "$2b$12$QvSKnJSTG.OnvumxNnko/eXt7vf6Lv3DmuAvS6OBSufxC7anA2Pc."

# Testar diferentes senhas
test_passwords = ['senha123', 'novaSenha123', 'admin123', 'password']

print("Testando senhas contra o hash atual do banco:")
print(f"Hash: {current_hash}")
print()

for password in test_passwords:
    is_valid = verify_password(password, current_hash)
    status = "✅ VÁLIDA" if is_valid else "❌ Inválida"
    print(f"Senha '{password}': {status}")

if __name__ == "__main__":
    pass