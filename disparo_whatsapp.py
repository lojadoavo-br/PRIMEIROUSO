"""
Disparo de Pós-Venda — Loja do Avô
Script de envio humanizado via ChatCenter API

INSTRUÇÕES DE CONFIGURAÇÃO:
1. Instale as dependências:  pip install requests python-dotenv
2. Crie um arquivo .env na mesma pasta com as variáveis abaixo
3. Execute:  python disparo_whatsapp.py

COMO ENCONTRAR OS DADOS DA API NO CHATCENTER:
- Acesse app.chatcenter.com.br → Configurações → Integrações → API
- Copie a API Key e a URL base
- Cole no arquivo .env

VARIÁVEIS DO .env:
    CHATCENTER_API_URL=https://api-br.chatcenter.com.br       (URL base)
    CHATCENTER_API_KEY=68d54d4299d4485110508993               (sua key)
    CHATCENTER_CHANNEL_ID=                                     (ID do canal/instância, se exigido)
    INTERVALO_SEGUNDOS=8                                       (pausa entre mensagens)
    DRY_RUN=false                                              (true = simula sem enviar)
"""

import json
import time
import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIGURAÇÃO ─────────────────────────────────────────────────────────────

API_URL        = os.getenv("CHATCENTER_API_URL", "https://api-br.chatcenter.com.br")
API_KEY        = os.getenv("CHATCENTER_API_KEY", "")
CHANNEL_ID     = os.getenv("CHATCENTER_CHANNEL_ID", "")
INTERVALO      = int(os.getenv("INTERVALO_SEGUNDOS", "8"))
DRY_RUN        = os.getenv("DRY_RUN", "false").lower() == "true"

LEADS_FILE     = "leads_disparo.json"
LOG_ENVIADOS   = "enviados.log"
LOG_ERROS      = "erros.log"
PROGRESSO_FILE = "progresso.json"

# ─── LOGGING ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("disparo.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─── FUNÇÕES AUXILIARES ────────────────────────────────────────────────────────

def carregar_progresso():
    if os.path.exists(PROGRESSO_FILE):
    	with open(PROGRESSO_FILE, "r") as f:
            return set(json.load(f))
    return set()

def salvar_progresso(enviados):
    with open(PROGRESSO_FILE, "w") as f:
        json.dump(list(enviados), f)

def normalizar_telefone(tel_raw: str) -> str:
    """Pega o primeiro número da lista (caso haja dois), remove não-dígitos, garante DDI 55."""
    tel = tel_raw.split("|")[0].strip()
    digits = "".join(filter(str.isdigit, tel))
    if not digits.startswith("55"):
        digits = "55" + digits
    return digits

def registrar_log(arquivo: str, linha: str):
    with open(arquivo, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {linha}\n")

# ─── ENVIO DE MENSAGEM ─────────────────────────────────────────────────────────

def enviar_mensagem(telefone: str, mensagem: str) -> bool:
    """
    Envia mensagem via ChatCenter API.

    Se o endpoint ou o body precisar de ajuste, altere aqui.
    Estruturas mais comuns:

        POST {API_URL}/messages
        Headers: Authorization: Bearer {API_KEY}
        Body: { "phone": "5511999999999", "message": "texto" }

        POST {API_URL}/api/v1/sendMessage
        Headers: apikey: {API_KEY}
        Body: { "number": "5511999999999@c.us", "text": "texto" }
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    if CHANNEL_ID:
        headers["X-Channel-Id"] = CHANNEL_ID

    payload = {
        "phone": telefone,
        "message": mensagem,
    }

    try:
        resp = requests.post(
            f"{API_URL}/messages",
            headers=headers,
            json=payload,
            timeout=30,
        )
        if resp.status_code in (200, 201, 202):
            return True
        else:
            log.warning(f"HTTP {resp.status_code} para {telefone}: {resp.text[:200]}")
            return False
    except requests.exceptions.RequestException as e:
        log.error(f"Erro de conexão para {telefone}: {e}")
        return False

# ─── LOOP PRINCIPAL ────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        log.error("API_KEY não configurada. Verifique o arquivo .env")
        return

    if not os.path.exists(LEADS_FILE):
        log.error(f"Arquivo de leads não encontrado: {LEADS_FILE}")
        return

    with open(LEADS_FILE, "r", encoding="utf-8") as f:
        leads = json.load(f)

    ja_enviados = carregar_progresso()

    total       = len(leads)
    enviados    = 0
    falhas      = 0
    pulados     = 0

    log.info(f"{'[DRY RUN] ' if DRY_RUN else ''}Iniciando disparo — {total} leads carregados")
    log.info(f"Já enviados anteriormente: {len(ja_enviados)}")
    log.info(f"Intervalo entre mensagens: {INTERVALO}s")
    log.info("─" * 60)

    for i, lead in enumerate(leads, 1):
        telefone_raw = lead.get("telefone_raw", "")
        nome         = lead.get("nome", "Cliente")
        mensagem     = lead.get("mensagem", "")
        categoria    = lead.get("categoria", "")

        telefone = normalizar_telefone(telefone_raw)

        # Pular inválidos
        if len(telefone) < 12:
            log.warning(f"[{i}/{total}] Telefone inválido ignorado: {telefone_raw} ({nome})")
            pulados += 1
            continue

        # Pular já enviados (permite retomar de onde parou)
        if telefone in ja_enviados:
            log.info(f"[{i}/{total}] JÁ ENVIADO — pulando {nome}")
            pulados += 1
            continue

        log.info(f"[{i}/{total}] {nome} | {telefone} | {categoria}")

        if DRY_RUN:
            log.info(f"  [DRY RUN] Mensagem que seria enviada:\n{mensagem[:80]}...")
            enviados += 1
            ja_enviados.add(telefone)
        else:
            sucesso = enviar_mensagem(telefone, mensagem)

            if sucesso:
                enviados += 1
                ja_enviados.add(telefone)
                registrar_log(LOG_ENVIADOS, f"{nome} | {telefone} | {categoria}")
                log.info(f"  ✓ Enviado com sucesso")
            else:
                falhas += 1
                registrar_log(LOG_ERROS, f"{nome} | {telefone} | {categoria}")
                log.warning(f"  ✗ Falha no envio")

        salvar_progresso(ja_enviados)

        # Pausa entre disparos — essencial para não ser bloqueado pelo WhatsApp
        if i < total:
            time.sleep(INTERVALO)

    log.info("─" * 60)
    log.info(f"DISPARO CONCLUÍDO")
    log.info(f"  Enviados:  {enviados}")
    log.info(f"  Falhas:    {falhas}")
    log.info(f"  Pulados:   {pulados}")
    log.info(f"  Total:     {total}")

if __name__ == "__main__":
    main()
