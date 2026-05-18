# Automação de Instagram Direct — Loja do Avô

Sistema de envio humanizado de DMs para os 66 mil seguidores.

---

## Arquivos do sistema

| Arquivo | Função |
|---|---|
| `instagram_dm.py` | Motor principal — disparo e modo respostas |
| `mensagens_instagram.py` | Banco de mensagens: 20 variações + respostas contextuais |
| `exportar_seguidores.py` | Exporta lista de seguidores para `seguidores.json` |
| `.env` | Credenciais e configurações (criado a partir do `.env.example`) |

---

## Instalação

```bash
pip install instagrapi
```

---

## Configuração

```bash
cp .env.example .env
```

Edite o `.env` e preencha:

```
INSTAGRAM_USER=lojadoavo
INSTAGRAM_PASS=sua_senha_aqui
```

---

## Passo a passo recomendado para 66 mil seguidores

### Etapa 1 — Exportar a lista de seguidores (uma vez só)

```bash
python exportar_seguidores.py
```

Gera o arquivo `seguidores.json`. Pode demorar 30–90 minutos para 66k.
Só precisa fazer isso uma vez — o arquivo é reutilizado em todas as sessões.

---

### Etapa 2 — Rodar o disparo

```bash
python instagram_dm.py
```

O sistema:
- Carrega seguidores do `seguidores.json`
- Filtra quem já recebeu mensagem (via `log_instagram.txt`)
- Envia em lotes com intervalos aleatórios
- Pausa automaticamente a cada 10 mensagens
- Salva progresso — pode interromper e retomar a qualquer hora

---

### Etapa 3 — Ativar respostas automáticas (opcional)

Em outro terminal, enquanto o disparo roda:

```bash
MODO=respostas python instagram_dm.py
```

Ou edite no `.env`:
```
MODO=respostas
```

O sistema detecta a intenção da resposta e responde de forma humanizada:

| Intenção detectada | Tipo de resposta |
|---|---|
| "obrigado", "valeu" | Acolhimento e abertura de conversa |
| "produto", "preço" | Orientação consultiva sobre produtos |
| "entrega", "frete" | Informações sobre envio nacional |
| "cupom", "desconto" | Explicação do PRIMEIRACOMPRA10 |
| "banheiro", "adaptação" | Especialista em adaptação residencial |
| "mobilidade", "queda" | Orientação de mobilidade e segurança |

---

## Limites de segurança recomendados

| Configuração | Valor padrão | Mínimo seguro |
|---|---|---|
| Mensagens por sessão | 40 | 20 |
| Intervalo entre msgs | 60–180s | 45s |
| Pausa longa (a cada 10) | 5–10 min | 3 min |
| Sessões por dia | 1 | 1 |

**Nunca envie mais de 50 DMs por dia.** O Instagram monitora volume de envios para contas não verificadas.

---

## Estratégia de disparo para 66 mil seguidores

Com 40 mensagens/dia → **1.650 dias (~4,5 anos)** para toda a base.

Recomendação prática:

| Fase | Volume diário | Duração |
|---|---|---|
| Semanas 1–2 (aquecimento) | 20 msgs/dia | 2 semanas |
| Mês 2–3 | 40 msgs/dia | 2 meses |
| A partir do mês 4 | 50 msgs/dia | contínuo |

Foque nos seguidores mais recentes primeiro — eles têm mais memória da marca.

---

## Banco de mensagens

O arquivo `mensagens_instagram.py` contém:

- **20 variações** da mensagem principal (cupom PRIMEIRACOMPRA10)
- **10 aberturas** diferentes
- **10 fechamentos** diferentes
- **10 respostas** para "obrigado"
- **10 respostas** para dúvidas de produto
- **10 respostas** para dúvidas de entrega
- **10 respostas** sobre o cupom
- **10 respostas** sobre adaptação residencial
- **10 respostas** sobre mobilidade e segurança

Todas humanizadas, variadas e sem linguagem robótica.

---

## Logs e progresso

O arquivo `log_instagram.txt` registra cada envio:

```
OK|123456789|usuario_fulano|18/05/2026 14:32:11|
ERRO|987654321|usuario_ciclano|18/05/2026 14:33:45|Challenge required
RESPOSTA|123456789|usuario_fulano|18/05/2026 15:00:00|mobilidade
```

O sistema nunca envia duas vezes para o mesmo perfil — pode interromper e retomar sem problema.

---

## Dúvidas frequentes

**Por que usar `seguidores.json` em vez de buscar direto da API?**
Buscar 66k seguidores via API leva 30–90 min e gera muito tráfego. Exportar uma vez e reutilizar é mais seguro.

**O que fazer se aparecer "Challenge required"?**
O Instagram pediu verificação. Acesse o app manualmente, resolva o desafio (e-mail/SMS) e rode novamente.

**Posso rodar em VPS/servidor?**
Sim, mas use sempre o mesmo IP. Mudar de IP entre sessões aumenta o risco de bloqueio.

**O cupom PRIMEIRACOMPRA10 tem validade?**
Verifique no painel da loja. Se precisar trocar o cupom, edite a variável `CUPOM` em `mensagens_instagram.py`.
