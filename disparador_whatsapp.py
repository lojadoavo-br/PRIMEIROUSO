"""
DISPARADOR DE PÓS-VENDA — LOJA DO AVÔ
Roda na sua máquina com o Chrome aberto e logado no WhatsApp Web.

REQUISITOS:
  pip install selenium webdriver-manager openpyxl

COMO USAR:
  1. Abra o Chrome normalmente e acesse web.whatsapp.com
  2. Certifique-se que está logado
  3. Rode: python disparador_whatsapp.py
  4. NÃO mexa no PC enquanto roda — o script controla o navegador
"""

import time
import random
import re
from urllib.parse import quote
from datetime import datetime

# ─────────────────────────────────────────
# CONFIGURAÇÕES — AJUSTE AQUI SE PRECISAR
# ─────────────────────────────────────────
INTERVALO_MIN = 25   # segundos mínimos entre mensagens
INTERVALO_MAX = 45   # segundos máximos entre mensagens
CAMINHO_PLANILHA = "PLANILHA ULTIMOS 6 MESES.xlsx"
LOG_ARQUIVO = "log_disparos.txt"
LIMITE_HOJE = 100    # máximo de mensagens por sessão
COMECAR_DE = "5511940068925"  # começar a partir deste número (Ana Marcato)

# ─────────────────────────────────────────
# EXTRAÇÃO E GERAÇÃO DAS MENSAGENS
# ─────────────────────────────────────────

def parse_date(d):
    try:
        return datetime.strptime(str(d), '%d/%m/%Y %H:%M')
    except:
        return datetime.min

def first_name(nome):
    parts = nome.strip().split()
    fn = parts[0].capitalize() if parts else nome
    if fn.lower() in ['free', 'teste', 'semear', 'lima']:
        return nome.strip().title()
    return fn

def clean_phone(tel):
    if '|' in str(tel):
        tel = str(tel).split('|')[0]
    digits = re.sub(r'\D', '', str(tel))
    if digits and not digits.startswith('55'):
        digits = '55' + digits
    return digits

def categorize(produtos):
    cats = set()
    combined = ' '.join(produtos).lower()
    if any(x in combined for x in ['barra de apoio', 'barra para']):
        cats.add('barra')
    if 'tapete' in combined:
        cats.add('tapete')
    if 'andador' in combined:
        cats.add('andador')
    if 'bengala' in combined:
        cats.add('bengala')
    if 'cadeira de banho' in combined or 'cadeira de rodas' in combined:
        cats.add('cadeira_banho')
    if 'poltrona' in combined or 'lift' in combined or 'reclinável' in combined:
        cats.add('poltrona')
    if any(x in combined for x in ['almofada', 'assento elevado', 'assento ortopédico', 'assento sanitário']):
        cats.add('conforto')
    if any(x in combined for x in ['fralda', 'absorvente', 'roupa íntima', 'coletor de urina', 'papagaio', 'lençol']):
        cats.add('incontinencia')
    if any(x in combined for x in ['bota imobilizadora', 'colar cervical', 'meia de compressão', 'faixa', 'curativo']):
        cats.add('pos_op')
    if any(x in combined for x in ['almofada térmica', 'travesseiro', 'almofada de ervas']):
        cats.add('termoterapia')
    if 'porta comprimido' in combined or 'pilbox' in combined:
        cats.add('medicacao')
    return cats

def gen_msg(nome, cats):
    fn = first_name(nome)
    if 'poltrona' in cats:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber como está sendo a experiência com a poltrona 😊\n\nEla já está bem posicionada na rotina? O conforto e o suporte têm ajudado no dia a dia?\n\nSe surgir alguma dúvida ou precisar de orientação, pode contar com a gente."
    elif 'andador' in cats:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber como está a adaptação com o andador 😊\n\nEstá sendo mais fácil se movimentar? Tem alguma dúvida sobre uso ou regulagem?\n\nA gente gosta de acompanhar de perto como foi a experiência."
    elif 'bengala' in cats:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber como está sendo o uso da bengala 😊\n\nA empunhadura ficou confortável? Está ajudando na mobilidade do dia a dia?\n\nQualquer dúvida, pode contar com a gente."
    elif 'barra' in cats:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber como ficou a instalação da barra de apoio 😊\n\nJá está usando bem? Fez diferença na segurança e na autonomia?\n\nQuando bem posicionada, ela realmente muda a rotina."
    elif 'cadeira_banho' in cats:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber como está sendo a experiência com a cadeira de banho 😊\n\nEstá trazendo mais conforto e segurança na hora do banho?\n\nA gente sabe que esses momentos fazem muita diferença na autonomia do dia a dia."
    elif 'tapete' in cats:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber como está o tapete antiderrapante 😊\n\nJá percebeu mais segurança nas áreas molhadas? Ficou bem posicionado?\n\nPrevenção de quedas começa nos pequenos detalhes do dia a dia."
    elif 'pos_op' in cats:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber como está indo a recuperação e a adaptação com o produto 😊\n\nTem ajudado no conforto e na mobilidade?\n\nQualquer dúvida sobre uso ou posicionamento, pode contar com nossa equipe."
    elif 'incontinencia' in cats:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber se os produtos chegaram bem e se estão atendendo à expectativa 😊\n\nA qualidade e o conforto estão bons?\n\nQualquer coisa que precisar, pode contar com a Loja do Avô."
    elif 'conforto' in cats:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber como está a experiência com o produto 😊\n\nJá notou diferença no conforto e no posicionamento?\n\nConforto e postura certa fazem muita diferença para o bem-estar no dia a dia."
    elif 'termoterapia' in cats:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber se a almofada térmica está ajudando bem 😊\n\nJá sentiu alívio? O calor terapêutico é um grande aliado para o conforto muscular e articular.\n\nQualquer dúvida, pode contar com a gente."
    elif 'medicacao' in cats:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber se o porta-comprimidos está sendo útil na rotina 😊\n\nFacilita na organização dos medicamentos?\n\nEsses detalhes fazem muita diferença na segurança do dia a dia."
    else:
        return f"Olá, {fn}! Tudo bem?\n\nPassando para saber como está sendo a experiência com o produto da Loja do Avô 😊\n\nEstá ajudando bem no dia a dia? Tem alguma dúvida sobre o uso?\n\nA gente gosta de acompanhar de perto como foi a experiência dos nossos clientes."

def carregar_contatos(planilha):
    import openpyxl
    wb = openpyxl.load_workbook(planilha)
    ws = wb.active
    raw = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        pedido_id, data, nome, telefone, produto = row
        tel = str(telefone).strip() if telefone else ''
        if not tel or tel == 'None':
            continue
        if tel not in raw:
            raw[tel] = {'nome': str(nome).strip(), 'produtos': [], 'data': data}
        if produto:
            raw[tel]['produtos'].append(str(produto).strip())

    skip = ['free fire', 'teste diego', 'teste']
    sorted_raw = sorted(raw.items(), key=lambda x: parse_date(x[1]['data']))

    contatos = []
    for tel, info in sorted_raw:
        if any(s in info['nome'].lower() for s in skip):
            continue
        phone = clean_phone(tel)
        if len(phone) < 12:
            continue
        msg = gen_msg(info['nome'], categorize(info['produtos']))
        contatos.append({'nome': info['nome'], 'telefone': phone, 'mensagem': msg})

    return contatos

# ─────────────────────────────────────────
# CARREGA PROGRESSO ANTERIOR (se tiver)
# ─────────────────────────────────────────

def normalizar_tel(tel):
    """Remove tudo que não é número para comparação segura."""
    import re
    return re.sub(r'\D', '', str(tel))

def carregar_enviados():
    enviados = set()
    try:
        with open(LOG_ARQUIVO, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('OK|'):
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        # Salva tanto o número original quanto normalizado
                        enviados.add(parts[1])
                        enviados.add(normalizar_tel(parts[1]))
    except FileNotFoundError:
        pass
    return enviados

def registrar_log(status, telefone, nome, obs=''):
    ts = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with open(LOG_ARQUIVO, 'a', encoding='utf-8') as f:
        f.write(f"{status}|{telefone}|{nome}|{ts}|{obs}\n")

# ─────────────────────────────────────────
# DISPARO VIA WHATSAPP WEB
# ─────────────────────────────────────────

def disparar(contatos):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager

    enviados = carregar_enviados()
    # Filtra pendentes verificando número normalizado também
    pendentes = [
        c for c in contatos
        if c['telefone'] not in enviados
        and normalizar_tel(c['telefone']) not in enviados
    ]

    # Se COMECAR_DE definido, pula todos que vierem antes desse número
    if COMECAR_DE:
        idx = next(
            (i for i, c in enumerate(pendentes)
             if normalizar_tel(c['telefone']) == normalizar_tel(COMECAR_DE)),
            None
        )
        if idx is not None:
            pulados = idx
            pendentes = pendentes[idx:]
            print(f"  ▶ Iniciando a partir de: {pendentes[0]['nome']} (pulando {pulados} anteriores)")
        else:
            print(f"  ⚠️  COMECAR_DE não encontrado nos pendentes — começando do início")

    print(f"\n{'='*50}")
    print(f"DISPARADOR DE PÓS-VENDA — LOJA DO AVÔ")
    print(f"{'='*50}")
    print(f"Total de contatos na planilha: {len(contatos)}")
    print(f"Já enviados (não serão repetidos): {len(contatos) - len(pendentes)}")
    print(f"Pendentes para enviar agora: {len(pendentes)}")
    print(f"Limite desta sessão: {LIMITE_HOJE}")
    print(f"Serão enviados hoje: {min(len(pendentes), LIMITE_HOJE)}")
    print(f"Intervalo entre mensagens: {INTERVALO_MIN}–{INTERVALO_MAX} segundos")
    print(f"Tempo estimado: ~{round(min(len(pendentes), LIMITE_HOJE) * (INTERVALO_MIN + INTERVALO_MAX) / 2 / 60)} minutos")
    print(f"{'='*50}")

    if len(pendentes) == 0:
        print("\n✅ Todos os contatos já receberam a mensagem! Nada a enviar.")
        return

    print(f"\nPrimeiros 5 contatos desta sessão:")
    for c in pendentes[:5]:
        print(f"  - {c['nome']} | {c['telefone']}")

    input("\nPressione ENTER para abrir o WhatsApp Web e começar...")

    # Limita ao máximo de envios desta sessão
    pendentes = pendentes[:LIMITE_HOJE]

    def iniciar_driver():
        opts = Options()
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--no-sandbox")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        d = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        d.get("https://web.whatsapp.com")
        return d

    driver = iniciar_driver()
    print("\n" + "="*50)
    print("ESCANEIE O QR CODE do WhatsApp Web na janela que abriu.")
    print("Depois volte aqui e pressione ENTER para começar o disparo.")
    print("="*50)
    input("\nPressione ENTER após escanear o QR Code...")
    time.sleep(5)

    erros = 0
    for i, contato in enumerate(pendentes, 1):
        tel = contato['telefone']
        nome = contato['nome']
        msg = contato['mensagem']

        print(f"\n[{i}/{len(pendentes)}] {nome} | {tel}")

        tentativas = 0
        while tentativas < 2:
            try:
                url = f"https://web.whatsapp.com/send?phone={tel}&text={quote(msg)}"
                driver.get(url)

                wait = WebDriverWait(driver, 25)

                # Tenta múltiplos seletores para o campo de texto
                campo = None
                for sel in [
                    '//div[@contenteditable="true"][@data-tab="10"]',
                    '//div[@contenteditable="true"][@title="Digite uma mensagem"]',
                    '//footer//div[@contenteditable="true"]',
                ]:
                    try:
                        campo = wait.until(EC.presence_of_element_located((By.XPATH, sel)))
                        break
                    except:
                        continue

                if not campo:
                    raise Exception("Campo de texto não encontrado")

                time.sleep(random.uniform(3, 5))

                # Tenta múltiplos seletores para o botão de envio
                botao_envio = None
                for sel in [
                    '//button[@data-testid="compose-btn-send"]',
                    '//button[@aria-label="Enviar"]',
                    '//span[@data-icon="send"]',
                ]:
                    try:
                        botao_envio = driver.find_element(By.XPATH, sel)
                        break
                    except:
                        continue

                if not botao_envio:
                    print(f"  ⚠️  Número inválido ou sem WhatsApp: {tel}")
                    registrar_log('INVALIDO', tel, nome, 'Número sem WhatsApp')
                    erros += 1
                    break

                botao_envio.click()
                time.sleep(random.uniform(2, 3))
                print(f"  ✅ Enviado com sucesso")
                registrar_log('OK', tel, nome)
                break

            except Exception as e:
                tentativas += 1
                msg_erro = str(e)[:120]
                print(f"  ⚠️  Tentativa {tentativas} falhou: {msg_erro[:60]}")

                # Chrome travou — reinicia
                if any(x in msg_erro for x in ['no such window', 'disconnected', 'not reachable', 'chrome not']):
                    print(f"  🔄 Chrome travou. Reiniciando navegador...")
                    try:
                        driver.quit()
                    except:
                        pass
                    time.sleep(5)
                    driver = iniciar_driver()
                    print("  ↩️  Abra o WhatsApp Web e escaneie o QR Code novamente.")
                    input("  Pressione ENTER após escanear...")
                    time.sleep(5)
                else:
                    if tentativas >= 2:
                        registrar_log('ERRO', tel, nome, msg_erro[:80])
                        erros += 1
                    time.sleep(3)

        # Intervalo entre mensagens
        if i < len(pendentes):
            espera = random.uniform(INTERVALO_MIN, INTERVALO_MAX)
            print(f"  ⏳ Aguardando {espera:.0f}s antes do próximo...")
            time.sleep(espera)

    print(f"\n{'='*50}")
    print(f"DISPARO CONCLUÍDO")
    print(f"Enviados: {len(pendentes) - erros}")
    print(f"Erros/inválidos: {erros}")
    print(f"Log salvo em: {LOG_ARQUIVO}")
    print(f"{'='*50}")

    driver.quit()

# ─────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────

if __name__ == '__main__':
    print("Carregando contatos da planilha...")
    contatos = carregar_contatos(CAMINHO_PLANILHA)
    print(f"{len(contatos)} contatos carregados.")
    disparar(contatos)
