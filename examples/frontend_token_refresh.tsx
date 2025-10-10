// ============================================
// EXEMPLO 1: Hook React para Auto-Refresh
// ============================================

import { useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

interface DecodedToken {
  sub: string;
  exp: number;
  profile: string;
}

export const useTokenRefresh = () => {
  useEffect(() => {
    const checkAndRefreshToken = async () => {
      const token = localStorage.getItem('token');
      
      if (!token) return;
      
      try {
        const decoded = jwtDecode<DecodedToken>(token);
        const currentTime = Date.now() / 1000;
        const timeUntilExpiry = decoded.exp - currentTime;
        
        // Se faltar menos de 1 hora para expirar, renova
        if (timeUntilExpiry < 3600) {
          console.log('🔄 Token expirando em breve, renovando...');
          
          const response = await fetch('https://bacelar-api.onrender.com/api/v1/auth/refresh', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            console.log('✅ Token renovado com sucesso!');
          } else if (response.status === 401) {
            console.log('❌ Token inválido, redirecionando para login...');
            localStorage.removeItem('token');
            window.location.href = '/login';
          }
        }
      } catch (error) {
        console.error('Erro ao verificar token:', error);
      }
    };
    
    // Verifica a cada 5 minutos
    const interval = setInterval(checkAndRefreshToken, 5 * 60 * 1000);
    
    // Verifica imediatamente ao montar
    checkAndRefreshToken();
    
    return () => clearInterval(interval);
  }, []);
};

// ============================================
// EXEMPLO 2: Interceptor Axios com Refresh
// ============================================

import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const api = axios.create({
  baseURL: 'https://bacelar-api.onrender.com/api/v1'
});

// Flag para evitar múltiplos refreshes simultâneos
let isRefreshing = false;
let failedQueue: Array<any> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

// Interceptor de requisição
api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('token');
    
    if (token) {
      try {
        const decoded = jwtDecode<DecodedToken>(token);
        const currentTime = Date.now() / 1000;
        
        // Se o token já expirou
        if (decoded.exp < currentTime) {
          console.log('❌ Token expirado');
          localStorage.removeItem('token');
          window.location.href = '/login';
          throw new Error('Token expirado');
        }
        
        // Se falta menos de 5 minutos para expirar, tenta renovar
        if (decoded.exp < currentTime + 300) {
          console.log('⚠️  Token expirando em breve, tentando renovar...');
          
          if (!isRefreshing) {
            isRefreshing = true;
            
            try {
              const response = await axios.post(
                'https://bacelar-api.onrender.com/api/v1/auth/refresh',
                {},
                {
                  headers: { Authorization: `Bearer ${token}` }
                }
              );
              
              const newToken = response.data.access_token;
              localStorage.setItem('token', newToken);
              config.headers.Authorization = `Bearer ${newToken}`;
              
              processQueue(null, newToken);
              isRefreshing = false;
              
              console.log('✅ Token renovado com sucesso!');
            } catch (error) {
              processQueue(error, null);
              isRefreshing = false;
              
              localStorage.removeItem('token');
              window.location.href = '/login';
              throw error;
            }
          } else {
            // Aguarda o refresh em andamento
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject });
            }).then((newToken) => {
              config.headers.Authorization = `Bearer ${newToken}`;
              return config;
            });
          }
        } else {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (error) {
        console.error('Erro ao processar token:', error);
      }
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor de resposta
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Se receber 401 e ainda não tentou refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const token = localStorage.getItem('token');
      
      if (token && !isRefreshing) {
        isRefreshing = true;
        
        try {
          const response = await axios.post(
            'https://bacelar-api.onrender.com/api/v1/auth/refresh',
            {},
            {
              headers: { Authorization: `Bearer ${token}` }
            }
          );
          
          const newToken = response.data.access_token;
          localStorage.setItem('token', newToken);
          
          // Atualiza o header da requisição original
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          
          processQueue(null, newToken);
          isRefreshing = false;
          
          // Reexecuta a requisição original com novo token
          return api(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError, null);
          isRefreshing = false;
          
          // Se o refresh falhar, faz logout
          localStorage.removeItem('token');
          window.location.href = '/login';
          
          return Promise.reject(refreshError);
        }
      } else if (isRefreshing) {
        // Aguarda o refresh em andamento
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(api(originalRequest));
            },
            reject: (err: any) => reject(err)
          });
        });
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;

// ============================================
// EXEMPLO 3: Uso no Componente React
// ============================================

import React, { useEffect, useState } from 'react';
import { useTokenRefresh } from './hooks/useTokenRefresh';
import api from './api/axiosInstance';

const App: React.FC = () => {
  // Hook que renova o token automaticamente
  useTokenRefresh();
  
  const [deadlines, setDeadlines] = useState([]);
  
  useEffect(() => {
    loadDeadlines();
  }, []);
  
  const loadDeadlines = async () => {
    try {
      // Usa a instância do axios com interceptor
      const response = await api.get('/deadlines');
      setDeadlines(response.data);
    } catch (error) {
      console.error('Erro ao carregar prazos:', error);
    }
  };
  
  const createDeadline = async (data: any) => {
    try {
      // O interceptor vai garantir que o token está válido
      const response = await api.post('/deadlines', data);
      console.log('✅ Prazo criado:', response.data);
      loadDeadlines(); // Recarrega a lista
    } catch (error: any) {
      if (error.response?.status === 401) {
        alert('Sua sessão expirou. Faça login novamente.');
      } else {
        alert('Erro ao criar prazo.');
      }
    }
  };
  
  return (
    <div>
      {/* Seu conteúdo aqui */}
    </div>
  );
};

export default App;

// ============================================
// EXEMPLO 4: Função Manual de Refresh
// ============================================

export const refreshToken = async (): Promise<string | null> => {
  try {
    const currentToken = localStorage.getItem('token');
    
    if (!currentToken) {
      console.log('❌ Nenhum token encontrado');
      return null;
    }
    
    console.log('🔄 Renovando token...');
    
    const response = await fetch('https://bacelar-api.onrender.com/api/v1/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${currentToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      console.log('❌ Erro ao renovar token:', response.status);
      
      if (response.status === 401) {
        // Token inválido ou expirado demais
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      
      return null;
    }
    
    const data = await response.json();
    const newToken = data.access_token;
    
    localStorage.setItem('token', newToken);
    console.log('✅ Token renovado com sucesso!');
    
    return newToken;
  } catch (error) {
    console.error('Erro ao renovar token:', error);
    return null;
  }
};

// Uso:
// await refreshToken();

// ============================================
// EXEMPLO 5: Verificar se Token Precisa Refresh
// ============================================

import { jwtDecode } from 'jwt-decode';

export const shouldRefreshToken = (token: string, minutesBefore: number = 60): boolean => {
  try {
    const decoded = jwtDecode<DecodedToken>(token);
    const currentTime = Date.now() / 1000;
    const timeUntilExpiry = decoded.exp - currentTime;
    
    // Retorna true se faltar menos que X minutos para expirar
    return timeUntilExpiry < (minutesBefore * 60);
  } catch {
    return true; // Se não conseguir decodificar, assume que precisa refresh
  }
};

export const isTokenExpired = (token: string): boolean => {
  try {
    const decoded = jwtDecode<DecodedToken>(token);
    const currentTime = Date.now() / 1000;
    
    return decoded.exp < currentTime;
  } catch {
    return true;
  }
};

// Uso:
const token = localStorage.getItem('token');
if (token && shouldRefreshToken(token, 30)) {
  // Renova se faltar menos de 30 minutos
  await refreshToken();
}

// ============================================
// INSTALAÇÃO DE DEPENDÊNCIAS
// ============================================

/*
npm install jwt-decode axios

ou

yarn add jwt-decode axios
*/
