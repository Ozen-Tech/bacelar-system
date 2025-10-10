# 🔐 Scripts de Diagnóstico e Senha

Este documento lista os scripts criados para diagnóstico e resolução de problemas relacionados a senhas.

---

## 📋 Scripts Disponíveis

### 1. 🔍 **diagnose_password_issue.py**
**Diagnóstico completo de problemas com senha**

```bash
python diagnose_password_issue.py
```

**O que faz:**
- Busca usuário no banco de dados
- Verifica o hash da senha armazenado
- Testa se a senha fornecida está correta
- Testa variações comuns (espaços, maiúsculas, etc.)
- Oferece opção para resetar senha imediatamente

**Quando usar:**
- Usuário não consegue fazer login
- Suspeita de senha corrompida no banco
- Verificar qual é a senha atual de um usuário

---

### 2. 🧪 **test_change_password_flow.py**
**Teste completo do fluxo de troca de senha**

```bash
python test_change_password_flow.py
```

**O que faz:**
- Login com senha atual
- Busca dados do usuário logado
- Tenta trocar a senha
- Testa login com a nova senha
- Reverte senha para o valor original

**Quando usar:**
- Usuário diz que não consegue trocar senha
- Testar se o endpoint de troca de senha funciona
- Verificar todo o fluxo de autenticação

---

### 3. 🔄 **reset_user_password.py**
**Resetar senha de qualquer usuário**

```bash
python reset_user_password.py
```

**O que faz:**
- Lista todos os usuários do sistema
- Permite resetar senha de qualquer usuário
- Gera novo hash seguro
- Confirmação obrigatória antes de executar

**Quando usar:**
- Usuário esqueceu a senha
- Senha corrompida no banco
- Primeiro acesso de um usuário novo

---

## 🚀 Guia Rápido de Uso

### Cenário 1: Usuário não consegue trocar senha

**Passo 1:** Verificar se a senha atual está correta
```bash
python diagnose_password_issue.py
# Digite o email e a senha atual
```

**Passo 2:** Testar o fluxo completo via API
```bash
python test_change_password_flow.py
# Siga as instruções interativas
```

**Resultado:**
- ✅ Se o teste passar: O problema está no frontend
- ❌ Se o teste falhar: O problema está na senha atual

---

### Cenário 2: Usuário esqueceu a senha

**Solução:** Resetar a senha
```bash
python reset_user_password.py
# Escolha opção 1
# Digite o email do usuário
# Digite a nova senha (ex: novaSenha123)
```

---

### Cenário 3: Verificar usuários no sistema

**Listar todos os usuários:**
```bash
python reset_user_password.py
# Escolha opção 2
```

---

## 📖 Documentação Completa

Para guia completo de diagnóstico, veja:
- **PASSWORD_CHANGE_TROUBLESHOOTING.md** - Guia detalhado de troubleshooting

---

## ⚠️ Requisitos

Todos os scripts precisam:
- Python 3.11+
- Banco de dados configurado
- Arquivo `.env` com credenciais corretas
- Executar no diretório raiz do projeto

---

## 🔒 Segurança

**IMPORTANTE:**
- ⚠️ Nunca compartilhe senhas por email ou chat
- ⚠️ Use senhas temporárias quando resetar
- ⚠️ Oriente o usuário a trocar a senha após reset
- ⚠️ Senhas devem ter no mínimo 6 caracteres

---

## 💡 Dicas

1. **Sempre teste primeiro:**
   - Use `diagnose_password_issue.py` antes de resetar senha
   
2. **Senhas temporárias sugeridas:**
   - `novaSenha123`
   - `senha123`
   - `Trocar@123`

3. **Para produção:**
   - Configure variável `DATABASE_URL` para apontar para banco de produção
   - Use sempre senha forte ao resetar

---

## 🐛 Problemas Comuns

### Erro: "ModuleNotFoundError"
**Solução:** Execute no diretório raiz do projeto onde está a pasta `app/`

### Erro: "Could not connect to database"
**Solução:** Verifique se o banco de dados está rodando e se o `.env` está correto

### Erro: "User not found"
**Solução:** Verifique se digitou o email corretamente (case-sensitive)

---

## 📞 Suporte

Se os problemas persistirem após usar todos os scripts:
1. Verifique os logs do servidor
2. Teste a API diretamente (Swagger UI: `/docs`)
3. Verifique o código do frontend
4. Consulte `PASSWORD_CHANGE_TROUBLESHOOTING.md`

---

**Última atualização:** Janeiro 2025
