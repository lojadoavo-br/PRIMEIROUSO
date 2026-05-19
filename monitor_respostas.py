"""
MONITOR DE RESPOSTAS — LOJA DO AVÔ
Fica monitorando o WhatsApp Web e responde automaticamente
quando clientes que receberam o pós-venda enviarem mensagem.

REQUISITOS:
  pip install selenium webdriver-manager

COMO USAR:
  1. Rode APÓS o disparador já ter enviado as mensagens
  2. python monitor_respostas.py
  3. Escaneie o QR Code
  4. Deixe rodando em segundo plano — ele monitora e responde sozinho
  5. Ctrl+C para parar
"""

import time
import random
import re
from datetime import datetime
from urllib.parse import quote

LOG_DISPAROS   = "log_disparos.txt"
LOG_RESPOSTAS  = "log_respostas.txt"
INTERVALO_SCAN = 20   # segundos entre cada varredura de novas mensagens

# ─────────────────────────────────────────
# CLASSIFICAÇÃO DA MENSAGEM DO CLIENTE
# ─────────────────────────────────────────

POSITIVO    = ['obrigad', 'ótim', 'otim', 'excelent', 'perfeito', 'gostei',
               'adorei', 'ajudou', 'funcionou', 'muito bom', 'maravilh',
               'satisfeit', 'amei', 'curti', 'bom sim', 'sim ', 'tá ótimo',
               'chegou', 'recebi', '👍', '😊', '❤', '🙏']

PERGUNTA    = ['como', 'onde', 'quando', 'qual', 'quanto', 'funciona',
               'usar', 'instalar', 'colocar', 'montar', 'regulag',
               'tamanho', 'medida', 'entrega', 'prazo', 'frete', '?']

PRECO       = ['caro', 'preço', 'preco', 'valor', 'desconto', 'barato',
               'custo', 'parcela', 'parcel', 'boleto', 'pix', 'pagamento']

PROBLEMA    = ['não funciona', 'nao funciona', 'defeito', 'quebrou',
               'problema', 'errado', 'trocar', 'devolver', 'reclamaç',
               'danificad', 'veio errado', 'não chegou', 'nao chegou',
               'extraviado', 'sumiu', 'desmont']

NAO_QUER    = ['não quero', 'nao quero', 'não preciso', 'nao preciso',
               'por enquanto não', 'obrigado, não', 'obrigada, não',
               'tô bem', 'to bem', 'nao obrigad', 'não obrigad']

def classificar(texto):
    t = texto.lower()
    for p in PROBLEMA:
        if p in t:
            return 'problema'
    for p in NAO_QUER:
        if p in t:
            return 'nao_quer'
    for p in PRECO:
        if p in t:
            return 'preco'
    for p in PERGUNTA:
        if p in t:
            return 'pergunta'
    for p in POSITIVO:
        if p in t:
            return 'positivo'
    return 'neutro'

# ─────────────────────────────────────────
# RESPOSTAS AUTOMÁTICAS POR CATEGORIA
# ─────────────────────────────────────────

def resposta(categoria, primeiro_nome):
    fn = primeiro_nome

    if categoria == 'positivo':
        opcoes = [
            f"Que ótimo, {fn}! Fico muito feliz em saber 😊\n\nSe puder nos mandar uma foto do produto em uso, ajuda muito outras famílias que também buscam mais segurança e autonomia no dia a dia.\n\nE se tiver um minutinho, uma avaliação no nosso site é uma forma incrível de ajudar outras pessoas. Qualquer coisa, pode contar com a gente!",
            f"Que maravilha, {fn}! Isso nos motiva muito 😊\n\nSe quiser compartilhar uma foto usando o produto, ficamos muito felizes — ajuda outras famílias que estão buscando mais qualidade de vida.\n\nContinue contando com a Loja do Avô sempre que precisar!",
        ]
        return random.choice(opcoes)

    elif categoria == 'pergunta':
        opcoes = [
            f"Claro, {fn}! Pode perguntar à vontade 😊\n\nNossa equipe especializada vai te ajudar da melhor forma. Qual é a sua dúvida?",
            f"Oi, {fn}! Com prazer te ajudo 😊\n\nMe conta o que você precisa saber que a gente orienta com cuidado.",
        ]
        return random.choice(opcoes)

    elif categoria == 'preco':
        opcoes = [
            f"Entendo, {fn}! A Loja do Avô trabalha com produtos de alta qualidade, com curadoria especializada por fisioterapeuta. Cada item foi testado e aprovado pensando em segurança, durabilidade e real benefício para quem usa.\n\nMais do que um produto, é um investimento em qualidade de vida 💙\n\nSe quiser, posso te passar mais detalhes sobre o item que te interessou.",
            f"Compreendo, {fn}! Nossos produtos passam por uma seleção rigorosa — são itens que realmente funcionam e têm durabilidade.\n\nA gente preza por qualidade e segurança acima de tudo. Se precisar de mais informações, pode contar com a gente 😊",
        ]
        return random.choice(opcoes)

    elif categoria == 'problema':
        return (
            f"Oi, {fn}, sinto muito por isso! 😟\n\n"
            f"Vou acionar nossa equipe de atendimento para te ajudar da melhor forma.\n\n"
            f"Pode nos passar mais detalhes do que aconteceu? Queremos resolver isso o mais rápido possível."
        )

    elif categoria == 'nao_quer':
        opcoes = [
            f"Tudo bem, {fn}! Fico feliz que esteja bem 😊\n\nQualquer coisa que precisar no futuro, pode contar com a Loja do Avô. Estamos sempre aqui!",
            f"Entendido, {fn}! Sem problema nenhum 😊\n\nA Loja do Avô estará aqui sempre que precisar. Cuide-se bem!",
        ]
        return random.choice(opcoes)

    else:  # neutro
        opcoes = [
            f"Oi, {fn}! Obrigado por responder 😊\n\nQualquer dúvida ou necessidade, pode contar com a gente aqui na Loja do Avô!",
            f"Olá, {fn}! Que bom ter seu retorno 😊\n\nEstamos à disposição sempre que precisar. Cuide-se!",
        ]
        return random.choice(opcoes)

# ─────────────────────────────────────────
# LOG
# ─────────────────────────────────────────

def carregar_contatos_enviados():
    """Retorna dict {telefone: nome} de quem recebeu o pós-venda."""
    contatos = {}
    try:
        with open(LOG_DISPAROS, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('OK|'):
                    parts = line.strip().split('|')
                    if len(parts) >= 3:
                        contatos[parts[1]] = parts[2]  # tel -> nome
    except FileNotFoundError:
        print("⚠️  log_disparos.txt não encontrado. Rode o disparador primeiro.")
    return contatos

def ja_respondido(telefone):
    try:
        with open(LOG_RESPOSTAS, 'r', encoding='utf-8') as f:
            for line in f:
                if f'|{telefone}|' in line:
                    return True
    except FileNotFoundError:
        pass
    return False

def registrar_resposta(telefone, nome, categoria, msg_cliente):
    ts = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with open(LOG_RESPOSTAS, 'a', encoding='utf-8') as f:
        f.write(f"OK|{telefone}|{nome}|{categoria}|{ts}|{msg_cliente[:60]}\n")

def primeiro_nome(nome):
    parts = nome.strip().split()
    fn = parts[0].capitalize() if parts else nome
    if fn.lower() in ['free', 'teste', 'semear', 'lima']:
        return nome.strip().title()
    return fn

# ─────────────────────────────────────────
# MONITORAMENTO VIA SELENIUM
# ─────────────────────────────────────────

def monitorar():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager

    contatos = carregar_contatos_enviados()
    print(f"\n{'='*50}")
    print(f"MONITOR DE RESPOSTAS — LOJA DO AVÔ")
    print(f"{'='*50}")
    print(f"Monitorando respostas de {len(contatos)} contatos")
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
    input("Pressione ENTER após escanear e o WhatsApp carregar...")
    time.sleep(5)

    print("\n✅ Monitoramento iniciado! Aguardando respostas dos clientes...")
    print("   (Pressione Ctrl+C para parar)\n")

    respondidos_sessao = set()

    while True:
        try:
            # Busca chats com mensagens não lidas
            nao_lidos = driver.find_elements(
                By.XPATH,
                '//span[@data-testid="icon-unread-count" or contains(@aria-label,"não lida") or @data-icon="unread-count"]'
            )

            if nao_lidos:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {len(nao_lidos)} chat(s) com mensagem não lida...")

                # Clica no primeiro chat não lido
                for badge in nao_lidos[:3]:
                    try:
                        chat_item = badge.find_element(By.XPATH, './ancestor::div[@data-testid="cell-frame-container"]')
                        chat_item.click()
                        time.sleep(2)

                        # Pega o número do chat aberto via URL
                        url_atual = driver.current_url
                        tel_match = re.search(r'phone=(\d+)', url_atual)

                        # Tenta pegar o telefone pelo título do chat
                        try:
                            header = driver.find_element(By.XPATH, '//header//span[@dir="auto"]')
                            nome_chat = header.text.strip()
                        except:
                            nome_chat = ''

                        # Lê a última mensagem recebida
                        try:
                            mensagens_recebidas = driver.find_elements(
                                By.XPATH,
                                '//div[contains(@class,"message-in")]//span[@dir="ltr"]'
                            )
                            if mensagens_recebidas:
                                ultima_msg = mensagens_recebidas[-1].text.strip()
                            else:
                                ultima_msg = ''
                        except:
                            ultima_msg = ''

                        if not ultima_msg:
                            continue

                        # Verifica se é um contato que recebeu o pós-venda
                        nome_encontrado = None
                        tel_encontrado = None

                        for tel, nome in contatos.items():
                            # Compara pelo nome do chat (WhatsApp mostra o nome salvo)
                            nome_norm = nome.strip().lower()
                            chat_norm = nome_chat.lower()
                            if (nome_norm[:8] in chat_norm or chat_norm[:8] in nome_norm):
                                nome_encontrado = nome
                                tel_encontrado = tel
                                break

                        if not nome_encontrado or tel_encontrado in respondidos_sessao:
                            continue

                        if ja_respondido(tel_encontrado):
                            respondidos_sessao.add(tel_encontrado)
                            continue

                        # Classifica e responde
                        categoria = classificar(ultima_msg)
                        fn = primeiro_nome(nome_encontrado)
                        msg_resposta = resposta(categoria, fn)

                        print(f"\n💬 {nome_encontrado}")
                        print(f"   Cliente disse: \"{ultima_msg[:60]}\"")
                        print(f"   Categoria: {categoria}")
                        print(f"   Respondendo...")

                        # Digita e envia a resposta
                        try:
                            campo = driver.find_element(
                                By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'
                            )
                            # Digita linha por linha
                            for linha in msg_resposta.split('\n'):
                                campo.send_keys(linha)
                                if linha != msg_resposta.split('\n')[-1]:
                                    from selenium.webdriver.common.keys import Keys
                                    campo.send_keys(Keys.SHIFT + Keys.ENTER)

                            time.sleep(1)
                            botao = driver.find_element(By.XPATH, '//button[@aria-label="Enviar"]')
                            botao.click()
                            time.sleep(2)

                            print(f"   ✅ Resposta enviada ({categoria})")
                            registrar_resposta(tel_encontrado, nome_encontrado, categoria, ultima_msg)
                            respondidos_sessao.add(tel_encontrado)

                        except Exception as e:
                            print(f"   ❌ Erro ao enviar resposta: {e}")

                    except Exception as e:
                        continue

            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Nenhuma resposta nova. Aguardando...", end='\r')

        except Exception as e:
            print(f"\n⚠️  Erro na varredura: {e}")

        time.sleep(INTERVALO_SCAN)

# ─────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────

if __name__ == '__main__':
    monitorar()
