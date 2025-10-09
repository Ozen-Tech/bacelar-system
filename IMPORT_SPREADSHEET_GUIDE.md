# 📋 Guia de Importação de Planilhas - Bacelar Legal Intelligence

Este documento explica como usar o endpoint de importação de prazos via planilha Excel/CSV.

## 🎯 Endpoint

```
POST /api/v1/excel/import-spreadsheet
```

**Autenticação:** Bearer Token (JWT)  
**Permissão:** Apenas usuários com perfil `ADMIN`

---

## 📊 Formato da Planilha

### Colunas Obrigatórias

| Coluna           | Tipo     | Descrição                                    | Exemplo                          |
|------------------|----------|----------------------------------------------|----------------------------------|
| `descricao`      | string   | Descrição do prazo (mín. 5 caracteres)      | "Apresentar recurso de apelação" |
| `data_vencimento`| date     | Data no formato YYYY-MM-DD ou DD/MM/YYYY    | "2024-12-31" ou "31/12/2024"     |

### Colunas Opcionais

| Coluna            | Tipo   | Descrição                              | Exemplo                    |
|-------------------|--------|----------------------------------------|----------------------------|
| `numero_processo` | string | Número do processo                     | "0001234-56.2024.8.02.0001"|
| `tipo`            | string | Tipo do prazo                          | "Recursal", "Processual"   |
| `partes`          | string | Partes envolvidas                      | "João Silva vs. Maria José"|
| `classificacao`   | string | normal, critico ou fatal (padrão: normal) | "critico"             |

---

## 📁 Tipos de Arquivo Aceitos

- ✅ `.xlsx` (Excel 2007+)
- ✅ `.xls` (Excel 97-2003)
- ✅ `.csv` (Valores separados por vírgula)

---

## 🔧 Exemplo de Uso

### 1. Criar Planilha Excel

**Exemplo de conteúdo:**

| descricao                          | data_vencimento | numero_processo        | tipo      | partes                | classificacao |
|------------------------------------|-----------------|------------------------|-----------|-----------------------|---------------|
| Apresentar recurso de apelação     | 2024-12-15      | 0001234-56.2024.8.02.0001 | Recursal  | João vs. Maria       | critico       |
| Contestação no processo trabalhista| 31/12/2024      | 0007890-12.2024.5.02.0001 | Processual| Empresa X vs. João   | normal        |
| Audiência de conciliação           | 2025-01-10      | 0005555-99.2024.8.02.0001 | Audiência | Maria vs. José       | fatal         |

### 2. Fazer Requisição via cURL

```bash
curl -X POST "https://bacelar-api.onrender.com/api/v1/excel/import-spreadsheet" \
  -H "Authorization: Bearer SEU_TOKEN_JWT_AQUI" \
  -F "file=@planilha_prazos.xlsx"
```

### 3. Fazer Requisição via JavaScript (Fetch)

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('https://bacelar-api.onrender.com/api/v1/excel/import-spreadsheet', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const result = await response.json();
console.log(result);
```

### 4. Fazer Requisição via Python (requests)

```python
import requests

url = "https://bacelar-api.onrender.com/api/v1/excel/import-spreadsheet"
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("planilha_prazos.xlsx", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

---

## 📤 Resposta da API

### Sucesso (200 OK)

```json
{
  "message": "Importação concluída. 15 prazos importados, 2 falharam.",
  "imported_count": 15,
  "error_count": 2,
  "imported_deadlines": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "task_description": "Apresentar recurso de apelação",
      "due_date": "2024-12-15T00:00:00",
      "classification": "critico"
    },
    {
      "id": "f9e8d7c6-b5a4-3210-fedc-ba0987654321",
      "task_description": "Contestação no processo trabalhista",
      "due_date": "2024-12-31T00:00:00",
      "classification": "normal"
    }
  ],
  "errors": [
    {
      "linha": 5,
      "erro": "Descrição deve ter pelo menos 5 caracteres",
      "descricao": "Aud"
    },
    {
      "linha": 8,
      "erro": "Erro na data: Formato de data inválido. Use YYYY-MM-DD ou DD/MM/YYYY",
      "descricao": "Prazo com data inválida"
    }
  ]
}
```

### Erros Comuns

#### 403 Forbidden - Permissão Negada
```json
{
  "detail": "Apenas usuários ADMIN podem importar prazos"
}
```

**Solução:** Verifique se o usuário logado possui perfil `ADMIN`.

#### 400 Bad Request - Tipo de Arquivo Inválido
```json
{
  "detail": "Arquivo deve ser Excel (.xlsx, .xls) ou CSV"
}
```

**Solução:** Certifique-se de enviar arquivo com extensão `.xlsx`, `.xls` ou `.csv`.

#### 400 Bad Request - Colunas Faltando
```json
{
  "detail": "Colunas obrigatórias faltando: descricao, data_vencimento"
}
```

**Solução:** Verifique se a planilha contém as colunas obrigatórias: `descricao` e `data_vencimento`.

---

## ✅ Validações Aplicadas

### 1. Validação de Permissão
- ✅ Apenas usuários com perfil `ADMIN` podem importar

### 2. Validação de Arquivo
- ✅ Tipo de arquivo: `.xlsx`, `.xls` ou `.csv`
- ✅ Colunas obrigatórias presentes

### 3. Validação de Dados por Linha
- ✅ **Descrição:** Mínimo de 5 caracteres
- ✅ **Data:** Formato YYYY-MM-DD ou DD/MM/YYYY
- ✅ **Linhas vazias:** Ignoradas automaticamente
- ✅ **Erros:** Registrados sem interromper o processo

### 4. Comportamento de Erro
- ❌ Linhas com erro **não são importadas**
- ✅ Linhas válidas **são importadas normalmente**
- ✅ Relatório completo de sucessos e erros é retornado

---

## 🎨 Exemplo Completo de Integração Frontend (React)

```tsx
import { useState } from 'react';

function ImportarPlanilha() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Selecione um arquivo');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        'https://bacelar-api.onrender.com/api/v1/excel/import-spreadsheet',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        }
      );

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Erro ao importar planilha');
      }

      setResult(data);
      alert(`✅ ${data.message}`);
    } catch (error: any) {
      alert(`❌ Erro: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Importar Prazos</h2>
      
      <div className="space-y-4">
        <input
          type="file"
          accept=".xlsx,.xls,.csv"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100"
        />
        
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg 
                     hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Importando...' : 'Importar Planilha'}
        </button>
      </div>

      {result && (
        <div className="mt-6 p-4 bg-gray-100 rounded-lg">
          <h3 className="font-bold mb-2">Resultado:</h3>
          <p>✅ Importados: {result.imported_count}</p>
          <p>❌ Erros: {result.error_count}</p>
          
          {result.errors.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold text-red-600">Erros:</h4>
              <ul className="list-disc pl-5">
                {result.errors.map((error: any, idx: number) => (
                  <li key={idx}>
                    Linha {error.linha}: {error.erro}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ImportarPlanilha;
```

---

## 📝 Notas Importantes

1. **Formato de Data Flexível:** O sistema aceita tanto `YYYY-MM-DD` quanto `DD/MM/YYYY`
2. **Case Insensitive:** Os nomes das colunas não diferenciam maiúsculas/minúsculas
3. **Linhas Vazias:** São automaticamente ignoradas
4. **Classificação Padrão:** Se não especificada, será `normal`
5. **Responsável:** O usuário que faz a importação é automaticamente definido como responsável
6. **Histórico:** Cada prazo importado gera um registro de histórico automático
7. **Notificações:** Todos os usuários ativos são notificados sobre os novos prazos

---

## 🔗 Endpoints Relacionados

- `POST /api/v1/excel/import-excel` - Importação antiga (formato específico)
- `GET /api/v1/deadlines` - Listar todos os prazos
- `POST /api/v1/deadlines` - Criar prazo individual
- `GET /api/v1/deadlines/{id}` - Buscar prazo específico

---

## 📞 Suporte

Em caso de dúvidas ou problemas:
- 📧 Email: suporte@bacelar.com.br
- 📖 Documentação completa: https://bacelar-api.onrender.com/docs
