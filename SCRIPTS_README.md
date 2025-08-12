# 🏛️ Scripts de Gerenciamento de Usuários - Bacelar Advocacia

Este diretório contém scripts para criar e gerenciar contas de usuário no sistema.

## 📋 Scripts Disponíveis

### 1. `create_users.py` - Script Interativo Completo

**Descrição:** Script interativo com menu para gerenciar usuários.

**Funcionalidades:**
- ✅ Criação interativa de usuários
- ✅ Criação de usuários de demonstração
- ✅ Listagem de todos os usuários
- ✅ Validações completas
- ✅ Interface amigável

**Como usar:**
```bash
cd /Users/ozen/bacelar-advocacia
python create_users.py
```

**Menu de opções:**
1. Criar usuário (interativo)
2. Criar usuários de demonstração
3. Listar usuários
4. Sair

---

### 2. `quick_create_user.py` - Criação Rápida via Linha de Comando

**Descrição:** Script para criação rápida de usuários via argumentos de linha de comando.

**Sintaxe:**
```bash
python quick_create_user.py "Nome" "email@exemplo.com" "senha" "perfil" ["telefone"]
```

**Perfis disponíveis:**
- `admin` - Administrador
- `advogado` - Advogado
- `estagiario` - Estagiário

**Exemplos:**
```bash
# Criar advogado
python quick_create_user.py "João Silva" "joao@bacelar.com" "senha123" "advogado"

# Criar admin com telefone
python quick_create_user.py "Maria Admin" "maria@bacelar.com" "senha123" "admin" "(11) 99999-1111"

# Criar estagiário
python quick_create_user.py "Pedro Oliveira" "pedro@bacelar.com" "senha123" "estagiario"
```

---

### 3. `app/scripts/create_superuser.py` - Criação do Superusuário

**Descrição:** Script para criar o superusuário inicial do sistema.

**Como usar:**
```bash
cd /Users/ozen/bacelar-advocacia
python app/scripts/create_superuser.py
```

**Nota:** Este script usa as variáveis de ambiente `SUPERUSER_EMAIL` e `SUPERUSER_PASSWORD` definidas no arquivo `.env`.

---

## 🚀 Usuários de Demonstração

O script `create_users.py` pode criar os seguintes usuários de demonstração:

| Nome | Email | Perfil | Telefone | Senha |
|------|-------|--------|----------|-------|
| João Silva | joao.silva@bacelar.com | Advogado | (11) 99999-1111 | senha123 |
| Maria Santos | maria.santos@bacelar.com | Advogado | (11) 99999-2222 | senha123 |
| Pedro Oliveira | pedro.oliveira@bacelar.com | Estagiário | (11) 99999-3333 | senha123 |
| Ana Costa | ana.costa@bacelar.com | Admin | (11) 99999-4444 | senha123 |

---

## ⚙️ Pré-requisitos

1. **Ambiente virtual ativado:**
   ```bash
   cd /Users/ozen/bacelar-advocacia
   source venv/bin/activate
   ```

2. **Banco de dados configurado e rodando**

3. **Variáveis de ambiente configuradas** (arquivo `.env`)

---

## 🔒 Perfis de Usuário

### Admin (Administrador)
- ✅ Acesso completo ao sistema
- ✅ Gerenciar usuários
- ✅ Gerenciar prazos
- ✅ Configurações do sistema

### Advogado
- ✅ Criar e gerenciar prazos
- ✅ Visualizar relatórios
- ✅ Gerenciar próprios casos

### Estagiário
- ✅ Visualizar prazos
- ✅ Criar prazos (com aprovação)
- ❌ Acesso limitado

---

## 🛠️ Solução de Problemas

### Erro: "Usuário já existe"
- **Causa:** Email já cadastrado no sistema
- **Solução:** Use um email diferente ou verifique a lista de usuários

### Erro: "Senha deve ter pelo menos 6 caracteres"
- **Causa:** Senha muito curta
- **Solução:** Use uma senha com 6 ou mais caracteres

### Erro: "Perfil inválido"
- **Causa:** Perfil não reconhecido
- **Solução:** Use apenas: `admin`, `advogado` ou `estagiario`

### Erro de conexão com banco
- **Causa:** Banco de dados não está rodando
- **Solução:** Verifique se o PostgreSQL está ativo e as configurações estão corretas

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se o ambiente virtual está ativado
2. Confirme se o banco de dados está rodando
3. Verifique as variáveis de ambiente no arquivo `.env`
4. Execute os scripts a partir do diretório raiz do projeto

---

**Última atualização:** Dezembro 2024