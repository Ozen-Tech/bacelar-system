# Correção do Problema do Celery Worker no Render

## Problema Identificado
O log do Render mostra que o comando executado é:
```
==> Running 'celery -A app.worker.celery_app worker -l info --beat'
```

Este comando está **incorreto** por dois motivos:
1. Usa `app.worker.celery_app` em vez de `app.worker`
2. Inclui a flag `--beat` no worker, que deveria ser um serviço separado

## Solução

### 1. Verificar a Configuração no Dashboard do Render

Acesse o Dashboard do Render e verifique os seguintes serviços:

#### bacelar-celery-worker
- **Comando deve ser:** `celery -A app.worker worker --loglevel=info`
- **NÃO deve ter** a flag `--beat`

#### bacelar-celery-beat (serviço separado)
- **Comando deve ser:** `celery -A app.worker beat --loglevel=info`

### 2. Comandos Corretos

**Worker (para processar tarefas):**
```bash
celery -A app.worker worker --loglevel=info
```

**Beat (para agendar tarefas):**
```bash
celery -A app.worker beat --loglevel=info
```

### 3. Estrutura Correta no render.yaml

O arquivo `render.yaml` já foi corrigido com os comandos corretos:

```yaml
# WORKER DO CELERY
- type: worker
  name: bacelar-celery-worker
  env: docker
  autoDeploy: true
  rootDir: .
  dockerCommand: "celery -A app.worker worker --loglevel=info"

# BEAT DO CELERY (para tarefas agendadas)
- type: worker
  name: bacelar-celery-beat
  env: docker
  autoDeploy: true
  rootDir: .
  dockerCommand: "celery -A app.worker beat --loglevel=info"
```

### 4. Passos para Corrigir

1. **Acesse o Dashboard do Render**
2. **Vá para o serviço `bacelar-celery-worker`**
3. **Verifique se o comando está correto:**
   - Se estiver usando `app.worker.celery_app`, mude para `app.worker`
   - Se tiver `--beat`, remova essa flag
4. **Faça o redeploy do serviço**
5. **Repita para o serviço `bacelar-celery-beat`**

### 5. Verificação

Após a correção, os logs devem mostrar:

**Para o Worker:**
```
==> Running 'celery -A app.worker worker --loglevel=info'
✅ Firebase Admin SDK inicializado com credenciais JSON da variável de ambiente.
[tasks]
  . app.tasks.classify_deadline
  . app.tasks.reclassify_all_deadlines_task
```

**Para o Beat:**
```
==> Running 'celery -A app.worker beat --loglevel=info'
✅ Firebase Admin SDK inicializado com credenciais JSON da variável de ambiente.
```

## Resumo das Correções Necessárias

1. ✅ **Código atualizado** para suportar Firebase via variável de ambiente
2. ✅ **render.yaml corrigido** com comandos corretos do Celery
3. 🔄 **Configurar FIREBASE_CREDENTIALS_JSON** no Dashboard do Render
4. 🔄 **Verificar comandos dos serviços** no Dashboard do Render
5. 🔄 **Redeploy dos serviços** após as correções

## Notas Importantes

- O Worker e Beat devem ser **serviços separados**
- Nunca use `--beat` no comando do worker
- Use `app.worker` e não `app.worker.celery_app`
- Configure a variável `FIREBASE_CREDENTIALS_JSON` conforme o arquivo `RENDER_FIREBASE_SETUP.md`