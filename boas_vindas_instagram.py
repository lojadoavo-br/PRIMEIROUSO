"""
BOAS-VINDAS A NOVOS SEGUIDORES — LOJA DO AVÔ
Envia DM automática via Instagram Graph API para novos seguidores.

REQUISITOS:
  pip install requests python-dotenv

CONFIGURAÇÃO (.env):
  INSTAGRAM_ACCESS_TOKEN=   Token de acesso (Meta Business / Graph API)
  INSTAGRAM_USER_ID=        ID numérico da conta profissional Instagram
  INTERVALO_SEGUNDOS=10     Pausa entre envios (mínimo recomendado)
  DRY_RUN=true              true = simula sem enviar

COMO OBTER O ACCESS TOKEN:
  1. Acesse developers.facebook.com → Meus Apps
  2. Crie ou abra um app com produto "Instagram Graph API"
  3. Em "Ferramentas da API do Graph", gere um token com a permissão:
     instagram_manage_messages
  4. Cole em INSTAGRAM_ACCESS_TOKEN no .env

FLUXO DE USO:
  1. Sempre que identificar um novo seguidor, adicione o Instagram ID (número)
     dele ao arquivo novos_seguidores.json  (veja o formato abaixo).
  2. Execute:  python boas_vindas_instagram.py
  3. O script envia a DM, registra em log e marca como enviado.

FORMATO novos_seguidores.json:
  [
    { "instagram_id": "123456789", "username": "nome_do_seguidor" },
    ...
  ]

NOTA: A API do Instagram não permite enviar DMs a qualquer usuário de forma
irrestrita. O destinatário precisa ter iniciado uma conversa antes OU a conta
precisa ter permissão "instagram_manage_messages" aprovada pela Meta para envio
proativo (disponível para contas elegíveis). Use o modo DRY_RUN para validar
antes de ativar o envio real.
"""

import json
import os
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIGURAÇÃO ─────────────────────────────────────────────────────────────

ACCESS_TOKEN   = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
IG_USER_ID     = os.getenv("INSTAGRAM_USER_ID", "")
INTERVALO      = int(os.getenv("INTERVALO_SEGUNDOS", "10"))
DRY_RUN        = os.getenv("DRY_RUN", "true").lower() == "true"

SEGUIDORES_FILE = "novos_seguidores.json"
PROGRESSO_FILE  = "boas_vindas_enviados.json"
LOG_FILE        = "boas_vindas_instagram.log"

GRAPH_API_BASE  = "https://graph.facebook.com/v21.0"

# ─── MENSAGEM DE BOAS-VINDAS ──────────────────────────────────────────────────

MENSAGEM_BOAS_VINDAS = """Olá! Seja muito bem-vindo(a) à Loja do Avô 😊

Somos especialistas em segurança e autonomia 60+, com produtos cuidadosamente selecionados para proporcionar mais conforto, prevenção e qualidade de vida.

E para agradecer por estar aqui, você ganhou 10% OFF na sua primeira compra com o cupom:

PRIMEIRACOMPRA10

Nosso site:
www.lojadoavo.com.br

Qualquer dúvida, estamos sempre à disposição!"""

# ─── LOGGING ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# ─── PROGRESSO ────────────────────────────────────────────────────────────────

def carregar_enviados() -> set:
    if os.path.exists(PROGRESSO_FILE):
        with open(PROGRESSO_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def salvar_enviados(enviados: set):
    with open(PROGRESSO_FILE, "w", encoding="utf-8") as f:
        json.dump(list(enviados), f, ensure_ascii=False, indent=2)

# ─── ENVIO DE DM VIA INSTAGRAM GRAPH API ─────────────────────────────────────

def enviar_dm(instagram_id: str, mensagem: str) -> bool:
    """
    Envia uma DM para o usuário identificado por instagram_id.

    Endpoint: POST /{ig-user-id}/messages
    Docs: developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging
    """
    url = f"{GRAPH_API_BASE}/{IG_USER_ID}/messages"

    payload = {
        "recipient": {"id": instagram_id},
        "message":   {"text": mensagem},
        "access_token": ACCESS_TOKEN,
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code in (200, 201):
            return True
        log.warning(f"HTTP {resp.status_code} para {instagram_id}: {resp.text[:300]}")
        return False
    except requests.exceptions.RequestException as e:
        log.error(f"Erro de conexão para {instagram_id}: {e}")
        return False

# ─── LOOP PRINCIPAL ────────────────────────────────────────────────────────────

def main():
    if not DRY_RUN and not ACCESS_TOKEN:
        log.error("INSTAGRAM_ACCESS_TOKEN não configurado. Verifique o .env")
        return

    if not DRY_RUN and not IG_USER_ID:
        log.error("INSTAGRAM_USER_ID não configurado. Verifique o .env")
        return

    if not os.path.exists(SEGUIDORES_FILE):
        log.error(
            f"Arquivo '{SEGUIDORES_FILE}' não encontrado. "
            "Crie-o com a lista de novos seguidores (veja o docstring do script)."
        )
        return

    with open(SEGUIDORES_FILE, "r", encoding="utf-8") as f:
        seguidores = json.load(f)

    ja_enviados = carregar_enviados()

    total   = len(seguidores)
    enviados = 0
    falhas   = 0
    pulados  = 0

    log.info(f"{'[DRY RUN] ' if DRY_RUN else ''}Iniciando boas-vindas — {total} seguidor(es) carregado(s)")
    log.info(f"Ja enviados anteriormente: {len(ja_enviados)}")
    log.info(f"Intervalo entre mensagens: {INTERVALO}s")
    log.info("-" * 60)

    for i, seguidor in enumerate(seguidores, 1):
        ig_id    = str(seguidor.get("instagram_id", "")).strip()
        username = seguidor.get("username", ig_id)

        if not ig_id:
            log.warning(f"[{i}/{total}] instagram_id ausente — pulando")
            pulados += 1
            continue

        if ig_id in ja_enviados:
            log.info(f"[{i}/{total}] JA ENVIADO — pulando @{username}")
            pulados += 1
            continue

        log.info(f"[{i}/{total}] @{username} (ID: {ig_id})")

        if DRY_RUN:
            log.info(f"  [DRY RUN] Mensagem que seria enviada:\n{MENSAGEM_BOAS_VINDAS[:120]}...")
            enviados += 1
            ja_enviados.add(ig_id)
        else:
            sucesso = enviar_dm(ig_id, MENSAGEM_BOAS_VINDAS)
            if sucesso:
                enviados += 1
                ja_enviados.add(ig_id)
                log.info(f"  Enviado com sucesso")
            else:
                falhas += 1
                log.warning(f"  Falha no envio")

        salvar_enviados(ja_enviados)

        if i < total:
            time.sleep(INTERVALO)

    log.info("-" * 60)
    log.info("DISPARO CONCLUIDO")
    log.info(f"  Enviados: {enviados}")
    log.info(f"  Falhas:   {falhas}")
    log.info(f"  Pulados:  {pulados}")
    log.info(f"  Total:    {total}")


if __name__ == "__main__":
    main()
