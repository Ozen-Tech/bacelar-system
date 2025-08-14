import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import verify_password, get_password_hash

# Testar hash e verificação de senha
test_password = "senha123"
hashed = get_password_hash(test_password)
print(f"Senha original: {test_password}")
print(f"Hash gerado: {hashed}")
print(f"Verificação: {verify_password(test_password, hashed)}")

# Testar com diferentes senhas
test_passwords = ['senha123', 'admin123', 'password', '123456']
for pwd in test_passwords:
    test_hash = get_password_hash(pwd)
    result = verify_password(pwd, test_hash)
    print(f"Teste com '{pwd}': {result}")

# Testar hash específico que pode estar no banco
# Vamos simular um hash bcrypt típico
bcrypt_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # hash de 'secret'
print(f"\nTeste com hash bcrypt conhecido:")
print(f"Verificação 'secret': {verify_password('secret', bcrypt_hash)}")
print(f"Verificação 'senha123': {verify_password('senha123', bcrypt_hash)}")