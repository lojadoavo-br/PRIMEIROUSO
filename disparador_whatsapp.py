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

def carregar_enviados():
    enviados = set()
    try:
        with open(LOG_ARQUIVO, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('OK|'):
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        enviados.add(parts[1])
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
    pendentes = [c for c in contatos if c['telefone'] not in enviados]

    print(f"\n{'='*50}")
    print(f"DISPARADOR DE PÓS-VENDA — LOJA DO AVÔ")
    print(f"{'='*50}")
    print(f"Total de contatos: {len(contatos)}")
    print(f"Já enviados anteriormente: {len(enviados)}")
    print(f"Pendentes para enviar agora: {len(pendentes)}")
    print(f"Intervalo entre mensagens: {INTERVALO_MIN}–{INTERVALO_MAX} segundos")
    print(f"Tempo estimado: ~{round(len(pendentes) * (INTERVALO_MIN + INTERVALO_MAX) / 2 / 60)} minutos")
    print(f"{'='*50}")
    input("\nPressione ENTER para abrir o WhatsApp Web e começar...")

    # Abre Chrome com perfil do usuário (já logado no WhatsApp Web)
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument(r"--user-data-dir=C:\Users\%USERNAME%\AppData\Local\Google\Chrome\User Data")
    opts.add_argument("--profile-directory=Default")
    # Evita detecção de automação
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )

    print("\nAguardando WhatsApp Web carregar (30s)...")
    driver.get("https://web.whatsapp.com")
    time.sleep(30)

    # Limita ao máximo de envios desta sessão
    pendentes = pendentes[:LIMITE_HOJE]

    erros = 0
    for i, contato in enumerate(pendentes, 1):
        tel = contato['telefone']
        nome = contato['nome']
        msg = contato['mensagem']

        print(f"\n[{i}/{len(pendentes)}] {nome} | {tel}")

        try:
            # Abre chat diretamente pela URL
            url = f"https://web.whatsapp.com/send?phone={tel}&text={quote(msg)}"
            driver.get(url)

            wait = WebDriverWait(driver, 20)

            # Aguarda campo de texto aparecer
            campo = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            ))

            time.sleep(random.uniform(3, 5))

            # Verifica se o número é válido (botão de envio aparece)
            try:
                botao_envio = driver.find_element(By.XPATH, '//button[@aria-label="Enviar"]')
            except:
                print(f"  ⚠️  Número inválido ou sem conta WhatsApp: {tel}")
                registrar_log('INVALIDO', tel, nome, 'Número sem WhatsApp')
                erros += 1
                time.sleep(3)
                continue

            # Envia a mensagem
            botao_envio.click()
            time.sleep(random.uniform(2, 3))

            print(f"  ✅ Enviado com sucesso")
            registrar_log('OK', tel, nome)

        except Exception as e:
            print(f"  ❌ Erro: {e}")
            registrar_log('ERRO', tel, nome, str(e)[:80])
            erros += 1

        # Intervalo aleatório entre mensagens
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
