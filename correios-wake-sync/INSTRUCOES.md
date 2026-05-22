# correios-wake-sync

Automação que lê pedidos do **Bling** (onde as etiquetas são geradas),
verifica o rastreamento nos **Correios** via API oficial e atualiza o
status para **Entregue** no **Bling** e na **Wake Commerce**.

---

## Como funciona

```
Bling (fonte)
    └─ pedidos com rastreio dos Correios
           └─ API Rastro (Correios)
                  └─ evento "Objeto entregue ao destinatário"
                         ├─ Atualiza status → Bling
                         └─ Atualiza status → Wake (por nº de pedido)
```

O rastreio fica no Bling. A Wake é atualizada buscando o pedido pelo
número, sem precisar ter o rastreio salvo lá.

---

## Requisitos

- Node.js 18+
- App Bling criado em developer.bling.com.br com permissão de leitura/escrita em pedidos
- Token da Wake Commerce (Painel Wake → Configurações → Integrações → API)
- Contrato Correios com API Rastro habilitada

---

## Instalação

```bash
cd correios-wake-sync
npm install
cp .env.example .env
```

---

## Configuração do .env

### 1. Bling — obter as credenciais OAuth2

1. Acesse **developer.bling.com.br** e crie um novo app
2. Anote o **Client ID** e o **Client Secret**
3. Faça a autorização inicial (fluxo OAuth2 com o botão "Autorizar"):
   - A URL de autorização é:
     ```
     https://api.bling.com.br/Api/v3/oauth/authorize?response_type=code&client_id=SEU_CLIENT_ID&state=state123
     ```
   - Após autorizar, você recebe um `code` na URL de retorno
4. Troque o `code` pelo `refresh_token`:
   ```bash
   curl -s -X POST https://api.bling.com.br/Api/v3/oauth/token \
     -H "Authorization: Basic $(echo -n 'CLIENT_ID:CLIENT_SECRET' | base64)" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code&code=SEU_CODE"
   ```
5. Salve o `refresh_token` retornado no `.env`

### 2. Bling — IDs de situação

Verifique os IDs de situação da sua loja:
- Bling → Configurações → Situações de Pedido
- Preencha `BLING_SITUACOES_VERIFICAR` com os IDs que significam "em rota"
- Preencha `BLING_SITUACAO_ENTREGUE_ID` com o ID da situação "Entregue"

### 3. Correios

Solicite acesso à API Rastro em **correios.com.br → Acesso para Empresas**.
Você receberá usuário, senha e número do cartão de postagem.

### 4. Wake

O token está em **Painel Wake → Configurações → Integrações → API**.

---

## Uso

### Modo simulação (comece sempre aqui)

```bash
npm run simular
# ou
node index.js --dry-run
```

Lista os pedidos que **seriam** atualizados. Nada é alterado.

### Modo produção

```bash
npm run producao
# ou
node index.js --producao
```

### Ajuda

```bash
node index.js --help
```

---

## Saída e logs

Dois arquivos são gerados em `logs/` a cada execução:

- `execucao_YYYY-MM-DD_HH-mm-ss.log` — log linha a linha
- `relatorio_YYYY-MM-DD_HH-mm-ss.json` — resultado estruturado (útil para n8n)

Exemplo de relatório no terminal:

```
════════════════════════════════════════════════════════════
RELATÓRIO FINAL — MODO PRODUÇÃO
Total de pedidos analisados:        48
Sem código de rastreio:              3
Em trânsito (não entregues):        30
Confirmados como entregues:         15
Atualizados no Bling:               15
Atualizados na Wake:                15
════════════════════════════════════════════════════════════
```

---

## Agendamento (cron)

Para rodar duas vezes por dia (8h e 18h):

```bash
crontab -e
```

```cron
0 8,18 * * * cd /caminho/para/correios-wake-sync && node index.js --producao >> /tmp/correios-wake.out 2>&1
```

---

## Uso com n8n

No n8n, crie um nó **Schedule Trigger** e conecte a um nó **Execute Command**:

```bash
cd /caminho/para/correios-wake-sync && node index.js --producao
```

Para processar o resultado, leia o último arquivo `relatorio_*.json` com
um nó **Read/Write File** e use os dados para criar notificações ou dashboards.

---

## Regras de segurança

| Regra | Comportamento |
|---|---|
| Sem rastreio | Ignora |
| Rastreio não é formato Correios | Ignora |
| Transportadora não é Correios | Ignora |
| Pedido cancelado / devolvido / em troca | Ignora |
| Correios retorna "em trânsito" | Nenhuma ação |
| Correios retorna erro | Ignora nessa execução |
| Wake retorna erro | Registra no log, continua os demais |
| Credenciais | Nunca aparecem em logs |
