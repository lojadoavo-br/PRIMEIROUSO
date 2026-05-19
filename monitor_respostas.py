"""
MONITOR DE RESPOSTAS — LOJA DO AVÔ
Monitora o WhatsApp Web e responde automaticamente todos os chats não lidos.

REQUISITOS:
  pip install selenium webdriver-manager

COMO USAR:
  1. python monitor_respostas.py
  2. Escaneie o QR Code
  3. Deixe rodando — ele monitora e responde sozinho
  4. Ctrl+C para parar
"""

import time
import random
import re
from datetime import datetime
from selenium.webdriver.common.keys import Keys

LOG_RESPOSTAS  = "log_respostas.txt"
INTERVALO_SCAN = 15  # segundos entre varreduras

# ─────────────────────────────────────────
# CLASSIFICAÇÃO
# ─────────────────────────────────────────

POSITIVO = ['obrigad', 'ótim', 'otim', 'excelent', 'perfeito', 'gostei',
            'adorei', 'ajudou', 'funcionou', 'muito bom', 'maravilh',
            'satisfeit', 'amei', 'curti', 'chegou', 'recebi', 'legal',
            'ficou bom', 'ficou ótim', 'tá bom', 'ta bom', '👍', '😊', '❤', '🙏']

PERGUNTA = ['como', 'onde', 'quando', 'qual', 'quanto', 'funciona',
            'usar', 'instalar', 'colocar', 'montar', 'regulag',
            'tamanho', 'medida', 'entrega', 'prazo', 'frete', '?']

PRECO    = ['caro', 'preço', 'preco', 'valor', 'desconto', 'barato',
            'custo', 'parcela', 'parcel', 'boleto', 'pix', 'pagamento']

PROBLEMA = ['não funciona', 'nao funciona', 'defeito', 'quebrou',
            'problema', 'errado', 'trocar', 'devolver', 'reclamaç',
            'danificad', 'veio errado', 'não chegou', 'nao chegou',
            'extraviado', 'sumiu']

NAO_QUER = ['não quero', 'nao quero', 'não preciso', 'nao preciso',
            'por enquanto não', 'tô bem', 'to bem', 'nao obrigad', 'não obrigad']

def classificar(texto):
    t = texto.lower()
    for p in PROBLEMA:
        if p in t: return 'problema'
    for p in NAO_QUER:
        if p in t: return 'nao_quer'
    for p in PRECO:
        if p in t: return 'preco'
    for p in PERGUNTA:
        if p in t: return 'pergunta'
    for p in POSITIVO:
        if p in t: return 'positivo'
    return 'neutro'

# ─────────────────────────────────────────
# RESPOSTAS
# ─────────────────────────────────────────

def resposta(categoria, nome_chat):
    # Pega só o primeiro nome do contato
    fn = nome_chat.strip().split()[0].capitalize() if nome_chat.strip() else 'olá'
    # Se for número, usa forma genérica
    if fn.startswith('+') or fn.isdigit():
        fn = 'olá'
        prefixo = 'Oi! '
    else:
        prefixo = f'Oi, {fn}! '

    if categoria == 'positivo':
        opcoes = [
            f"{prefixo}Fico muito feliz em saber 😊\n\nSe puder nos mandar uma foto do produto em uso, ajuda muito outras famílias que também buscam mais segurança e autonomia no dia a dia.\n\nE se tiver um minutinho, uma avaliação no nosso site é uma forma incrível de ajudar outras pessoas. Qualquer coisa, pode contar com a gente!",
            f"{prefixo}Que maravilha! Isso nos motiva muito 😊\n\nSe quiser compartilhar uma foto usando o produto, ficamos muito felizes — ajuda outras famílias que estão buscando mais qualidade de vida.\n\nContinue contando com a Loja do Avô sempre que precisar!",
        ]
        return random.choice(opcoes)

    elif categoria == 'pergunta':
        opcoes = [
            f"{prefixo}Pode perguntar à vontade 😊\n\nNossa equipe especializada vai te ajudar da melhor forma. Qual é a sua dúvida?",
            f"{prefixo}Com prazer te ajudo 😊\n\nMe conta o que você precisa saber que a gente orienta com cuidado.",
        ]
        return random.choice(opcoes)

    elif categoria == 'preco':
        return (
            f"{prefixo}Entendo! A Loja do Avô trabalha com produtos de alta qualidade, com curadoria especializada por fisioterapeuta. "
            f"Cada item foi testado e aprovado pensando em segurança, durabilidade e real benefício para quem usa.\n\n"
            f"Mais do que um produto, é um investimento em qualidade de vida 💙\n\n"
            f"Se quiser, posso te passar mais detalhes sobre o item que te interessou."
        )

    elif categoria == 'problema':
        return (
            f"{prefixo}Sinto muito por isso! 😟\n\n"
            f"Vou acionar nossa equipe de atendimento para te ajudar da melhor forma.\n\n"
            f"Pode nos passar mais detalhes do que aconteceu? Queremos resolver isso o mais rápido possível."
        )

    elif categoria == 'nao_quer':
        opcoes = [
            f"{prefixo}Tudo bem! Fico feliz que esteja bem 😊\n\nQualquer coisa que precisar no futuro, pode contar com a Loja do Avô. Estamos sempre aqui!",
            f"{prefixo}Sem problema nenhum 😊\n\nA Loja do Avô estará aqui sempre que precisar. Cuide-se bem!",
        ]
        return random.choice(opcoes)

    else:
        opcoes = [
            f"{prefixo}Obrigado por responder 😊\n\nQualquer dúvida ou necessidade, pode contar com a gente aqui na Loja do Avô!",
            f"{prefixo}Que bom ter seu retorno 😊\n\nEstamos à disposição sempre que precisar. Cuide-se!",
        ]
        return random.choice(opcoes)

# ─────────────────────────────────────────
# LOG
# ─────────────────────────────────────────

def ja_respondido(chat_id):
    try:
        with open(LOG_RESPOSTAS, 'r', encoding='utf-8') as f:
            for line in f:
                if f'|{chat_id}|' in line:
                    return True
    except FileNotFoundError:
        pass
    return False

def registrar(chat_id, nome, categoria, msg):
    ts = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with open(LOG_RESPOSTAS, 'a', encoding='utf-8') as f:
        f.write(f"OK|{chat_id}|{nome}|{categoria}|{ts}|{msg[:60]}\n")

# ─────────────────────────────────────────
# ENVIO DE MENSAGEM
# ─────────────────────────────────────────

def enviar_mensagem(driver, texto):
    from selenium.webdriver.common.by import By

    seletores_campo = [
        '//div[@contenteditable="true"][@data-tab="10"]',
        '//div[@contenteditable="true"][@title="Digite uma mensagem"]',
        '//div[@data-testid="conversation-compose-box-input"]',
        '//footer//div[@contenteditable="true"]',
    ]

    campo = None
    for sel in seletores_campo:
        try:
            elementos = driver.find_elements(By.XPATH, sel)
            if elementos:
                campo = elementos[0]
                break
        except:
            continue

    if not campo:
        raise Exception("Campo de texto não encontrado")

    campo.click()
    time.sleep(0.5)

    linhas = texto.split('\n')
    for i, linha in enumerate(linhas):
        campo.send_keys(linha)
        if i < len(linhas) - 1:
            campo.send_keys(Keys.SHIFT + Keys.ENTER)

    time.sleep(1)

    seletores_botao = [
        '//button[@data-testid="compose-btn-send"]',
        '//button[@aria-label="Enviar"]',
        '//span[@data-icon="send"]',
    ]
    for sel in seletores_botao:
        try:
            botoes = driver.find_elements(By.XPATH, sel)
            if botoes:
                botoes[0].click()
                return True
        except:
            continue

    campo.send_keys(Keys.ENTER)
    return True

# ─────────────────────────────────────────
# MONITORAMENTO
# ─────────────────────────────────────────

def monitorar():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager

    print(f"\n{'='*50}")
    print(f"MONITOR DE RESPOSTAS — LOJA DO AVÔ")
    print(f"{'='*50}")
    print(f"Varredura a cada {INTERVALO_SCAN} segundos")
    print(f"{'='*50}")

    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )

    driver.get("https://web.whatsapp.com")
    print("\nEscaneie o QR Code na janela do Chrome.")
    input("Pressione ENTER após escanear e o WhatsApp carregar completamente...")
    time.sleep(5)

    print("\n✅ Monitoramento iniciado! Aguardando respostas...")
    print("   (Pressione Ctrl+C para parar)\n")

    respondidos_sessao = set()

    while True:
        try:
            # Detecta chats com mensagens não lidas pelo badge verde
            seletores_nao_lidos = [
                '//span[contains(@aria-label,"mensagem não lida")]',
                '//span[@data-testid="icon-unread-count"]',
                '//span[contains(@class,"unread-count")]',
            ]

            chats_nao_lidos = []
            for sel in seletores_nao_lidos:
                encontrados = driver.find_elements(By.XPATH, sel)
                if encontrados:
                    chats_nao_lidos = encontrados
                    break

            if chats_nao_lidos:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {len(chats_nao_lidos)} chat(s) não lido(s) — processando...")

                for badge in chats_nao_lidos[:5]:
                    try:
                        # Sobe na árvore DOM para achar o container do chat
                        chat_container = None
                        for xpath_anc in [
                            './ancestor::div[@data-testid="cell-frame-container"]',
                            './ancestor::li',
                            './ancestor::div[@role="listitem"]',
                        ]:
                            try:
                                chat_container = badge.find_element(By.XPATH, xpath_anc)
                                break
                            except:
                                continue

                        if not chat_container:
                            continue

                        chat_container.click()
                        time.sleep(2)

                        # Pega o nome/número do chat aberto
                        nome_chat = ''
                        for sel_header in [
                            '//header//span[@dir="auto"][1]',
                            '//header//*[@data-testid="conversation-info-header-chat-title"]',
                            '//div[@data-testid="conversation-header"]//span[@dir="auto"]',
                        ]:
                            try:
                                el = driver.find_element(By.XPATH, sel_header)
                                nome_chat = el.text.strip()
                                if nome_chat:
                                    break
                            except:
                                continue

                        if not nome_chat:
                            continue

                        # Usa nome como ID único do chat
                        chat_id = re.sub(r'\s+', '_', nome_chat.lower())

                        if chat_id in respondidos_sessao or ja_respondido(chat_id):
                            respondidos_sessao.add(chat_id)
                            continue

                        # Lê a última mensagem recebida
                        ultima_msg = ''
                        for sel_msg in [
                            '//div[@data-testid="msg-container"][last()]//span[@dir="ltr"]',
                            '//div[contains(@class,"message-in")][last()]//span[@dir="ltr"]',
                            '//div[@data-id][last()]//span[@dir="ltr"]',
                        ]:
                            try:
                                msgs = driver.find_elements(By.XPATH, sel_msg)
                                if msgs:
                                    ultima_msg = msgs[-1].text.strip()
                                    if ultima_msg:
                                        break
                            except:
                                continue

                        if not ultima_msg:
                            continue

                        # Classifica e responde
                        categoria = classificar(ultima_msg)
                        msg_resp  = resposta(categoria, nome_chat)

                        print(f"\n  💬 {nome_chat}")
                        print(f"     Disse: \"{ultima_msg[:70]}\"")
                        print(f"     Categoria: {categoria}")

                        enviar_mensagem(driver, msg_resp)
                        time.sleep(2)

                        print(f"     ✅ Respondido!")
                        registrar(chat_id, nome_chat, categoria, ultima_msg)
                        respondidos_sessao.add(chat_id)

                    except Exception as e:
                        print(f"     ⚠️  Erro neste chat: {e}")
                        continue

            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Aguardando respostas...", end='\r')

        except Exception as e:
            print(f"\n⚠️  Erro na varredura: {e}")

        time.sleep(INTERVALO_SCAN)

# ─────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────

if __name__ == '__main__':
    monitorar()
