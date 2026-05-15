# Como rodar o disparo de pós-venda — Loja do Avô

## O que você precisa

- Python 3.8+
- Sua máquina (ou servidor) com IP liberado no ChatCenter

---

## Passo a passo

### 1. Copie os 3 arquivos para sua máquina
- `disparo_whatsapp.py`
- `leads_disparo.json`
- `.env.example`

### 2. Configure o .env
Renomeie `.env.example` para `.env` e preencha:

```
CHATCENTER_API_URL=https://api-br.chatcenter.com.br
CHATCENTER_API_KEY=SUA_API_KEY_AQUI
CHATCENTER_CHANNEL_ID=ID_DO_CANAL_SE_NECESSÁRIO
INTERVALO_SEGUNDOS=8
DRY_RUN=true
```

> **Onde encontrar no ChatCenter:**
> `app.chatcenter.com.br → Configurações → Integrações → API`

### 3. Instale as dependências
```bash
pip install requests python-dotenv
```

### 4. Teste primeiro (DRY RUN)
Com `DRY_RUN=true` no .env, rode:
```bash
python disparo_whatsapp.py
```
Vai simular o envio sem disparar nada. Verifique se os logs ficaram certos.

### 5. Disparo real
Altere no .env:
```
DRY_RUN=false
```
Execute novamente:
```bash
python disparo_whatsapp.py
```

---

## Recursos do script

| Recurso | Descrição |
|---------|-----------|
| **Retomada automática** | Se o script parar, retoma de onde parou (salvo em `progresso.json`) |
| **Rate limiting** | Pausa configurável entre mensagens (padrão: 8s) |
| **Logs completos** | `disparo.log`, `enviados.log`, `erros.log` |
| **DRY RUN** | Simula sem enviar |
| **Telefone normalizado** | Trata múltiplos telefones e formatos diferentes |

---

## Ajuste do endpoint (se necessário)

Se o ChatCenter usar um endpoint diferente, edite a função `enviar_mensagem` em `disparo_whatsapp.py`.

Formatos mais comuns:

```python
# Formato A (mais comum)
resp = requests.post(f"{API_URL}/messages", headers=headers, json={"phone": telefone, "message": mensagem})

# Formato B
resp = requests.post(f"{API_URL}/api/v1/sendMessage", headers=headers, json={"number": f"{telefone}@c.us", "text": mensagem})

# Formato C (apikey no header em vez de Authorization)
headers["apikey"] = API_KEY
resp = requests.post(f"{API_URL}/message/sendText/{CHANNEL_ID}", headers=headers, json={"number": telefone, "text": mensagem})
```

---

## Total de leads
- **493 clientes** — do mais antigo (16/12/2025) ao mais recente
- Tempo estimado de disparo com 8s de intervalo: ~66 minutos
