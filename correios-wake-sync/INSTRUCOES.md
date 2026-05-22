# correios-wake-sync

Automação que consulta pedidos na Wake Commerce, verifica o rastreamento nos
Correios via API oficial e atualiza automaticamente o status para **Entregue**
quando a entrega é confirmada.

---

## Requisitos

- Node.js 18 ou superior
- Contrato com os Correios habilitado para a API Rastro
  (solicite em correios.com.br → Acesso para Empresas)
- Token de API da Wake Commerce
  (Painel Wake → Configurações → Integrações → API)

---

## Instalação

```bash
cd correios-wake-sync
npm install
cp .env.example .env
# edite o .env com suas credenciais
```

---

## Configuração

Edite o arquivo `.env`. Os campos obrigatórios são:

| Variável                  | Onde obter                                      |
|---------------------------|-------------------------------------------------|
| `WAKE_API_URL`            | Painel Wake → Integrações → API                 |
| `WAKE_ACCESS_TOKEN`       | Painel Wake → Integrações → API                 |
| `CORREIOS_USUARIO`        | Contrato Correios (geralmente o CNPJ)           |
| `CORREIOS_SENHA`          | Senha do contrato Correios                      |
| `CORREIOS_CARTAO_POSTAGEM`| Número do cartão de postagem do contrato        |

### Status da Wake

Confirme no painel da Wake os nomes exatos dos status da sua loja:

- `WAKE_STATUS_VERIFICAR` — pedidos que entrarão na verificação  
  *Padrão:* `Enviado,Em transporte,Objeto postado`
- `WAKE_STATUS_ENTREGUE` — status aplicado quando entregue  
  *Padrão:* `Entregue`

Se a Wake da sua loja usar IDs numéricos em vez de nomes, use:
```
WAKE_STATUS_ID_VERIFICAR=3,4,5
WAKE_STATUS_ID_ENTREGUE=6
```

---

## Uso

### Modo simulação (recomendado primeiro)

Lista o que seria feito **sem alterar nada na Wake**:

```bash
npm run simular
# ou
node index.js --dry-run
```

### Modo produção

Atualiza os pedidos entregues na Wake:

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

## Saída

Ao final de cada execução, dois arquivos são gerados em `logs/`:

- `execucao_YYYY-MM-DD_HH-mm-ss.log` — log completo linha a linha
- `relatorio_YYYY-MM-DD_HH-mm-ss.json` — relatório estruturado (útil para n8n)

Relatório exibido no terminal:

```
══════════════════════════════════════════════
RELATÓRIO FINAL — MODO SIMULAÇÃO
Total de pedidos analisados:  45
Sem código de rastreio:        3
Rastreio não é Correios:       2
Em trânsito (não entregues):  28
Confirmados como entregues:   12
[SIMULAÇÃO] Seriam atualizados: 12
══════════════════════════════════════════════
```

---

## Agendamento

### Cron (Linux/Mac)

Para rodar todo dia às 8h e às 18h:

```bash
crontab -e
```

```cron
0 8,18 * * * cd /caminho/para/correios-wake-sync && node index.js --producao >> /tmp/correios-wake.out 2>&1
```

### n8n

No n8n, use um nó **Execute Command** com:

```bash
cd /caminho/para/correios-wake-sync && node index.js --producao
```

Ou use um nó **Function** que leia o `relatorio_*.json` gerado para
criar dashboards ou enviar notificações.

---

## Regras de segurança aplicadas

- Nunca atualiza pedido sem código de rastreio válido
- Apenas rastreios no formato Correios (`AA123456789BR`) são processados
- Apenas o evento `BDE`/`BDI` (entregue ao destinatário) aciona a atualização
- Pedidos cancelados, devolvidos, em troca ou com contestação são ignorados
- Credenciais nunca aparecem em logs
- Em caso de falha na API dos Correios, o pedido é ignorado nessa execução
- Em caso de falha na Wake, o erro é registrado e os demais pedidos continuam

---

## Ajuste do schema GraphQL da Wake

Caso a Wake retorne erro de campo não encontrado, abra `src/wakeApi.js`
e ajuste os nomes dos campos nas queries `QUERY_PEDIDOS`,
`MUTATION_ATUALIZAR_STATUS` e `MUTATION_ADICIONAR_NOTA` para os nomes
corretos do schema da sua versão da Wake.

Para inspecionar o schema disponível na sua loja:

```bash
# Introspection query (execute com seu token)
curl -s -X POST https://api.wake.tech/graphql \
  -H "access-token: SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { queryType { fields { name } } } }"}' | jq
```
