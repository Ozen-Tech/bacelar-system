# Configuração do Firebase no Render

## Problema
O serviço `bacelar-api-worker` no Render está falhando com o erro:
```
❌ ATENÇÃO: Erro ao inicializar o Firebase Admin SDK: [Errno 2] No such file or directory: '/code/firebase-credentials.json'
```

## Solução
O código foi atualizado para suportar credenciais do Firebase via variável de ambiente, que é a forma recomendada para deploy em produção.

## Passos para Configurar no Render

### 1. Obter as Credenciais do Firebase
1. Acesse o [Console do Firebase](https://console.firebase.google.com/)
2. Selecione seu projeto
3. Vá em **Configurações do Projeto** (ícone de engrenagem)
4. Aba **Contas de Serviço**
5. Clique em **Gerar nova chave privada**
6. Baixe o arquivo JSON

### 2. Converter para String JSON
O conteúdo do arquivo baixado deve ser convertido para uma string JSON em uma única linha.

**Exemplo do arquivo:**
```json
{
  "type": "service_account",
  "project_id": "seu-projeto",
  "private_key_id": "abc123",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxx@seu-projeto.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxx%40seu-projeto.iam.gserviceaccount.com"
}
```

**Deve ser convertido para:**
```json
{"type":"service_account","project_id":"seu-projeto","private_key_id":"abc123","private_key":"-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n","client_email":"firebase-adminsdk-xxx@seu-projeto.iam.gserviceaccount.com","client_id":"123456789","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxx%40seu-projeto.iam.gserviceaccount.com"}
```

### 3. Configurar no Render
1. Acesse o [Dashboard do Render](https://dashboard.render.com/)
2. Vá em **Environment Groups**
3. Encontre o grupo `bacelar-env`
4. Adicione uma nova variável:
   - **Key:** `FIREBASE_CREDENTIALS_JSON`
   - **Value:** Cole a string JSON convertida (uma única linha)

### 4. Redesploy dos Serviços
Após adicionar a variável de ambiente, faça o redeploy dos seguintes serviços:
- `bacelar-api`
- `bacelar-celery-worker`
- `bacelar-celery-beat`

## Verificação
Após o redeploy, você deve ver nos logs:
```
✅ Firebase Admin SDK inicializado com credenciais JSON da variável de ambiente.
```

## Notas Importantes
- **Nunca** commite o arquivo `firebase-credentials.json` no repositório
- A variável `FIREBASE_CREDENTIALS_JSON` deve conter o JSON completo em uma única linha
- Certifique-se de que as quebras de linha no `private_key` estejam escapadas como `\\n`
- O código funciona tanto em desenvolvimento (com arquivo) quanto em produção (com variável de ambiente)

## Troubleshooting
Se ainda houver problemas:
1. Verifique se a variável `FIREBASE_CREDENTIALS_JSON` está definida no grupo `bacelar-env`
2. Confirme que o JSON está válido (sem quebras de linha desnecessárias)
3. Verifique os logs dos serviços após o redeploy
4. Certifique-se de que o projeto Firebase está ativo e as permissões estão corretas