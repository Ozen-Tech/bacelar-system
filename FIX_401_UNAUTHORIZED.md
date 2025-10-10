# 🔐 Solução: Erro 401 Unauthorized

## 🔍 **O Problema**

Você está recebendo este erro:
```
POST https://bacelar-api.onrender.com/api/v1/deadlines/ 401 (Unauthorized)
```

**O que significa:** O token de autenticação (JWT) está **expirado**, **inválido** ou **não está sendo enviado**.

---

## ✅ **Soluções (Do Mais Simples ao Mais Complexo)**

### **Solução 1: Fazer Logout e Login Novamente** ⭐ (RECOMENDADO)

Esta é a solução mais simples e resolve 90% dos casos.

**No Frontend:**
1. Clique no botão de "Sair" ou "Logout"
2. Faça login novamente
3. Tente criar o prazo novamente

**Por que funciona:**
- Gera um novo token JWT válido
- Remove tokens expirados do localStorage
- Reautentica o usuário

---

### **Solução 2: Limpar Cache e Storage do Navegador**

**Passo a passo:**
1. Abra o DevTools (F12)
2. Vá na aba **Application** (Chrome) ou **Storage** (Firefox)
3. No menu lateral esquerdo:
   - Clique em **Local Storage**
   - Selecione seu domínio
   - Delete a chave que contém o token (geralmente `token`, `auth`, `user`, etc.)
4. Recarregue a página (Ctrl+Shift+R)
5. Faça login novamente

---

### **Solução 3: Aumentar Tempo de Expiração do Token**

Se o problema acontece com frequência, você pode aumentar o tempo de expiração.

**No Backend (app/core/config.py):**

O token já está configurado para **7 dias**:
```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 dias
```

Se quiser aumentar para 30 dias:
```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 dias
```

**⚠️ IMPORTANTE:**
- Tokens com expiração longa são menos seguros
- Para produção, recomendamos no máximo 7-14 dias
- Implemente refresh token para melhor segurança

---

### **Solução 4: Implementar Auto-Refresh do Token**

Para melhor experiência do usuário, implemente refresh automático no frontend.

**No Frontend (React/TypeScript):**

```typescript
// utils/auth.ts
import { jwtDecode } from 'jwt-decode';

export const isTokenExpired = (token: string): boolean => {
  try {
    const decoded: any = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    
    // Verifica se o token expira em menos de 5 minutos
    return decoded.exp < currentTime + 300;
  } catch {
    return true;
  }
};

export const shouldRefreshToken = (token: string): boolean => {
  try {
    const decoded: any = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    
    // Refresh se faltar menos de 1 hora para expirar
    return decoded.exp < currentTime + 3600;
  } catch {
    return true;
  }
};
```

**Interceptor Axios:**
```typescript
// api/axiosInstance.ts
import axios from 'axios';
import { isTokenExpired } from './utils/auth';

const api = axios.create({
  baseURL: 'https://bacelar-api.onrender.com/api/v1'
});

// Interceptor de requisição
api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('token');
    
    if (token) {
      // Verifica se o token está expirado
      if (isTokenExpired(token)) {
        // Redireciona para login
        localStorage.removeItem('token');
        window.location.href = '/login';
        throw new Error('Token expirado');
      }
      
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor de resposta
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido ou expirado
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

### **Solução 5: Implementar Refresh Token** (Melhor Prática)

Para aplicações em produção, implemente sistema de refresh token.

**Backend: Criar endpoint de refresh**

```python
# app/api/endpoints/auth.py

@router.post("/refresh", response_model=Token)
def refresh_token(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Gera um novo access token para o usuário logado.
    """
    access_token = create_access_token(data={"sub": current_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
```

**Frontend: Usar refresh automático**

```typescript
const refreshToken = async () => {
  try {
    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${oldToken}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      return data.access_token;
    }
  } catch (error) {
    console.error('Erro ao renovar token:', error);
    // Redireciona para login
    window.location.href = '/login';
  }
};
```

---

## 🔍 **Diagnóstico: Verificar o Token**

Para identificar o problema exato, siga estes passos:

### **1. Verificar se o Token Existe**

**No Console do Navegador (F12):**
```javascript
console.log(localStorage.getItem('token'));
// Deve mostrar algo como: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

- ✅ Se aparecer um token: Token existe, mas pode estar expirado
- ❌ Se aparecer `null`: Token não existe, faça login

---

### **2. Verificar se o Token Está Expirado**

**Instale jwt-decode:**
```bash
npm install jwt-decode
```

**No Console do Navegador:**
```javascript
import { jwtDecode } from 'jwt-decode';

const token = localStorage.getItem('token');
if (token) {
  const decoded = jwtDecode(token);
  console.log('Token expira em:', new Date(decoded.exp * 1000));
  console.log('Hora atual:', new Date());
  console.log('Expirado?', decoded.exp < Date.now() / 1000);
}
```

---

### **3. Verificar Headers da Requisição**

**No DevTools (F12) → Network:**
1. Tente criar um prazo
2. Clique na requisição que deu 401
3. Vá na aba **Headers**
4. Procure por:
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
   ```

- ✅ Se o header existe: Token está sendo enviado, mas é inválido/expirado
- ❌ Se o header não existe: Token não está sendo enviado

---

## 🛠️ **Correções no Frontend**

### **Problema: Token não está sendo enviado**

**Verifique se você está usando o token corretamente:**

```typescript
// ❌ ERRADO - Sem token
fetch('https://bacelar-api.onrender.com/api/v1/deadlines/', {
  method: 'POST',
  body: JSON.stringify(data)
});

// ✅ CERTO - Com token
const token = localStorage.getItem('token');
fetch('https://bacelar-api.onrender.com/api/v1/deadlines/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
});
```

---

### **Problema: Token expirado constantemente**

**Adicione verificação antes de cada requisição:**

```typescript
// hooks/useAuth.ts
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { isTokenExpired } from '../utils/auth';

export const useAuth = () => {
  const navigate = useNavigate();
  
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      
      if (!token || isTokenExpired(token)) {
        localStorage.removeItem('token');
        navigate('/login');
      }
    };
    
    // Verifica a cada 1 minuto
    const interval = setInterval(checkAuth, 60000);
    checkAuth(); // Verifica imediatamente
    
    return () => clearInterval(interval);
  }, [navigate]);
};
```

---

## 📋 **Checklist de Verificação**

Frontend:
- [ ] Token está sendo armazenado no localStorage após login?
- [ ] Token está sendo incluído no header Authorization?
- [ ] Formato do header está correto: `Bearer <token>`?
- [ ] Token está sendo removido após logout?
- [ ] Há verificação de expiração do token?
- [ ] Usuário é redirecionado para login se token expirar?

Backend:
- [x] Endpoint de autenticação funciona
- [x] Token JWT está sendo gerado corretamente
- [x] Validação do token está implementada
- [x] Tempo de expiração está configurado (7 dias)

---

## 🚀 **Solução Rápida (Agora)**

**Execute estes comandos no console do navegador (F12):**

```javascript
// 1. Ver o token atual
console.log('Token:', localStorage.getItem('token'));

// 2. Limpar token
localStorage.removeItem('token');

// 3. Recarregar página
window.location.reload();

// 4. Fazer login novamente
```

Depois de fazer login, tente criar o prazo novamente.

---

## ⚠️ **Notas Importantes**

1. **Token não é salvo no banco:** JWT é stateless, não há como "invalidar" no servidor
2. **Tempo de expiração:** Atualmente configurado para 7 dias
3. **Segurança:** Nunca exponha o SECRET_KEY
4. **HTTPS:** Em produção, sempre use HTTPS para proteger o token

---

## 🔗 **Endpoints de Autenticação**

- **Login:** `POST /api/v1/auth/login`
- **Verificar usuário:** `GET /api/v1/users/me`
- **Criar prazo:** `POST /api/v1/deadlines/` ← **Requer autenticação**

---

## 💡 **Resumo**

**O erro 401 não é um bug do backend.** É um comportamento esperado quando:
- Token expirou
- Token é inválido
- Token não foi enviado

**Solução mais rápida:**
1. Fazer logout
2. Fazer login novamente
3. Tentar a operação novamente

Se o problema persistir mesmo após fazer login novamente, verifique se o token está sendo incluído nos headers das requisições.

---

**Status:** ✅ Backend funcionando corretamente  
**Causa:** Token JWT expirado ou não enviado  
**Solução:** Fazer login novamente
