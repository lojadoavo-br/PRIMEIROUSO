"""
AUTOMAÇÃO DE INSTAGRAM DIRECT — LOJA DO AVÔ
Envia DMs humanizadas para seguidores com sistema anti-spam inteligente.

REQUISITOS:
  pip install instagrapi

COMO USAR:
  1. Copie .env.example → .env e preencha INSTAGRAM_USER e INSTAGRAM_PASS
  2. Execute: python instagram_dm.py
  3. Na primeira execução, pode pedir código 2FA — basta digitar aqui
  4. O progresso é salvo em log_instagram.txt (retoma de onde parou)

LIMITES DE SEGURANÇA (padrão):
  • Máximo 50 mensagens por sessão
  • Intervalo 60–180 segundos entre envios
  • Pausas longas a cada 10 mensagens (simula comportamento humano)
"""

import os
import time
import random
import json
from datetime import datetime
from pathlib import Path

from mensagens_instagram import (
    get_mensagem_principal,
    get_resposta,
    detectar_intencao,
)

# ─────────────────────────────────────────────────────────────────
# CONFIGURAÇÕES — ajuste conforme necessário
# ─────────────────────────────────────────────────────────────────
INSTAGRAM_USER   = os.getenv("INSTAGRAM_USER", "")
INSTAGRAM_PASS   = os.getenv("INSTAGRAM_PASS", "")

LIMITE_POR_SESSAO    = int(os.getenv("LIMITE_POR_SESSAO", "50"))
INTERVALO_MIN        = int(os.getenv("INTERVALO_MIN", "60"))    # segundos
INTERVALO_MAX        = int(os.getenv("INTERVALO_MAX", "180"))   # segundos
PAUSA_LONGA_A_CADA   = int(os.getenv("PAUSA_LONGA_A_CADA", "10"))  # mensagens
PAUSA_LONGA_MIN      = int(os.getenv("PAUSA_LONGA_MIN", "300"))    # 5 min
PAUSA_LONGA_MAX      = int(os.getenv("PAUSA_LONGA_MAX", "600"))    # 10 min

LOG_ARQUIVO          = "log_instagram.txt"
SESSAO_ARQUIVO       = "sessao_instagram.json"

# ─────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────

def log(status: str, user_id: str, username: str, obs: str = "") -> None:
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linha = f"{status}|{user_id}|{username}|{ts}|{obs}\n"
    with open(LOG_ARQUIVO, "a", encoding="utf-8") as f:
        f.write(linha)


def carregar_enviados() -> set:
    enviados = set()
    try:
        with open(LOG_ARQUIVO, "r", encoding="utf-8") as f:
            for linha in f:
                if linha.startswith("OK|"):
                    partes = linha.strip().split("|")
                    if len(partes) >= 2:
                        enviados.add(partes[1])
    except FileNotFoundError:
        pass
    return enviados


# ─────────────────────────────────────────────────────────────────
# CLIENTE INSTAGRAM
# ─────────────────────────────────────────────────────────────────

def criar_cliente():
    try:
        from instagrapi import Client
    except ImportError:
        print("\n❌ Pacote 'instagrapi' não instalado.")
        print("   Execute: pip install instagrapi\n")
        raise SystemExit(1)

    cl = Client()
    cl.delay_range = [2, 5]  # delay interno adicional do instagrapi

    from instagrapi.exceptions import TwoFactorRequired

    def _login_com_2fa(cl, user, passwd):
        try:
            cl.login(user, passwd)
        except TwoFactorRequired:
            print("\n🔐 Verificação em duas etapas detectada.")
            print("   Abra o app do Instagram ou SMS e pegue o código de 6 dígitos.\n")
            codigo = input("   Digite o código aqui: ").strip()
            two_factor_id = cl.last_json.get("two_factor_info", {}).get("two_factor_identifier", "")
            cl.two_factor_login(user, passwd, codigo, two_factor_id)

    if Path(SESSAO_ARQUIVO).exists():
        try:
            cl.load_settings(SESSAO_ARQUIVO)
            cl.login(INSTAGRAM_USER, INSTAGRAM_PASS)
            print("✅ Sessão anterior carregada com sucesso.")
        except TwoFactorRequired:
            print("\n🔐 Verificação em duas etapas detectada.")
            print("   Abra o app do Instagram ou SMS e pegue o código de 6 dígitos.\n")
            codigo = input("   Digite o código aqui: ").strip()
            two_factor_id = cl.last_json.get("two_factor_info", {}).get("two_factor_identifier", "")
            cl.two_factor_login(INSTAGRAM_USER, INSTAGRAM_PASS, codigo, two_factor_id)
            cl.dump_settings(SESSAO_ARQUIVO)
        except Exception:
            print("⚠️  Sessão expirada. Fazendo login novo...")
            _login_com_2fa(cl, INSTAGRAM_USER, INSTAGRAM_PASS)
            cl.dump_settings(SESSAO_ARQUIVO)
    else:
        _login_com_2fa(cl, INSTAGRAM_USER, INSTAGRAM_PASS)
        cl.dump_settings(SESSAO_ARQUIVO)
        print("✅ Login realizado. Sessão salva.")

    return cl


# ─────────────────────────────────────────────────────────────────
# CARREGA SEGUIDORES
# ─────────────────────────────────────────────────────────────────

def carregar_seguidores(cl, quantidade: int = 0) -> list:
    """
    Retorna lista de dicts com {user_id, username} dos seguidores.
    quantidade=0 → busca todos (pode demorar para 66k).
    """
    print("\n⏳ Carregando lista de seguidores (pode demorar alguns minutos)...")
    meu_id = cl.user_id

    seguidores_raw = cl.user_followers(meu_id, amount=quantidade)
    seguidores = [
        {"user_id": str(uid), "username": info.username}
        for uid, info in seguidores_raw.items()
    ]

    print(f"✅ {len(seguidores)} seguidores carregados.")
    return seguidores


def carregar_seguidores_de_arquivo(caminho: str) -> list:
    """
    Alternativa: carrega seguidores de um JSON previamente exportado.
    Formato: [{"user_id": "123", "username": "usuario"}, ...]
    """
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────
# DISPARO PRINCIPAL
# ─────────────────────────────────────────────────────────────────

def disparar(cl, seguidores: list) -> None:
    enviados = carregar_enviados()
    # Inverte para começar pelos seguidores mais recentes
    seguidores_recentes = list(reversed(seguidores))
    pendentes = [s for s in seguidores_recentes if s["user_id"] not in enviados]

    total = len(pendentes)
    limite = min(total, LIMITE_POR_SESSAO)
    pendentes = pendentes[:limite]

    print(f"\n{'='*55}")
    print(f"  DISPARADOR INSTAGRAM DM — LOJA DO AVÔ")
    print(f"{'='*55}")
    print(f"  Seguidores total carregados : {len(seguidores)}")
    print(f"  Já enviados anteriormente   : {len(enviados)}")
    print(f"  Pendentes                   : {total}")
    print(f"  Enviar nesta sessão         : {limite}")
    print(f"  Intervalo entre mensagens   : {INTERVALO_MIN}–{INTERVALO_MAX}s")
    print(f"  Pausa longa a cada          : {PAUSA_LONGA_A_CADA} msgs")
    print(f"  Tempo estimado              : ~{round(limite * (INTERVALO_MIN + INTERVALO_MAX) / 2 / 60)} min")
    print(f"{'='*55}")
    input("\n  Pressione ENTER para começar o disparo...\n")

    erros = 0
    for i, seguidor in enumerate(pendentes, 1):
        uid      = seguidor["user_id"]
        username = seguidor["username"]

        print(f"[{i}/{limite}] @{username}", end="  ")

        try:
            mensagem = get_mensagem_principal()
            cl.direct_send(mensagem, [int(uid)])
            print("✅ enviado")
            log("OK", uid, username)

        except Exception as e:
            erro_str = str(e)[:100]
            print(f"❌ erro: {erro_str}")
            log("ERRO", uid, username, erro_str)
            erros += 1

            # Se o erro sugerir bloqueio de taxa, pausa mais longa
            if any(x in erro_str.lower() for x in ["challenge", "429", "spam", "block", "limit"]):
                pausa = random.uniform(600, 900)
                print(f"\n⚠️  Possível limite de taxa detectado. Pausando {pausa:.0f}s...\n")
                time.sleep(pausa)
                continue

        # Pausa longa a cada N mensagens enviadas
        if i % PAUSA_LONGA_A_CADA == 0 and i < limite:
            pausa_longa = random.uniform(PAUSA_LONGA_MIN, PAUSA_LONGA_MAX)
            print(f"\n⏸  Pausa longa após {i} msgs ({pausa_longa:.0f}s)...\n")
            time.sleep(pausa_longa)
        elif i < limite:
            espera = random.uniform(INTERVALO_MIN, INTERVALO_MAX)
            # Micro-variação humana: às vezes digita "mais devagar"
            if random.random() < 0.15:
                espera += random.uniform(20, 60)
            print(f"   ⏳ próximo em {espera:.0f}s")
            time.sleep(espera)

    print(f"\n{'='*55}")
    print(f"  DISPARO CONCLUÍDO")
    print(f"  Enviados com sucesso : {limite - erros}")
    print(f"  Erros               : {erros}")
    print(f"  Log salvo em        : {LOG_ARQUIVO}")
    print(f"{'='*55}\n")


# ─────────────────────────────────────────────────────────────────
# MODO RESPOSTAS (escuta DMs recebidas e responde automaticamente)
# ─────────────────────────────────────────────────────────────────

def modo_respostas(cl, intervalo_verificacao: int = 120) -> None:
    """
    Verifica DMs recebidas periodicamente e responde com base no contexto.
    Rode em paralelo ao disparo (em outro terminal) ou após.
    """
    print(f"\n{'='*55}")
    print(f"  MODO RESPOSTAS AUTOMÁTICAS — LOJA DO AVÔ")
    print(f"  Verificando caixas de entrada a cada {intervalo_verificacao}s")
    print(f"  Pressione Ctrl+C para encerrar")
    print(f"{'='*55}\n")

    respondidos = set()

    try:
        while True:
            try:
                threads = cl.direct_threads(amount=20)
                for thread in threads:
                    thread_id = str(thread.id)
                    if not thread.messages:
                        continue

                    ultima = thread.messages[0]
                    # Só responde mensagens recebidas (não enviadas por nós)
                    if str(ultima.user_id) == str(cl.user_id):
                        continue

                    msg_id = str(ultima.id)
                    if msg_id in respondidos:
                        continue

                    texto = getattr(ultima, "text", "") or ""
                    if not texto.strip():
                        continue

                    intencao = detectar_intencao(texto)
                    resposta = get_resposta(intencao)

                    participantes = [u.pk for u in thread.users if str(u.pk) != str(cl.user_id)]
                    if not participantes:
                        continue

                    username = thread.users[0].username if thread.users else "desconhecido"
                    print(f"💬 @{username} → intencao: {intencao}")
                    print(f"   Texto: {texto[:80]}")

                    time.sleep(random.uniform(5, 15))  # simula leitura humana
                    cl.direct_send(resposta, participantes)
                    respondidos.add(msg_id)
                    print(f"   ✅ Respondido\n")
                    log("RESPOSTA", str(participantes[0]), username, intencao[:30])

            except Exception as e:
                print(f"⚠️  Erro ao verificar mensagens: {e}")

            time.sleep(intervalo_verificacao + random.uniform(-10, 10))

    except KeyboardInterrupt:
        print("\n⏹  Modo respostas encerrado.")


# ─────────────────────────────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────────────────────────────

def _carregar_env():
    """Carrega .env se existir (sem dependência de python-dotenv)."""
    env_path = Path(".env")
    if not env_path.exists():
        return
    with open(env_path, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip())


if __name__ == "__main__":
    _carregar_env()

    INSTAGRAM_USER = os.getenv("INSTAGRAM_USER", "")
    INSTAGRAM_PASS = os.getenv("INSTAGRAM_PASS", "")

    if not INSTAGRAM_USER or not INSTAGRAM_PASS:
        print("\n❌ Configure INSTAGRAM_USER e INSTAGRAM_PASS no arquivo .env\n")
        raise SystemExit(1)

    print(f"\nUsuário: @{INSTAGRAM_USER}")

    MODO = os.getenv("MODO", "disparo").lower()

    cl = criar_cliente()

    if MODO == "respostas":
        modo_respostas(cl)

    elif MODO == "disparo":
        # Opção A: carrega seguidores direto da API (lento para 66k)
        # seguidores = carregar_seguidores(cl)

        # Opção B: carrega de arquivo JSON exportado previamente (recomendado)
        arquivo_seguidores = os.getenv("ARQUIVO_SEGUIDORES", "seguidores.json")
        if Path(arquivo_seguidores).exists():
            seguidores = carregar_seguidores_de_arquivo(arquivo_seguidores)
            print(f"✅ {len(seguidores)} seguidores carregados do arquivo.")
        else:
            print(f"⚠️  Arquivo {arquivo_seguidores} não encontrado. Buscando da API...")
            seguidores = carregar_seguidores(cl)
            # Salva para uso futuro
            with open(arquivo_seguidores, "w", encoding="utf-8") as f:
                json.dump(seguidores, f, ensure_ascii=False, indent=2)
            print(f"💾 Lista salva em {arquivo_seguidores} para próximas sessões.")

        disparar(cl, seguidores)

    else:
        print(f"❌ MODO inválido: '{MODO}'. Use 'disparo' ou 'respostas'.")
