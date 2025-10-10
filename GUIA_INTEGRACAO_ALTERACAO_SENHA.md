# 🔐 Guia de Integração: Alteração de Senha no Frontend (React + Vite)

> Guia passo a passo para implementar a funcionalidade de alteração de senha consumindo o backend Bacelar Legal Intelligence

---

## 📋 Índice

1. [Informações do Backend](#informações-do-backend)
2. [Estrutura do Projeto Frontend](#estrutura-do-projeto-frontend)
3. [Passo 1: Configuração Inicial](#passo-1-configuração-inicial)
4. [Passo 2: Criar Serviço de API](#passo-2-criar-serviço-de-api)
5. [Passo 3: Criar Componente de Alteração de Senha](#passo-3-criar-componente-de-alteração-de-senha)
6. [Passo 4: Estilização](#passo-4-estilização)
7. [Passo 5: Integração com Roteamento](#passo-5-integração-com-roteamento)
8. [Passo 6: Testes](#passo-6-testes)
9. [Melhorias Opcionais](#melhorias-opcionais)

---

## 📌 Informações do Backend

### Endpoint
```
POST /api/v1/users/me/change-password
```

### Autenticação
- **Requerida**: Sim (Bearer Token JWT)
- **Header**: `Authorization: Bearer {seu_token_jwt}`

### Request Body
```json
{
  "current_password": "senha_atual",
  "new_password": "nova_senha_minimo_6_caracteres"
}
```

### Respostas

**✅ Sucesso (204 No Content)**
```
Status: 204
Body: (vazio)
```

**❌ Erro - Senha Incorreta (400 Bad Request)**
```json
{
  "detail": "Senha atual incorreta"
}
```

**❌ Erro - Token Inválido (401 Unauthorized)**
```json
{
  "detail": "Could not validate credentials"
}
```

**❌ Erro - Validação (422 Unprocessable Entity)**
```json
{
  "detail": [
    {
      "loc": ["body", "new_password"],
      "msg": "ensure this value has at least 6 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

## 🏗️ Estrutura do Projeto Frontend

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChangePassword/
│   │   │   ├── ChangePassword.tsx
│   │   │   └── ChangePassword.module.css
│   │   └── ...
│   ├── services/
│   │   ├── api.ts
│   │   └── authService.ts
│   ├── hooks/
│   │   └── useAuth.ts
│   ├── types/
│   │   └── api.types.ts
│   └── App.tsx
└── package.json
```

---

## 🚀 Passo 1: Configuração Inicial

### 1.1. Criar o Projeto Vite (se ainda não existe)

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

### 1.2. Instalar Dependências

```bash
# Biblioteca HTTP
npm install axios

# Para gerenciamento de formulários (opcional, mas recomendado)
npm install react-hook-form

# Para validação de formulários
npm install zod @hookform/resolvers

# Para notificações (opcional)
npm install react-toastify

# Para ícones
npm install react-icons
```

### 1.3. Configurar Variáveis de Ambiente

Crie o arquivo `.env` na raiz do projeto:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🔧 Passo 2: Criar Serviço de API

### 2.1. Criar Tipos TypeScript

Crie o arquivo `src/types/api.types.ts`:

```typescript
// src/types/api.types.ts

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export interface ApiError {
  detail: string | Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}

export interface User {
  id: string;
  email: string;
  name: string;
  profile: 'admin' | 'advogado' | 'estagiario';
}
```

### 2.2. Configurar Cliente Axios

Crie o arquivo `src/services/api.ts`:

```typescript
// src/services/api.ts

import axios, { AxiosError, AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Criar instância do axios
export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token em todas as requisições
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratar erros globalmente
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 2.3. Criar Serviço de Autenticação

Crie o arquivo `src/services/authService.ts`:

```typescript
// src/services/authService.ts

import api from './api';
import { PasswordChangeRequest, ApiError } from '../types/api.types';

export const authService = {
  /**
   * Altera a senha do usuário logado
   */
  changePassword: async (data: PasswordChangeRequest): Promise<void> => {
    try {
      await api.post('/users/me/change-password', data);
    } catch (error: any) {
      // Repassar o erro para ser tratado no componente
      throw error;
    }
  },

  /**
   * Login do usuário
   */
  login: async (username: string, password: string): Promise<string> => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const token = response.data.access_token;
    localStorage.setItem('access_token', token);
    return token;
  },

  /**
   * Logout do usuário
   */
  logout: () => {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  },

  /**
   * Verifica se o usuário está autenticado
   */
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Obtém o token atual
   */
  getToken: (): string | null => {
    return localStorage.getItem('access_token');
  },
};

export default authService;
```

---

## 🎨 Passo 3: Criar Componente de Alteração de Senha

### 3.1. Componente com React Hook Form (Recomendado)

Crie o arquivo `src/components/ChangePassword/ChangePassword.tsx`:

```typescript
// src/components/ChangePassword/ChangePassword.tsx

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { authService } from '../../services/authService';
import { FiEye, FiEyeOff, FiLock, FiCheck, FiX } from 'react-icons/fi';
import styles from './ChangePassword.module.css';

// Schema de validação com Zod
const passwordChangeSchema = z.object({
  current_password: z.string().min(1, 'Senha atual é obrigatória'),
  new_password: z.string()
    .min(6, 'Nova senha deve ter no mínimo 6 caracteres')
    .regex(/[A-Z]/, 'Senha deve conter pelo menos uma letra maiúscula')
    .regex(/[a-z]/, 'Senha deve conter pelo menos uma letra minúscula')
    .regex(/[0-9]/, 'Senha deve conter pelo menos um número'),
  confirm_password: z.string().min(1, 'Confirmação de senha é obrigatória'),
}).refine((data) => data.new_password === data.confirm_password, {
  message: 'As senhas não coincidem',
  path: ['confirm_password'],
});

type PasswordChangeFormData = z.infer<typeof passwordChangeSchema>;

export default function ChangePassword() {
  const [isLoading, setIsLoading] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch
  } = useForm<PasswordChangeFormData>({
    resolver: zodResolver(passwordChangeSchema),
  });

  const newPassword = watch('new_password');

  const onSubmit = async (data: PasswordChangeFormData) => {
    setIsLoading(true);
    setSuccessMessage('');
    setErrorMessage('');

    try {
      await authService.changePassword({
        current_password: data.current_password,
        new_password: data.new_password,
      });

      setSuccessMessage('Senha alterada com sucesso!');
      reset(); // Limpa o formulário
      
      // Opcional: Fazer logout automático após trocar senha
      setTimeout(() => {
        authService.logout();
      }, 2000);

    } catch (error: any) {
      console.error('Erro ao alterar senha:', error);

      if (error.response?.status === 400) {
        setErrorMessage('Senha atual incorreta. Tente novamente.');
      } else if (error.response?.status === 401) {
        setErrorMessage('Sessão expirada. Faça login novamente.');
      } else if (error.response?.status === 422) {
        setErrorMessage('Dados inválidos. Verifique os campos e tente novamente.');
      } else {
        setErrorMessage('Erro ao alterar senha. Tente novamente mais tarde.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Verificações de força da senha
  const passwordStrength = {
    hasMinLength: newPassword?.length >= 6,
    hasUpperCase: /[A-Z]/.test(newPassword || ''),
    hasLowerCase: /[a-z]/.test(newPassword || ''),
    hasNumber: /[0-9]/.test(newPassword || ''),
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <FiLock className={styles.icon} />
          <h2>Alterar Senha</h2>
        </div>

        {successMessage && (
          <div className={styles.successAlert}>
            <FiCheck /> {successMessage}
          </div>
        )}

        {errorMessage && (
          <div className={styles.errorAlert}>
            <FiX /> {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className={styles.form}>
          {/* Campo: Senha Atual */}
          <div className={styles.formGroup}>
            <label htmlFor="current_password">Senha Atual</label>
            <div className={styles.inputWrapper}>
              <input
                id="current_password"
                type={showCurrentPassword ? 'text' : 'password'}
                {...register('current_password')}
                className={errors.current_password ? styles.inputError : ''}
                placeholder="Digite sua senha atual"
              />
              <button
                type="button"
                className={styles.togglePassword}
                onClick={() => setShowCurrentPassword(!showCurrentPassword)}
              >
                {showCurrentPassword ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
            {errors.current_password && (
              <span className={styles.errorText}>
                {errors.current_password.message}
              </span>
            )}
          </div>

          {/* Campo: Nova Senha */}
          <div className={styles.formGroup}>
            <label htmlFor="new_password">Nova Senha</label>
            <div className={styles.inputWrapper}>
              <input
                id="new_password"
                type={showNewPassword ? 'text' : 'password'}
                {...register('new_password')}
                className={errors.new_password ? styles.inputError : ''}
                placeholder="Digite sua nova senha"
              />
              <button
                type="button"
                className={styles.togglePassword}
                onClick={() => setShowNewPassword(!showNewPassword)}
              >
                {showNewPassword ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
            {errors.new_password && (
              <span className={styles.errorText}>
                {errors.new_password.message}
              </span>
            )}

            {/* Indicador de força da senha */}
            {newPassword && (
              <div className={styles.passwordStrength}>
                <p className={styles.strengthTitle}>Requisitos da senha:</p>
                <ul className={styles.strengthList}>
                  <li className={passwordStrength.hasMinLength ? styles.valid : styles.invalid}>
                    {passwordStrength.hasMinLength ? <FiCheck /> : <FiX />}
                    Mínimo 6 caracteres
                  </li>
                  <li className={passwordStrength.hasUpperCase ? styles.valid : styles.invalid}>
                    {passwordStrength.hasUpperCase ? <FiCheck /> : <FiX />}
                    Letra maiúscula
                  </li>
                  <li className={passwordStrength.hasLowerCase ? styles.valid : styles.invalid}>
                    {passwordStrength.hasLowerCase ? <FiCheck /> : <FiX />}
                    Letra minúscula
                  </li>
                  <li className={passwordStrength.hasNumber ? styles.valid : styles.invalid}>
                    {passwordStrength.hasNumber ? <FiCheck /> : <FiX />}
                    Número
                  </li>
                </ul>
              </div>
            )}
          </div>

          {/* Campo: Confirmar Nova Senha */}
          <div className={styles.formGroup}>
            <label htmlFor="confirm_password">Confirmar Nova Senha</label>
            <div className={styles.inputWrapper}>
              <input
                id="confirm_password"
                type={showConfirmPassword ? 'text' : 'password'}
                {...register('confirm_password')}
                className={errors.confirm_password ? styles.inputError : ''}
                placeholder="Confirme sua nova senha"
              />
              <button
                type="button"
                className={styles.togglePassword}
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
            {errors.confirm_password && (
              <span className={styles.errorText}>
                {errors.confirm_password.message}
              </span>
            )}
          </div>

          {/* Botões */}
          <div className={styles.buttonGroup}>
            <button
              type="button"
              className={styles.cancelButton}
              onClick={() => reset()}
              disabled={isLoading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className={styles.submitButton}
              disabled={isLoading}
            >
              {isLoading ? 'Alterando...' : 'Alterar Senha'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

### 3.2. Componente Simples (Sem bibliotecas externas)

Se preferir não usar React Hook Form, aqui está uma versão mais simples:

```typescript
// src/components/ChangePassword/ChangePasswordSimple.tsx

import { useState, FormEvent } from 'react';
import { authService } from '../../services/authService';
import { FiEye, FiEyeOff, FiLock } from 'react-icons/fi';
import styles from './ChangePassword.module.css';

export default function ChangePasswordSimple() {
  const [formData, setFormData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.current_password) {
      newErrors.current_password = 'Senha atual é obrigatória';
    }

    if (!formData.new_password) {
      newErrors.new_password = 'Nova senha é obrigatória';
    } else if (formData.new_password.length < 6) {
      newErrors.new_password = 'Nova senha deve ter no mínimo 6 caracteres';
    }

    if (formData.new_password !== formData.confirm_password) {
      newErrors.confirm_password = 'As senhas não coincidem';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSuccessMessage('');
    setErrorMessage('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      await authService.changePassword({
        current_password: formData.current_password,
        new_password: formData.new_password,
      });

      setSuccessMessage('Senha alterada com sucesso!');
      setFormData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });

      // Opcional: Logout automático
      setTimeout(() => {
        authService.logout();
      }, 2000);

    } catch (error: any) {
      if (error.response?.status === 400) {
        setErrorMessage('Senha atual incorreta');
      } else {
        setErrorMessage('Erro ao alterar senha. Tente novamente.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <FiLock className={styles.icon} />
          <h2>Alterar Senha</h2>
        </div>

        {successMessage && (
          <div className={styles.successAlert}>{successMessage}</div>
        )}

        {errorMessage && (
          <div className={styles.errorAlert}>{errorMessage}</div>
        )}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label>Senha Atual</label>
            <div className={styles.inputWrapper}>
              <input
                type={showPasswords.current ? 'text' : 'password'}
                value={formData.current_password}
                onChange={(e) =>
                  setFormData({ ...formData, current_password: e.target.value })
                }
                placeholder="Digite sua senha atual"
              />
              <button
                type="button"
                onClick={() =>
                  setShowPasswords({ ...showPasswords, current: !showPasswords.current })
                }
              >
                {showPasswords.current ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
            {errors.current_password && (
              <span className={styles.errorText}>{errors.current_password}</span>
            )}
          </div>

          <div className={styles.formGroup}>
            <label>Nova Senha</label>
            <div className={styles.inputWrapper}>
              <input
                type={showPasswords.new ? 'text' : 'password'}
                value={formData.new_password}
                onChange={(e) =>
                  setFormData({ ...formData, new_password: e.target.value })
                }
                placeholder="Digite sua nova senha"
              />
              <button
                type="button"
                onClick={() =>
                  setShowPasswords({ ...showPasswords, new: !showPasswords.new })
                }
              >
                {showPasswords.new ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
            {errors.new_password && (
              <span className={styles.errorText}>{errors.new_password}</span>
            )}
          </div>

          <div className={styles.formGroup}>
            <label>Confirmar Nova Senha</label>
            <div className={styles.inputWrapper}>
              <input
                type={showPasswords.confirm ? 'text' : 'password'}
                value={formData.confirm_password}
                onChange={(e) =>
                  setFormData({ ...formData, confirm_password: e.target.value })
                }
                placeholder="Confirme sua nova senha"
              />
              <button
                type="button"
                onClick={() =>
                  setShowPasswords({ ...showPasswords, confirm: !showPasswords.confirm })
                }
              >
                {showPasswords.confirm ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
            {errors.confirm_password && (
              <span className={styles.errorText}>{errors.confirm_password}</span>
            )}
          </div>

          <button type="submit" disabled={isLoading} className={styles.submitButton}>
            {isLoading ? 'Alterando...' : 'Alterar Senha'}
          </button>
        </form>
      </div>
    </div>
  );
}
```

---

## 🎨 Passo 4: Estilização

Crie o arquivo `src/components/ChangePassword/ChangePassword.module.css`:

```css
/* src/components/ChangePassword/ChangePassword.module.css */

.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  max-width: 500px;
  width: 100%;
}

.header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
}

.header h2 {
  margin: 0;
  color: #2d3748;
  font-size: 24px;
}

.icon {
  font-size: 28px;
  color: #667eea;
}

/* Alertas */
.successAlert,
.errorAlert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
  font-weight: 500;
}

.successAlert {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.errorAlert {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* Formulário */
.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.formGroup {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.formGroup label {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
}

.inputWrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.inputWrapper input {
  width: 100%;
  padding: 12px 45px 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  outline: none;
}

.inputWrapper input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.inputWrapper input::placeholder {
  color: #a0aec0;
}

.inputError {
  border-color: #fc8181 !important;
}

.togglePassword {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  color: #718096;
  font-size: 18px;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.togglePassword:hover {
  color: #667eea;
}

.errorText {
  color: #e53e3e;
  font-size: 12px;
  font-weight: 500;
}

/* Força da senha */
.passwordStrength {
  background-color: #f7fafc;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  margin-top: 8px;
}

.strengthTitle {
  font-size: 12px;
  font-weight: 600;
  color: #4a5568;
  margin: 0 0 8px 0;
}

.strengthList {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.strengthList li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  transition: all 0.2s;
}

.strengthList li svg {
  font-size: 14px;
}

.valid {
  color: #38a169;
}

.invalid {
  color: #718096;
}

/* Botões */
.buttonGroup {
  display: flex;
  gap: 12px;
  margin-top: 10px;
}

.submitButton,
.cancelButton {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submitButton {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.submitButton:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.submitButton:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancelButton {
  background-color: #e2e8f0;
  color: #4a5568;
}

.cancelButton:hover:not(:disabled) {
  background-color: #cbd5e0;
}

/* Responsividade */
@media (max-width: 600px) {
  .card {
    padding: 24px;
  }

  .header h2 {
    font-size: 20px;
  }

  .buttonGroup {
    flex-direction: column;
  }
}
```

---

## 🛣️ Passo 5: Integração com Roteamento

### 5.1. Instalar React Router

```bash
npm install react-router-dom
```

### 5.2. Configurar Rotas

Atualize o arquivo `src/App.tsx`:

```typescript
// src/App.tsx

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { authService } from './services/authService';
import ChangePassword from './components/ChangePassword/ChangePassword';
import Login from './components/Login/Login';
import Dashboard from './components/Dashboard/Dashboard';

// Componente de rota protegida
function ProtectedRoute({ children }: { children: JSX.Element }) {
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/change-password"
          element={
            <ProtectedRoute>
              <ChangePassword />
            </ProtectedRoute>
          }
        />
        
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

### 5.3. Adicionar Link no Menu/Header

```typescript
// Exemplo de link no componente de navegação

import { Link } from 'react-router-dom';
import { FiSettings, FiLock, FiLogOut } from 'react-icons/fi';

function UserMenu() {
  return (
    <div className="user-menu">
      <Link to="/change-password">
        <FiLock /> Alterar Senha
      </Link>
      <button onClick={() => authService.logout()}>
        <FiLogOut /> Sair
      </button>
    </div>
  );
}
```

---

## 🧪 Passo 6: Testes

### 6.1. Teste Manual

1. Inicie o backend:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Inicie o frontend:
```bash
cd frontend
npm run dev
```

3. Acesse `http://localhost:5173/change-password`

4. Teste os cenários:
   - ✅ Alteração com sucesso
   - ❌ Senha atual incorreta
   - ❌ Nova senha muito curta
   - ❌ Senhas não coincidem

### 6.2. Teste com cURL

```bash
# Primeiro, faça login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=seu@email.com&password=suasenha"

# Use o token retornado
TOKEN="seu_token_aqui"

# Teste a alteração de senha
curl -X POST "http://localhost:8000/api/v1/users/me/change-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "senha_atual",
    "new_password": "nova_senha123"
  }'
```

---

## 🚀 Melhorias Opcionais

### 1. Adicionar Toasts de Notificação

```typescript
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// No componente
const onSubmit = async (data) => {
  try {
    await authService.changePassword(data);
    toast.success('Senha alterada com sucesso!');
  } catch (error) {
    toast.error('Erro ao alterar senha');
  }
};

// No JSX
return (
  <>
    <ToastContainer />
    {/* ... resto do componente */}
  </>
);
```

### 2. Modal de Alteração de Senha

```typescript
import { useState } from 'react';
import Modal from 'react-modal';
import ChangePassword from './ChangePassword';

function ChangePasswordModal() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        Alterar Senha
      </button>

      <Modal
        isOpen={isOpen}
        onRequestClose={() => setIsOpen(false)}
        contentLabel="Alterar Senha"
      >
        <ChangePassword onSuccess={() => setIsOpen(false)} />
      </Modal>
    </>
  );
}
```

### 3. Hook Personalizado

```typescript
// src/hooks/useChangePassword.ts

import { useState } from 'react';
import { authService } from '../services/authService';

export function useChangePassword() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const changePassword = async (currentPassword: string, newPassword: string) => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await authService.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setSuccess(true);
      return true;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Erro ao alterar senha';
      setError(errorMsg);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  return { changePassword, isLoading, error, success };
}
```

### 4. Verificador de Senha Comprometida

```typescript
import { useState } from 'react';
import crypto from 'crypto-js';

async function checkPasswordBreach(password: string): Promise<boolean> {
  // Usa a API Have I Been Pwned
  const sha1 = crypto.SHA1(password).toString().toUpperCase();
  const prefix = sha1.substring(0, 5);
  const suffix = sha1.substring(5);

  try {
    const response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`);
    const data = await response.text();
    return data.includes(suffix);
  } catch {
    return false;
  }
}

// Use no componente
const handlePasswordCheck = async (password: string) => {
  const isBreached = await checkPasswordBreach(password);
  if (isBreached) {
    setWarning('Esta senha foi encontrada em vazamentos de dados!');
  }
};
```

### 5. Gerador de Senha Forte

```typescript
function generateStrongPassword(length: number = 12): string {
  const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const lowercase = 'abcdefghijklmnopqrstuvwxyz';
  const numbers = '0123456789';
  const symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?';
  
  const all = uppercase + lowercase + numbers + symbols;
  let password = '';
  
  // Garantir pelo menos um de cada tipo
  password += uppercase[Math.floor(Math.random() * uppercase.length)];
  password += lowercase[Math.floor(Math.random() * lowercase.length)];
  password += numbers[Math.floor(Math.random() * numbers.length)];
  password += symbols[Math.floor(Math.random() * symbols.length)];
  
  // Preencher o resto
  for (let i = password.length; i < length; i++) {
    password += all[Math.floor(Math.random() * all.length)];
  }
  
  // Embaralhar
  return password.split('').sort(() => Math.random() - 0.5).join('');
}

// Adicionar botão no componente
<button type="button" onClick={() => {
  const newPass = generateStrongPassword();
  setValue('new_password', newPass);
  setValue('confirm_password', newPass);
}}>
  Gerar Senha Forte
</button>
```

---

## 📝 Checklist de Implementação

- [ ] Projeto Vite criado com TypeScript
- [ ] Dependências instaladas (axios, react-hook-form, zod, etc.)
- [ ] Variáveis de ambiente configuradas
- [ ] Serviço de API criado com interceptors
- [ ] Serviço de autenticação implementado
- [ ] Componente de alteração de senha criado
- [ ] Estilização aplicada
- [ ] Rotas configuradas com proteção
- [ ] Testes manuais realizados
- [ ] Tratamento de erros implementado
- [ ] Feedback visual para o usuário
- [ ] Validações de formulário funcionando

---

## 🐛 Troubleshooting

### Erro: CORS

Se encontrar erros de CORS, verifique se o backend está configurado corretamente:

```python
# backend/app/main.py

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL do Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Erro: Token não enviado

Verifique se o interceptor está configurado corretamente e se o token está sendo salvo no localStorage após o login.

### Erro: 422 Unprocessable Entity

Verifique se os nomes dos campos no request body correspondem exatamente aos esperados pelo backend (`current_password` e `new_password`).

---

## 📚 Recursos Adicionais

- [React Hook Form Docs](https://react-hook-form.com/)
- [Zod Documentation](https://zod.dev/)
- [Axios Documentation](https://axios-http.com/)
- [React Router v6](https://reactrouter.com/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

## 🎉 Conclusão

Agora você tem uma implementação completa e profissional de alteração de senha no seu frontend React + Vite! O componente inclui:

✅ Validação de formulário robusta  
✅ Feedback visual de força da senha  
✅ Tratamento de erros completo  
✅ UI responsiva e acessível  
✅ Segurança (tokens JWT, HTTPS recomendado)  
✅ Experiência do usuário otimizada  

**Próximos passos sugeridos:**
1. Implementar recuperação de senha por email
2. Adicionar autenticação de dois fatores (2FA)
3. Implementar histórico de senhas anteriores
4. Adicionar política de expiração de senha

---

**Desenvolvido para:** Bacelar Legal Intelligence  
**Data:** 2024  
**Versão:** 1.0
