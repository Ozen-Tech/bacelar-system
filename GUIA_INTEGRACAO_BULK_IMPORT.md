# 📤 Guia de Integração: Importação em Massa de Deadlines (JSON)

> Guia completo para implementar a importação em massa de prazos via JSON no frontend React + Vite

---

## 📋 Índice

1. [Informações do Backend](#informações-do-backend)
2. [Diferença entre os Endpoints](#diferença-entre-os-endpoints)
3. [Passo 1: Criar Tipos TypeScript](#passo-1-criar-tipos-typescript)
4. [Passo 2: Criar Serviço de API](#passo-2-criar-serviço-de-api)
5. [Passo 3: Componente de Importação JSON](#passo-3-componente-de-importação-json)
6. [Passo 4: Componente com Upload de Arquivo](#passo-4-componente-com-upload-de-arquivo)
7. [Passo 5: Estilização](#passo-5-estilização)
8. [Passo 6: Integração Completa](#passo-6-integração-completa)
9. [Exemplos de Uso](#exemplos-de-uso)
10. [Troubleshooting](#troubleshooting)

---

## 📌 Informações do Backend

### Endpoint de Importação em Massa (JSON)

```
POST /api/v1/deadlines/bulk
```

#### Autenticação
- **Requerida**: Sim (Bearer Token JWT)
- **Perfil Necessário**: ADMIN
- **Header**: `Authorization: Bearer {seu_token_jwt}`

#### Request Body

```typescript
{
  "deadlines": [
    {
      "task_description": "Apresentar contestação",
      "due_date": "2024-12-31T23:59:59",
      "process_number": "1234567-89.2024.8.01.0001",  // Opcional
      "type": "Recursal",                             // Opcional
      "parties": "João Silva vs. Maria José",         // Opcional
      "status": "pendente",                           // Padrão: "pendente"
      "responsible_user_id": "uuid-do-usuario"        // Opcional
    }
    // ... até 500 deadlines por requisição
  ],
  "skip_notifications": true,  // Padrão: true
  "skip_celery": true          // Padrão: true
}
```

#### Response (201 Created)

```json
{
  "total_received": 10,
  "imported_count": 8,
  "error_count": 2,
  "deadlines": [
    {
      "id": "uuid",
      "task_description": "Apresentar contestação",
      "due_date": "2024-12-31T23:59:59Z",
      "process_number": "1234567-89.2024.8.01.0001",
      "type": "Recursal",
      "parties": "João Silva vs. Maria José",
      "status": "pendente",
      "classification": "normal",
      "responsible_user_id": "uuid",
      "responsible": {
        "id": "uuid",
        "name": "João Silva",
        "email": "joao@example.com",
        "profile": "advogado"
      },
      "history": [],
      "attachments": [],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": null
    }
  ],
  "errors": [
    {
      "index": 3,
      "task_description": "Descrição curta",
      "error": "task_description deve ter no mínimo 5 caracteres"
    },
    {
      "index": 7,
      "task_description": "Prazo inválido",
      "error": "due_date inválido"
    }
  ]
}
```

#### Possíveis Respostas de Erro

**❌ 401 Unauthorized**
```json
{
  "detail": "Could not validate credentials"
}
```

**❌ 403 Forbidden**
```json
{
  "detail": "Apenas usuários ADMIN podem criar prazos em massa"
}
```

**❌ 422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "loc": ["body", "deadlines", 0, "task_description"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🔄 Diferença entre os Endpoints

| Característica | `/deadlines/bulk` (JSON) | `/excel/import-spreadsheet` (Excel/CSV) |
|---------------|-------------------------|----------------------------------------|
| **Formato** | JSON | Excel (.xlsx, .xls) ou CSV |
| **Tipo de Request** | `application/json` | `multipart/form-data` |
| **Uso Principal** | Integração entre sistemas, API | Upload de arquivo pelo usuário |
| **Frontend** | Formulário ou dados programáticos | Upload de arquivo |
| **Validação** | Pydantic (backend) | Pandas + validação customizada |
| **Limite** | 500 deadlines/requisição | Sem limite especificado |
| **Flexibilidade** | Alta (programático) | Média (depende do formato do arquivo) |

**Quando usar cada um:**
- **`/bulk`**: Quando você já tem os dados em memória (ex: formulário, integração com outro sistema, conversão de CSV no frontend)
- **`/import-spreadsheet`**: Quando o usuário vai fazer upload direto de um arquivo Excel/CSV

---

## 🚀 Passo 1: Criar Tipos TypeScript

Crie o arquivo `src/types/deadline.types.ts`:

```typescript
// src/types/deadline.types.ts

export enum DeadlineStatus {
  PENDENTE = "pendente",
  CONCLUIDO = "concluido",
  CANCELADO = "cancelado"
}

export enum DeadlineClassification {
  NORMAL = "normal",
  CRITICO = "critico",
  FATAL = "fatal"
}

export interface UserPublic {
  id: string;
  name: string;
  email: string;
  profile: "admin" | "advogado" | "estagiario";
}

export interface DeadlineCreate {
  task_description: string;
  due_date: string; // ISO 8601 format
  process_number?: string;
  type?: string;
  parties?: string;
  status?: DeadlineStatus;
  responsible_user_id?: string;
}

export interface DeadlinePublic extends DeadlineCreate {
  id: string;
  classification: DeadlineClassification;
  responsible?: UserPublic;
  history: any[];
  attachments: any[];
  created_at: string;
  updated_at: string | null;
}

export interface BulkDeadlineError {
  index: number;
  task_description?: string;
  error: string;
}

export interface BulkImportRequest {
  deadlines: DeadlineCreate[];
  skip_notifications?: boolean;
  skip_celery?: boolean;
}

export interface BulkImportResponse {
  total_received: number;
  imported_count: number;
  error_count: number;
  deadlines: DeadlinePublic[];
  errors: BulkDeadlineError[];
}
```

---

## 🔧 Passo 2: Criar Serviço de API

Crie o arquivo `src/services/deadlineService.ts`:

```typescript
// src/services/deadlineService.ts

import api from './api';
import {
  DeadlineCreate,
  DeadlinePublic,
  BulkImportRequest,
  BulkImportResponse,
} from '../types/deadline.types';

export const deadlineService = {
  /**
   * Cria um único deadline
   */
  createDeadline: async (deadline: DeadlineCreate): Promise<DeadlinePublic> => {
    const response = await api.post('/deadlines/', deadline);
    return response.data;
  },

  /**
   * Cria múltiplos deadlines de uma vez (importação em massa via JSON)
   */
  createDeadlinesBulk: async (
    data: BulkImportRequest
  ): Promise<BulkImportResponse> => {
    const response = await api.post('/deadlines/bulk', data);
    return response.data;
  },

  /**
   * Lista todos os deadlines com filtros opcionais
   */
  listDeadlines: async (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    type?: string;
    responsible_id?: string;
    classification?: string;
    status?: string;
    due_date_from?: string;
    due_date_to?: string;
  }): Promise<DeadlinePublic[]> => {
    const response = await api.get('/deadlines/', { params });
    return response.data;
  },

  /**
   * Obtém um deadline específico
   */
  getDeadline: async (deadlineId: string): Promise<DeadlinePublic> => {
    const response = await api.get(`/deadlines/${deadlineId}`);
    return response.data;
  },

  /**
   * Importa deadlines de arquivo Excel/CSV
   */
  importFromSpreadsheet: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/excel/import-spreadsheet', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default deadlineService;
```

---

## 🎨 Passo 3: Componente de Importação JSON

Crie o arquivo `src/components/BulkImport/BulkImportJSON.tsx`:

```typescript
// src/components/BulkImport/BulkImportJSON.tsx

import { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { deadlineService } from '../../services/deadlineService';
import { DeadlineStatus, BulkImportResponse } from '../../types/deadline.types';
import { FiPlus, FiTrash2, FiUpload, FiAlertCircle, FiCheckCircle } from 'react-icons/fi';
import styles from './BulkImport.module.css';

// Schema de validação
const deadlineSchema = z.object({
  task_description: z.string().min(5, 'Descrição deve ter no mínimo 5 caracteres'),
  due_date: z.string().min(1, 'Data de vencimento é obrigatória'),
  process_number: z.string().optional(),
  type: z.string().optional(),
  parties: z.string().optional(),
  status: z.nativeEnum(DeadlineStatus).optional(),
  responsible_user_id: z.string().uuid().optional(),
});

const bulkImportSchema = z.object({
  deadlines: z.array(deadlineSchema).min(1, 'Adicione pelo menos um prazo'),
  skip_notifications: z.boolean(),
  skip_celery: z.boolean(),
});

type BulkImportFormData = z.infer<typeof bulkImportSchema>;

export default function BulkImportJSON() {
  const [isLoading, setIsLoading] = useState(false);
  const [importResult, setImportResult] = useState<BulkImportResponse | null>(null);

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<BulkImportFormData>({
    resolver: zodResolver(bulkImportSchema),
    defaultValues: {
      deadlines: [
        {
          task_description: '',
          due_date: '',
          process_number: '',
          type: '',
          parties: '',
          status: DeadlineStatus.PENDENTE,
        },
      ],
      skip_notifications: true,
      skip_celery: true,
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'deadlines',
  });

  const onSubmit = async (data: BulkImportFormData) => {
    setIsLoading(true);
    setImportResult(null);

    try {
      // Formatar datas para ISO 8601
      const formattedData = {
        ...data,
        deadlines: data.deadlines.map((deadline) => ({
          ...deadline,
          due_date: new Date(deadline.due_date).toISOString(),
        })),
      };

      const result = await deadlineService.createDeadlinesBulk(formattedData);
      setImportResult(result);

      // Se tudo foi importado com sucesso, limpar o formulário
      if (result.error_count === 0) {
        reset();
      }
    } catch (error: any) {
      console.error('Erro ao importar:', error);
      alert(
        error.response?.data?.detail || 'Erro ao importar prazos. Tente novamente.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>Importação em Massa (JSON)</h2>
        <p>Adicione múltiplos prazos de uma vez preenchendo o formulário abaixo</p>
      </div>

      {/* Resultado da importação */}
      {importResult && (
        <div className={styles.resultBox}>
          <div className={styles.resultSummary}>
            <div className={styles.statCard}>
              <span className={styles.statLabel}>Total Recebido</span>
              <span className={styles.statValue}>{importResult.total_received}</span>
            </div>
            <div className={`${styles.statCard} ${styles.success}`}>
              <FiCheckCircle />
              <span className={styles.statLabel}>Importados</span>
              <span className={styles.statValue}>{importResult.imported_count}</span>
            </div>
            <div className={`${styles.statCard} ${styles.error}`}>
              <FiAlertCircle />
              <span className={styles.statLabel}>Erros</span>
              <span className={styles.statValue}>{importResult.error_count}</span>
            </div>
          </div>

          {/* Lista de erros */}
          {importResult.errors.length > 0 && (
            <div className={styles.errorsList}>
              <h3>Erros Encontrados:</h3>
              {importResult.errors.map((error) => (
                <div key={error.index} className={styles.errorItem}>
                  <FiAlertCircle />
                  <span>
                    <strong>Linha {error.index + 1}:</strong> {error.error}
                    {error.task_description && ` (${error.task_description})`}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Lista de sucessos */}
          {importResult.deadlines.length > 0 && (
            <div className={styles.successList}>
              <h3>Prazos Criados com Sucesso:</h3>
              <ul>
                {importResult.deadlines.map((deadline) => (
                  <li key={deadline.id}>
                    <FiCheckCircle />
                    {deadline.task_description} - {new Date(deadline.due_date).toLocaleDateString()}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className={styles.form}>
        {/* Lista de deadlines */}
        <div className={styles.deadlinesList}>
          {fields.map((field, index) => (
            <div key={field.id} className={styles.deadlineCard}>
              <div className={styles.cardHeader}>
                <h3>Prazo #{index + 1}</h3>
                {fields.length > 1 && (
                  <button
                    type="button"
                    onClick={() => remove(index)}
                    className={styles.removeButton}
                  >
                    <FiTrash2 /> Remover
                  </button>
                )}
              </div>

              <div className={styles.cardBody}>
                {/* Descrição */}
                <div className={styles.formGroup}>
                  <label>Descrição da Tarefa *</label>
                  <input
                    {...register(`deadlines.${index}.task_description`)}
                    placeholder="Ex: Apresentar contestação"
                  />
                  {errors.deadlines?.[index]?.task_description && (
                    <span className={styles.errorText}>
                      {errors.deadlines[index]?.task_description?.message}
                    </span>
                  )}
                </div>

                {/* Data de Vencimento */}
                <div className={styles.formGroup}>
                  <label>Data de Vencimento *</label>
                  <input
                    type="datetime-local"
                    {...register(`deadlines.${index}.due_date`)}
                  />
                  {errors.deadlines?.[index]?.due_date && (
                    <span className={styles.errorText}>
                      {errors.deadlines[index]?.due_date?.message}
                    </span>
                  )}
                </div>

                {/* Número do Processo */}
                <div className={styles.formGroup}>
                  <label>Número do Processo</label>
                  <input
                    {...register(`deadlines.${index}.process_number`)}
                    placeholder="Ex: 1234567-89.2024.8.01.0001"
                  />
                </div>

                {/* Tipo */}
                <div className={styles.formGroup}>
                  <label>Tipo</label>
                  <input
                    {...register(`deadlines.${index}.type`)}
                    placeholder="Ex: Recursal, Processual, Audiência"
                  />
                </div>

                {/* Partes */}
                <div className={styles.formGroup}>
                  <label>Partes</label>
                  <input
                    {...register(`deadlines.${index}.parties`)}
                    placeholder="Ex: João Silva vs. Maria José"
                  />
                </div>

                {/* Status */}
                <div className={styles.formGroup}>
                  <label>Status</label>
                  <select {...register(`deadlines.${index}.status`)}>
                    <option value={DeadlineStatus.PENDENTE}>Pendente</option>
                    <option value={DeadlineStatus.CONCLUIDO}>Concluído</option>
                    <option value={DeadlineStatus.CANCELADO}>Cancelado</option>
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Botão adicionar mais */}
        <button
          type="button"
          onClick={() =>
            append({
              task_description: '',
              due_date: '',
              process_number: '',
              type: '',
              parties: '',
              status: DeadlineStatus.PENDENTE,
            })
          }
          className={styles.addButton}
        >
          <FiPlus /> Adicionar Mais um Prazo
        </button>

        {/* Opções */}
        <div className={styles.options}>
          <label className={styles.checkbox}>
            <input type="checkbox" {...register('skip_notifications')} />
            <span>Não enviar notificações (recomendado para grandes volumes)</span>
          </label>
          <label className={styles.checkbox}>
            <input type="checkbox" {...register('skip_celery')} />
            <span>Não classificar automaticamente (mais rápido)</span>
          </label>
        </div>

        {/* Botão de envio */}
        <button
          type="submit"
          disabled={isLoading}
          className={styles.submitButton}
        >
          {isLoading ? (
            <>Importando...</>
          ) : (
            <>
              <FiUpload /> Importar {fields.length} Prazo(s)
            </>
          )}
        </button>
      </form>
    </div>
  );
}
```

---

## 📁 Passo 4: Componente com Upload de Arquivo

Crie o arquivo `src/components/BulkImport/BulkImportFile.tsx`:

```typescript
// src/components/BulkImport/BulkImportFile.tsx

import { useState, useRef } from 'react';
import { deadlineService } from '../../services/deadlineService';
import { FiUpload, FiFile, FiX, FiDownload } from 'react-icons/fi';
import styles from './BulkImport.module.css';

export default function BulkImportFile() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validar extensão
      const validExtensions = ['.xlsx', '.xls', '.csv'];
      const fileExtension = selectedFile.name
        .substring(selectedFile.name.lastIndexOf('.'))
        .toLowerCase();

      if (!validExtensions.includes(fileExtension)) {
        alert('Arquivo inválido. Use apenas .xlsx, .xls ou .csv');
        return;
      }

      setFile(selectedFile);
      setResult(null);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      alert('Selecione um arquivo primeiro');
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const response = await deadlineService.importFromSpreadsheet(file);
      setResult(response);
      
      if (response.error_count === 0) {
        alert('Importação concluída com sucesso!');
        handleRemoveFile();
      }
    } catch (error: any) {
      console.error('Erro ao importar:', error);
      alert(
        error.response?.data?.detail || 'Erro ao importar arquivo. Tente novamente.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const downloadExample = () => {
    // Link para baixar o arquivo de exemplo
    window.open('/planilha_exemplo_importacao.csv', '_blank');
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>Importação de Planilha (Excel/CSV)</h2>
        <p>Faça upload de um arquivo Excel ou CSV com os prazos</p>
        <button onClick={downloadExample} className={styles.downloadButton}>
          <FiDownload /> Baixar Planilha de Exemplo
        </button>
      </div>

      {/* Resultado */}
      {result && (
        <div className={styles.resultBox}>
          <div className={styles.resultSummary}>
            <div className={styles.statCard}>
              <span className={styles.statLabel}>Total Recebido</span>
              <span className={styles.statValue}>
                {result.imported_count + result.error_count}
              </span>
            </div>
            <div className={`${styles.statCard} ${styles.success}`}>
              <span className={styles.statLabel}>Importados</span>
              <span className={styles.statValue}>{result.imported_count}</span>
            </div>
            <div className={`${styles.statCard} ${styles.error}`}>
              <span className={styles.statLabel}>Erros</span>
              <span className={styles.statValue}>{result.error_count}</span>
            </div>
          </div>

          {result.errors?.length > 0 && (
            <div className={styles.errorsList}>
              <h3>Erros Encontrados:</h3>
              {result.errors.map((error: any, index: number) => (
                <div key={index} className={styles.errorItem}>
                  <strong>Linha {error.line}:</strong> {error.error}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit} className={styles.form}>
        {/* Área de upload */}
        <div className={styles.uploadArea}>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={handleFileChange}
            style={{ display: 'none' }}
            id="file-upload"
          />

          {!file ? (
            <label htmlFor="file-upload" className={styles.uploadLabel}>
              <FiUpload size={48} />
              <span>Clique para selecionar ou arraste um arquivo</span>
              <small>Formatos aceitos: .xlsx, .xls, .csv</small>
            </label>
          ) : (
            <div className={styles.filePreview}>
              <FiFile size={32} />
              <div className={styles.fileInfo}>
                <span className={styles.fileName}>{file.name}</span>
                <span className={styles.fileSize}>
                  {(file.size / 1024).toFixed(2)} KB
                </span>
              </div>
              <button
                type="button"
                onClick={handleRemoveFile}
                className={styles.removeFileButton}
              >
                <FiX />
              </button>
            </div>
          )}
        </div>

        {/* Botão de envio */}
        <button
          type="submit"
          disabled={!file || isLoading}
          className={styles.submitButton}
        >
          {isLoading ? 'Importando...' : 'Importar Planilha'}
        </button>
      </form>

      {/* Instruções */}
      <div className={styles.instructions}>
        <h3>Instruções:</h3>
        <ol>
          <li>Baixe a planilha de exemplo clicando no botão acima</li>
          <li>Preencha a planilha com os dados dos prazos</li>
          <li>Salve o arquivo e faça o upload aqui</li>
          <li>Aguarde o processamento e verifique o relatório</li>
        </ol>

        <h3>Colunas Obrigatórias:</h3>
        <ul>
          <li><code>descricao</code> - Descrição do prazo (mínimo 5 caracteres)</li>
          <li><code>data_vencimento</code> - Data no formato YYYY-MM-DD ou DD/MM/YYYY</li>
        </ul>

        <h3>Colunas Opcionais:</h3>
        <ul>
          <li><code>numero_processo</code> - Número do processo</li>
          <li><code>tipo</code> - Tipo do prazo (ex: Recursal, Processual)</li>
          <li><code>partes</code> - Partes envolvidas</li>
          <li><code>classificacao</code> - normal, critico ou fatal</li>
        </ul>
      </div>
    </div>
  );
}
```

---

## 🎨 Passo 5: Estilização

Crie o arquivo `src/components/BulkImport/BulkImport.module.css`:

```css
/* src/components/BulkImport/BulkImport.module.css */

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.header {
  margin-bottom: 32px;
}

.header h2 {
  color: #2d3748;
  font-size: 28px;
  margin: 0 0 8px 0;
}

.header p {
  color: #718096;
  font-size: 16px;
  margin: 0;
}

.downloadButton {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 10px 20px;
  background-color: #e2e8f0;
  color: #2d3748;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.downloadButton:hover {
  background-color: #cbd5e0;
}

/* Resultado da importação */
.resultBox {
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
}

.resultSummary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.statCard {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.statCard.success {
  border-color: #48bb78;
  color: #38a169;
}

.statCard.error {
  border-color: #f56565;
  color: #e53e3e;
}

.statCard svg {
  font-size: 24px;
}

.statLabel {
  font-size: 14px;
  color: #718096;
  font-weight: 500;
}

.statValue {
  font-size: 32px;
  font-weight: 700;
}

/* Listas de erros e sucessos */
.errorsList,
.successList {
  margin-top: 16px;
}

.errorsList h3,
.successList h3 {
  font-size: 16px;
  color: #2d3748;
  margin: 0 0 12px 0;
}

.errorItem {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: #fff5f5;
  border-left: 4px solid #f56565;
  border-radius: 4px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #742a2a;
}

.errorItem svg {
  flex-shrink: 0;
  margin-top: 2px;
  color: #f56565;
}

.successList ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.successList li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: white;
  border-left: 4px solid #48bb78;
  border-radius: 4px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #2d3748;
}

.successList li svg {
  color: #48bb78;
}

/* Formulário */
.form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Lista de deadlines */
.deadlinesList {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.deadlineCard {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.cardHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f7fafc;
  border-bottom: 2px solid #e2e8f0;
}

.cardHeader h3 {
  margin: 0;
  font-size: 18px;
  color: #2d3748;
}

.removeButton {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #fff5f5;
  color: #e53e3e;
  border: 1px solid #feb2b2;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.removeButton:hover {
  background: #fed7d7;
}

.cardBody {
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.formGroup {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.formGroup label {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
}

.formGroup input,
.formGroup select {
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
}

.formGroup input:focus,
.formGroup select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.errorText {
  color: #e53e3e;
  font-size: 12px;
  font-weight: 500;
}

/* Botões */
.addButton {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  background: white;
  color: #667eea;
  border: 2px dashed #667eea;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.addButton:hover {
  background: #f7fafc;
}

.submitButton {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.submitButton:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.submitButton:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Opções */
.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  background: #f7fafc;
  border-radius: 8px;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #4a5568;
  cursor: pointer;
}

.checkbox input[type='checkbox'] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* Upload de arquivo */
.uploadArea {
  border: 3px dashed #cbd5e0;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  background: #f7fafc;
  transition: all 0.2s;
}

.uploadArea:hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.uploadLabel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  color: #4a5568;
}

.uploadLabel svg {
  color: #667eea;
}

.uploadLabel span {
  font-size: 16px;
  font-weight: 600;
}

.uploadLabel small {
  font-size: 12px;
  color: #718096;
}

.filePreview {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
}

.filePreview svg {
  color: #667eea;
  flex-shrink: 0;
}

.fileInfo {
  flex: 1;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.fileName {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
}

.fileSize {
  font-size: 12px;
  color: #718096;
}

.removeFileButton {
  background: #fed7d7;
  color: #e53e3e;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.removeFileButton:hover {
  background: #fc8181;
  color: white;
}

/* Instruções */
.instructions {
  padding: 24px;
  background: #f7fafc;
  border-radius: 8px;
  margin-top: 32px;
}

.instructions h3 {
  font-size: 16px;
  color: #2d3748;
  margin: 0 0 12px 0;
}

.instructions ol,
.instructions ul {
  margin: 0 0 24px 0;
  padding-left: 24px;
}

.instructions li {
  margin-bottom: 8px;
  color: #4a5568;
  font-size: 14px;
}

.instructions code {
  background: #edf2f7;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #e53e3e;
}

/* Responsividade */
@media (max-width: 768px) {
  .container {
    padding: 16px;
  }

  .cardBody {
    grid-template-columns: 1fr;
  }

  .resultSummary {
    grid-template-columns: 1fr;
  }
}
```

---

## 🔗 Passo 6: Integração Completa

Crie um componente tab para alternar entre os métodos:

```typescript
// src/components/BulkImport/BulkImportTabs.tsx

import { useState } from 'react';
import BulkImportJSON from './BulkImportJSON';
import BulkImportFile from './BulkImportFile';
import { FiCode, FiFileText } from 'react-icons/fi';
import styles from './BulkImport.module.css';

export default function BulkImportTabs() {
  const [activeTab, setActiveTab] = useState<'json' | 'file'>('json');

  return (
    <div className={styles.tabsContainer}>
      <div className={styles.tabButtons}>
        <button
          className={activeTab === 'json' ? styles.tabActive : styles.tab}
          onClick={() => setActiveTab('json')}
        >
          <FiCode /> Formulário (JSON)
        </button>
        <button
          className={activeTab === 'file' ? styles.tabActive : styles.tab}
          onClick={() => setActiveTab('file')}
        >
          <FiFileText /> Upload de Planilha
        </button>
      </div>

      <div className={styles.tabContent}>
        {activeTab === 'json' ? <BulkImportJSON /> : <BulkImportFile />}
      </div>
    </div>
  );
}
```

Adicione estes estilos ao CSS:

```css
/* Adicionar ao BulkImport.module.css */

.tabsContainer {
  width: 100%;
}

.tabButtons {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid #e2e8f0;
}

.tab,
.tabActive {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  color: #718096;
  transition: all 0.2s;
  margin-bottom: -2px;
}

.tab:hover {
  color: #667eea;
}

.tabActive {
  color: #667eea;
  border-bottom-color: #667eea;
}
```

---

## 📝 Exemplos de Uso

### Exemplo 1: Importação Simples

```typescript
import { deadlineService } from './services/deadlineService';
import { DeadlineStatus } from './types/deadline.types';

async function importarPrazos() {
  const deadlines = [
    {
      task_description: 'Apresentar contestação no processo 123',
      due_date: '2024-12-31T23:59:59',
      process_number: '1234567-89.2024.8.01.0001',
      type: 'Recursal',
      parties: 'João vs. Maria',
      status: DeadlineStatus.PENDENTE,
    },
    {
      task_description: 'Protocolar recurso no processo 456',
      due_date: '2024-11-15T17:00:00',
      process_number: '9876543-21.2024.8.01.0002',
      type: 'Recursal',
      parties: 'Pedro vs. Ana',
      status: DeadlineStatus.PENDENTE,
    },
  ];

  try {
    const resultado = await deadlineService.createDeadlinesBulk({
      deadlines,
      skip_notifications: true,
      skip_celery: true,
    });

    console.log('Importados:', resultado.imported_count);
    console.log('Erros:', resultado.error_count);
    console.log('Detalhes:', resultado);
  } catch (error) {
    console.error('Erro na importação:', error);
  }
}
```

### Exemplo 2: Converter CSV para JSON

```typescript
import Papa from 'papaparse';

function converterCSVParaJSON(file: File): Promise<any[]> {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      complete: (results) => {
        const deadlines = results.data.map((row: any) => ({
          task_description: row.descricao,
          due_date: new Date(row.data_vencimento).toISOString(),
          process_number: row.numero_processo || undefined,
          type: row.tipo || undefined,
          parties: row.partes || undefined,
          status: 'pendente',
        }));
        resolve(deadlines);
      },
      error: (error) => reject(error),
    });
  });
}

// Uso
const file = inputElement.files[0];
const deadlines = await converterCSVParaJSON(file);
const resultado = await deadlineService.createDeadlinesBulk({
  deadlines,
  skip_notifications: true,
});
```

### Exemplo 3: Importação com Progresso

```typescript
import { useState } from 'react';

function useProgressiveImport() {
  const [progress, setProgress] = useState(0);
  const [isImporting, setIsImporting] = useState(false);

  const importInBatches = async (allDeadlines: any[], batchSize = 100) => {
    setIsImporting(true);
    setProgress(0);

    const results = {
      imported: 0,
      errors: 0,
      details: [] as any[],
    };

    const batches = [];
    for (let i = 0; i < allDeadlines.length; i += batchSize) {
      batches.push(allDeadlines.slice(i, i + batchSize));
    }

    for (let i = 0; i < batches.length; i++) {
      try {
        const result = await deadlineService.createDeadlinesBulk({
          deadlines: batches[i],
          skip_notifications: true,
          skip_celery: true,
        });

        results.imported += result.imported_count;
        results.errors += result.error_count;
        results.details.push(result);

        setProgress(((i + 1) / batches.length) * 100);
      } catch (error) {
        console.error(`Erro no lote ${i + 1}:`, error);
        results.errors += batches[i].length;
      }
    }

    setIsImporting(false);
    return results;
  };

  return { importInBatches, progress, isImporting };
}
```

---

## 🐛 Troubleshooting

### Erro 403: Forbidden

**Causa:** Usuário não tem permissão ADMIN

**Solução:**
```typescript
// Verificar perfil antes de tentar importar
if (currentUser.profile !== 'admin') {
  alert('Apenas administradores podem importar prazos em massa');
  return;
}
```

### Erro 422: Validation Error

**Causa:** Dados inválidos no request

**Solução:**
```typescript
// Validar dados antes de enviar
const isValid = deadlines.every((d) => {
  return (
    d.task_description &&
    d.task_description.length >= 5 &&
    d.due_date &&
    new Date(d.due_date) > new Date()
  );
});

if (!isValid) {
  alert('Verifique os dados: descrição mínima 5 chars e data futura');
  return;
}
```

### Timeout em Grandes Volumes

**Solução:** Dividir em lotes menores

```typescript
const BATCH_SIZE = 100;

for (let i = 0; i < deadlines.length; i += BATCH_SIZE) {
  const batch = deadlines.slice(i, i + BATCH_SIZE);
  await deadlineService.createDeadlinesBulk({
    deadlines: batch,
    skip_notifications: true,
    skip_celery: true,
  });
  
  // Pequeno delay entre lotes
  await new Promise(resolve => setTimeout(resolve, 500));
}
```

---

## 📚 Recursos Adicionais

- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
- [React Hook Form Arrays](https://react-hook-form.com/api/usefieldarray)
- [PapaParse CSV Parser](https://www.papaparse.com/)
- [Zod Validation](https://zod.dev/)

---

## ✅ Checklist de Implementação

- [ ] Tipos TypeScript criados
- [ ] Serviço de API implementado
- [ ] Componente JSON funcional
- [ ] Componente de upload funcional
- [ ] Validações implementadas
- [ ] Tratamento de erros robusto
- [ ] Feedback visual completo
- [ ] Testes manuais realizados
- [ ] Documentação criada

---

**Pronto!** Agora você tem dois métodos completos de importação em massa:
1. **JSON** - Formulário dinâmico ou dados programáticos
2. **Arquivo** - Upload de Excel/CSV pelo usuário

Ambos integrados ao seu backend Bacelar Legal Intelligence! 🚀
