import requests
import json

# Fazer login
login_data = {
    "username": "ana.test@bacelar.com",
    "password": "senha123"
}

response = requests.post("http://localhost:8000/api/v1/auth/login", data=login_data)
print(f"Login status: {response.status_code}")
print(f"Login response: {response.text}")

if response.status_code == 200:
    token_data = response.json()
    token = token_data.get("access_token")
    print(f"Token: {token[:50]}...")
    
    # Testar troca de senha
    headers = {"Authorization": f"Bearer {token}"}
    password_change_data = {
        "current_password": "admin123",
        "new_password": "newpassword123"
    }
    
    change_response = requests.post(
        "http://localhost:8000/api/v1/users/me/change-password",
        json=password_change_data,
        headers=headers
    )
    
    print(f"Password change status: {change_response.status_code}")
    print(f"Password change response: {change_response.text}")
    
    # Tentar fazer login com a nova senha
    new_login_data = {
        "username": "ana.test@bacelar.com",
        "password": "newpassword123"
    }
    
    new_login_response = requests.post("http://localhost:8000/api/v1/auth/login", data=new_login_data)
    print(f"New login status: {new_login_response.status_code}")
    print(f"New login response: {new_login_response.text}")
    
    # Reverter a senha de volta
    if new_login_response.status_code == 200:
        new_token_data = new_login_response.json()
        new_token = new_token_data.get("access_token")
        
        revert_headers = {"Authorization": f"Bearer {new_token}"}
        revert_password_data = {
            "current_password": "newpassword123",
            "new_password": "admin123"
        }
        
        revert_response = requests.post(
            "http://localhost:8000/api/v1/users/me/change-password",
            json=revert_password_data,
            headers=revert_headers
        )
        
        print(f"Revert password status: {revert_response.status_code}")
        print(f"Revert password response: {revert_response.text}")
else:
    print("Login failed, cannot test password change")