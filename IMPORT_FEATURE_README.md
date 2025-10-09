# ✅ Endpoint de Importação de Planilhas - Implementado

## 📦 O que foi implementado

### 1. **Novo Endpoint** 
   - **Rota:** `POST /api/v1/excel/import-spreadsheet`
   - **Arquivo:** `app/api/endpoints/excel_import.py`
   - **Autenticação:** JWT Bearer Token
   - **Permissão:** Apenas usuários `ADMIN`

### 2. **Funcionalidades**
   - ✅ Importação de múltiplos prazos de Excel/CSV
   - ✅ Validação de permissões (apenas ADMIN)
   - ✅ Validação de tipo de arquivo (.xlsx, .xls, .csv)
   - ✅ Validação de colunas obrigatórias
   - ✅ Validação de dados por linha
   - ✅ Processamento de datas flexível (YYYY-MM-DD ou DD/MM/YYYY)
   - ✅ Relatório detalhado de sucessos e erros
   - ✅ Continuação do processo mesmo com erros individuais

### 3. **Colunas Suportadas**

#### Obrigatórias:
- `descricao` - Descrição do prazo (mín. 5 caracteres)
- `data_vencimento` - Data no formato YYYY-MM-DD ou DD/MM/YYYY

#### Opcionais:
- `numero_processo` - Número do processo
- `tipo` - Tipo do prazo (Recursal, Processual, etc.)
- `partes` - Partes envolvidas
- `classificacao` - normal, critico ou fatal (padrão: normal)

### 4. **Validações Implementadas**
- ✅ Permissão de usuário (apenas ADMIN)
- ✅ Tipo de arquivo válido
- ✅ Colunas obrigatórias presentes
- ✅ Descrição com mínimo de 5 caracteres
- ✅ Formato de data correto
- ✅ Linhas vazias ignoradas automaticamente

### 5. **Resposta da API**

```json
{
  "message": "Importação concluída. X prazos importados, Y falharam.",
  "imported_count": 15,
  "error_count": 2,
  "imported_deadlines": [
    {
      "id": "uuid",
      "task_description": "Descrição do prazo",
      "due_date": "2024-12-31T00:00:00",
      "classification": "critico"
    }
  ],
  "errors": [
    {
      "linha": 5,
      "erro": "Descrição do erro",
      "descricao": "Descrição do prazo com erro"
    }
  ]
}
```

## 📁 Arquivos Criados/Modificados

### Modificados:
1. **`app/api/endpoints/excel_import.py`**
   - Adicionado novo endpoint `/import-spreadsheet`
   - Mantido endpoint antigo `/import-excel` para compatibilidade

2. **`app/services/deadline_service.py`**
   - Corrigido import de `datetime` (já estava com problema antes)

### Criados:
1. **`IMPORT_SPREADSHEET_GUIDE.md`**
   - Documentação completa do endpoint
   - Exemplos de uso em várias linguagens
   - Guia de integração frontend

2. **`planilha_exemplo_importacao.csv`**
   - Arquivo CSV de exemplo para testes
   - 10 prazos de exemplo com dados variados

3. **`test_import_spreadsheet.py`**
   - Script Python para testes automatizados
   - Valida login, importação e casos de erro

## 🚀 Como Usar

### 1. Via cURL
```bash
curl -X POST "https://bacelar-api.onrender.com/api/v1/excel/import-spreadsheet" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "file=@planilha_exemplo_importacao.csv"
```

### 2. Via Python (requests)
```python
import requests

url = "https://bacelar-api.onrender.com/api/v1/excel/import-spreadsheet"
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("planilha_exemplo_importacao.csv", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

### 3. Via Script de Teste
```bash
# Ajuste as credenciais no arquivo test_import_spreadsheet.py
python test_import_spreadsheet.py
```

## 🧪 Testar Localmente

1. **Iniciar servidor:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Executar teste:**
   ```bash
   python test_import_spreadsheet.py
   ```

3. **Ou usar a planilha exemplo:**
   - Upload via Swagger UI: http://localhost:8000/docs
   - Endpoint: `POST /api/v1/excel/import-spreadsheet`
   - Arquivo: `planilha_exemplo_importacao.csv`

## 📊 Dependências

Todas as dependências necessárias já estão no `requirements.txt`:
- ✅ `pandas` - Processamento de planilhas
- ✅ `openpyxl` - Leitura de arquivos Excel
- ✅ `python-multipart` - Upload de arquivos

## 🔗 Endpoints Relacionados

- `POST /api/v1/excel/import-excel` - Endpoint antigo (formato específico)
- `POST /api/v1/excel/import-spreadsheet` - **NOVO** (formato padronizado)
- `GET /api/v1/deadlines` - Listar prazos
- `POST /api/v1/deadlines` - Criar prazo individual

## ⚠️ Notas Importantes

1. **Apenas ADMIN pode importar:** Usuários com perfil `ADVOGADO` ou `ESTAGIARIO` receberão erro 403
2. **Linhas com erro não param o processo:** O sistema continua processando as demais linhas
3. **Responsável automático:** O usuário que faz a importação é definido como responsável
4. **Notificações automáticas:** Todos os usuários ativos são notificados sobre novos prazos
5. **Histórico registrado:** Cada prazo importado gera registro de histórico

## 🐛 Problemas Conhecidos

Nenhum problema crítico identificado. O endpoint está pronto para uso em produção!

## 📚 Documentação Adicional

- **Guia completo:** `IMPORT_SPREADSHEET_GUIDE.md`
- **API Docs (Swagger):** https://bacelar-api.onrender.com/docs
- **Arquivo exemplo:** `planilha_exemplo_importacao.csv`

---

**Status:** ✅ IMPLEMENTADO E PRONTO PARA USO  
**Versão:** 1.0.0  
**Data:** Janeiro 2025
