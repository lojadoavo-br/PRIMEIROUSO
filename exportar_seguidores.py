"""
EXPORTADOR DE SEGUIDORES — LOJA DO AVÔ
Exporta a lista completa de seguidores para seguidores.json
antes de rodar o disparo (recomendado para 66k seguidores).

COMO USAR:
  python exportar_seguidores.py

O arquivo seguidores.json será criado e reutilizado pelo instagram_dm.py.
Isso evita buscar os 66k seguidores toda vez que rodar o disparo.
"""

import os
import json
import time
import random
from pathlib import Path


def _carregar_env():
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


def exportar():
    _carregar_env()

    try:
        from instagrapi import Client
    except ImportError:
        print("\n❌ Instale: pip install instagrapi\n")
        raise SystemExit(1)

    user = os.getenv("INSTAGRAM_USER", "")
    passwd = os.getenv("INSTAGRAM_PASS", "")

    if not user or not passwd:
        print("\n❌ Configure INSTAGRAM_USER e INSTAGRAM_PASS no .env\n")
        raise SystemExit(1)

    cl = Client()
    cl.delay_range = [2, 5]

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

    sessao = Path("sessao_instagram.json")
    if sessao.exists():
        try:
            cl.load_settings(str(sessao))
            cl.login(user, passwd)
            print("✅ Sessão anterior reutilizada.")
        except TwoFactorRequired:
            print("\n🔐 Verificação em duas etapas detectada.")
            print("   Abra o app do Instagram ou SMS e pegue o código de 6 dígitos.\n")
            codigo = input("   Digite o código aqui: ").strip()
            two_factor_id = cl.last_json.get("two_factor_info", {}).get("two_factor_identifier", "")
            cl.two_factor_login(user, passwd, codigo, two_factor_id)
            cl.dump_settings(str(sessao))
        except Exception:
            _login_com_2fa(cl, user, passwd)
            cl.dump_settings(str(sessao))
    else:
        _login_com_2fa(cl, user, passwd)
        cl.dump_settings(str(sessao))
        print("✅ Login realizado.")

    print(f"\n⏳ Exportando seguidores de @{user}...")
    print("   Isso pode levar 30–90 minutos para 66 mil seguidores.")
    print("   Deixe rodando em segundo plano.\n")

    meu_id = cl.user_id
    seguidores_raw = cl.user_followers(meu_id, amount=0)

    seguidores = [
        {"user_id": str(uid), "username": info.username}
        for uid, info in seguidores_raw.items()
    ]

    saida = "seguidores.json"
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(seguidores, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(seguidores)} seguidores exportados para {saida}")
    print("   Agora rode: python instagram_dm.py\n")


if __name__ == "__main__":
    exportar()
