"""
BANCO DE MENSAGENS — LOJA DO AVÔ
Instagram Direct: 20 variações principais + aberturas + fechamentos + respostas contextuais
"""

import random

CUPOM = "PRIMEIRACOMPRA10"
SITE = "lojadoavo.com.br"

# ══════════════════════════════════════════════════════════════════
# 20 VARIAÇÕES DA MENSAGEM PRINCIPAL
# ══════════════════════════════════════════════════════════════════

MENSAGENS_PRINCIPAIS = [

    # 1
    """Olá 😊
Passando para agradecer por acompanhar a Loja do Avô.

Somos especialistas em segurança, autonomia e qualidade de vida 60+, ajudando milhares de famílias em todo o Brasil a criarem ambientes mais seguros e confortáveis.

Para agradecer sua presença aqui, você ganhou 10% OFF na primeira compra:

🎁 PRIMEIRACOMPRA10

Fico feliz em ter você por aqui. Se tiver qualquer dúvida, é só chamar.""",

    # 2
    """Oi, tudo bem? 😊

Aqui é da Loja do Avô — a primeira loja do Brasil especializada em segurança e autonomia para pessoas acima de 60 anos.

Aproveitei para passar aqui e agradecer por nos acompanhar. É muito bom saber que você faz parte dessa comunidade.

Como um presente de boas-vindas, deixo um cupom especial:

🎁 PRIMEIRACOMPRA10 → 10% OFF na primeira compra

Qualquer dúvida sobre produtos ou adaptações, estou por aqui 💛""",

    # 3
    """Olá! Tudo bem por aí? 😊

Aqui é da equipe da Loja do Avô. Passando pra agradecer por nos seguir.

Trabalhamos há mais de 15 anos ajudando famílias a criarem ambientes mais seguros, confortáveis e adaptados para quem tem 60+. Nosso time conta até com fisioterapeuta especialista em geriatria 😊

Separei um cupom de 10% OFF pra você conhecer nosso site:

🎁 PRIMEIRACOMPRA10

Qualquer coisa, pode me chamar aqui.""",

    # 4
    """Oi 👋

Passei aqui só pra agradecer por acompanhar a Loja do Avô. Significa muito pra gente.

A nossa missão é ajudar pessoas 60+ — e também seus familiares — a terem mais segurança, independência e bem-estar no dia a dia.

E como forma de dizer obrigada:

🎁 Use PRIMEIRACOMPRA10 e ganhe 10% OFF na primeira compra no nosso site.

Se quiser conversar ou tirar dúvidas, estou aqui 😊""",

    # 5
    """Olá! 😊

Sabia que a Loja do Avô é a primeira loja do Brasil especializada em segurança e autonomia 60+?

Passando pra agradecer por nos acompanhar aqui. Nosso trabalho nasce da vontade de fazer diferença real na vida das pessoas — dentro de casa, no banheiro, na cozinha, na mobilidade do dia a dia.

Preparei um presente pra você:

🎁 PRIMEIRACOMPRA10 → 10% de desconto na primeira compra

Fico à disposição pra qualquer dúvida 💛""",

    # 6
    """Oi! Tudo certo? 😊

Aqui é da Loja do Avô. Vi que você nos acompanha e queria passar pra dizer: muito obrigada!

Somos especialistas em produtos que trazem mais segurança, conforto e autonomia para pessoas acima de 60 anos. Nossa equipe tem até fisioterapeuta em geriatria pra orientar as melhores escolhas.

Como presente de gratidão:

🎁 PRIMEIRACOMPRA10 — 10% OFF na primeira compra

Se precisar de ajuda pra escolher algo, pode contar comigo.""",

    # 7
    """Olá 😊

Passei aqui pra agradecer por fazer parte da nossa comunidade na Loja do Avô.

Cuidar de quem amamos é um ato de amor. E a gente existe pra ajudar nisso — com produtos especializados em segurança, prevenção de quedas, mobilidade e adaptação residencial para quem tem 60+.

Tenho um cupom especial pra te dar:

🎁 PRIMEIRACOMPRA10 = 10% OFF na primeira compra

Conta comigo pra o que precisar 💛""",

    # 8
    """Olá! 😊

Aqui é da Loja do Avô — especialistas em longevidade, segurança e qualidade de vida 60+.

Passando pra agradecer por nos seguir. Cada pessoa que nos acompanha tem uma história, e a gente quer fazer parte dela de um jeito positivo.

Como gratidão, você ganhou:

🎁 10% de desconto com o cupom PRIMEIRACOMPRA10

Visite nosso site e se precisar de ajuda pra escolher, estou aqui.""",

    # 9
    """Oi, tudo bem? 💛

Só passando pra agradecer por seguir a Loja do Avô. Faz muito sentido saber que você se importa com esse tema.

A gente atua há mais de 15 anos ajudando pessoas 60+ — e suas famílias — a viverem com mais segurança e independência. Prevenção de quedas, adaptação do lar, mobilidade, conforto... tudo isso com muito carinho.

Separei um cupom especial pra você:

🎁 PRIMEIRACOMPRA10 → 10% OFF na primeira compra

Qualquer dúvida, pode chamar aqui 😊""",

    # 10
    """Olá! Que bom ter você aqui 😊

Sou da Loja do Avô — a primeira loja do Brasil especializada em segurança e autonomia para pessoas acima de 60 anos.

Acompanho com muito carinho cada pessoa que passa a nos seguir. E queria deixar um presente de boas-vindas:

🎁 PRIMEIRACOMPRA10 → 10% de desconto na primeira compra

Qualquer dúvida sobre produtos, adaptações ou o que precisar, pode me chamar aqui 😊""",

    # 11
    """Oi! 👋

Aqui é da equipe Loja do Avô. Passando só pra agradecer por nos acompanhar.

Trabalhamos com produtos de segurança, mobilidade e conforto pensados especialmente para pessoas 60+. Nossa equipe conta com fisioterapeuta especialista em geriatria — porque a gente leva isso muito a sério.

Deixo um cupom especial pra você:

🎁 PRIMEIRACOMPRA10 = 10% na primeira compra

Precisando de qualquer orientação, estou aqui 😊""",

    # 12
    """Olá 😊

Vi que você nos acompanha aqui e queria agradecer de coração.

A Loja do Avô nasceu de uma missão simples: ajudar pessoas 60+ e suas famílias a viverem com mais segurança, autonomia e tranquilidade. São mais de 15 anos nesse propósito.

Como forma de dizer obrigada:

🎁 Use o cupom PRIMEIRACOMPRA10 e ganhe 10% OFF na sua primeira compra

Fico à disposição, pode chamar quando quiser 💛""",

    # 13
    """Oi, tudo bem? 😊

Aqui é da Loja do Avô — especialistas em qualidade de vida, segurança e autonomia 60+.

Queria passar pessoalmente pra agradecer por nos seguir. São mais de 15 anos cuidando de famílias em todo o Brasil com muito carinho e dedicação.

Pra você que nos acompanha:

🎁 PRIMEIRACOMPRA10 → 10% OFF na primeira compra no site

Se tiver dúvida sobre qualquer produto ou necessidade, pode contar comigo.""",

    # 14
    """Olá! Que alegria ter você aqui 😊

Passando rapidinho só pra agradecer por acompanhar a Loja do Avô.

A gente é especialista em segurança 60+: barras de apoio, tapetes antiderrapantes, andadores, bengalas adaptadas, e tudo que ajuda a viver com mais autonomia e menos riscos.

Deixo um presente:

🎁 Cupom PRIMEIRACOMPRA10 → 10% de desconto na 1ª compra

Qualquer dúvida, estou por aqui 💛""",

    # 15
    """Oi 😊

Aqui é da Loja do Avô. Passando pra agradecer por fazer parte da nossa comunidade.

Nossa missão é ser referência em segurança, longevidade e adaptação para pessoas acima de 60 anos — com produtos de qualidade, orientação especializada e muito carinho em cada detalhe.

Presente de boas-vindas:

🎁 PRIMEIRACOMPRA10 = 10% OFF na primeira compra

Se quiser conhecer nosso site ou tirar dúvidas, pode chamar aqui a qualquer hora.""",

    # 16
    """Olá! 😊

Sabia que a Loja do Avô tem fisioterapeuta especialista em geriatria na equipe?

A gente vai muito além de vender produtos — oferecemos orientação especializada pra ajudar cada pessoa a escolher o que realmente faz diferença na segurança e autonomia do dia a dia.

Pra agradecer por nos seguir:

🎁 PRIMEIRACOMPRA10 → 10% OFF na primeira compra

Conte comigo pra qualquer dúvida 😊""",

    # 17
    """Oi, tudo bem por aí? 😊

Sou da Loja do Avô — e passei aqui só pra agradecer por nos acompanhar.

Trabalhamos há mais de 15 anos com um propósito claro: garantir que pessoas 60+ tenham segurança, conforto e independência no seu dia a dia. Desde a adaptação do banheiro até a escolha da bengala certa.

Como gratidão pela sua presença aqui:

🎁 10% de desconto com o cupom PRIMEIRACOMPRA10

Pode me chamar se quiser conversar ou tiver dúvidas 💛""",

    # 18
    """Olá! 😊

Aqui é da Loja do Avô — a primeira loja do Brasil focada em segurança e autonomia 60+.

Cada seguidor nosso importa de verdade. Por isso passamos aqui pessoalmente pra dizer: obrigada por nos acompanhar.

Como presente:

🎁 Use PRIMEIRACOMPRA10 na primeira compra e ganhe 10% OFF

Se precisar de ajuda na escolha de algum produto ou tiver dúvidas sobre adaptação residencial, estou aqui 😊""",

    # 19
    """Olá 💛

Passando pra agradecer por fazer parte da nossa comunidade aqui na Loja do Avô.

Somos especialistas em longevidade e segurança 60+ — com produtos que previnem quedas, garantem mobilidade e adaptam o lar para mais conforto e autonomia.

Pra quem nos acompanha, tenho um cupom especial:

🎁 PRIMEIRACOMPRA10 → 10% OFF na primeira compra

Qualquer dúvida ou necessidade, pode chamar aqui. Estamos sempre por perto 😊""",

    # 20
    """Oi! Tudo bem? 😊

Aqui é da equipe Loja do Avô. Passando pra agradecer por seguir a gente.

A nossa história tem mais de 15 anos de dedicação a um propósito: ajudar pessoas 60+ e suas famílias a viverem com mais segurança, independência e qualidade de vida.

Deixo um presente pra você conhecer:

🎁 PRIMEIRACOMPRA10 = 10% de desconto na primeira compra

Fico feliz em te ter por aqui. Qualquer dúvida, pode me chamar 😊""",
]


# ══════════════════════════════════════════════════════════════════
# 10 ABERTURAS
# ══════════════════════════════════════════════════════════════════

ABERTURAS = [
    "Olá 😊",
    "Oi, tudo bem? 😊",
    "Olá! Tudo bem por aí? 😊",
    "Oi 👋",
    "Olá! Que bom ter você aqui 😊",
    "Oi! 👋",
    "Olá 💛",
    "Oi, tudo bem por aí? 💛",
    "Olá! Que alegria ter você aqui 😊",
    "Oi! Tudo certo? 😊",
]


# ══════════════════════════════════════════════════════════════════
# 10 FECHAMENTOS
# ══════════════════════════════════════════════════════════════════

FECHAMENTOS = [
    "Fico feliz em ter você por aqui. Se tiver qualquer dúvida, é só chamar 💛",
    "Qualquer dúvida sobre produtos ou adaptações, estou por aqui 😊",
    "Qualquer coisa, pode me chamar aqui.",
    "Se quiser conversar ou tirar dúvidas, estou aqui 😊",
    "Fico à disposição pra qualquer dúvida 💛",
    "Se precisar de ajuda pra escolher algo, pode contar comigo.",
    "Conta comigo pra o que precisar 💛",
    "Visite nosso site e se precisar de ajuda pra escolher, estou aqui.",
    "Precisando de qualquer orientação, estou aqui 😊",
    "Pode me chamar quando quiser 💛",
]


# ══════════════════════════════════════════════════════════════════
# RESPOSTAS CONTEXTUAIS
# ══════════════════════════════════════════════════════════════════

RESPOSTAS_OBRIGADO = [
    "Que ótimo, fico feliz! 😊 Se precisar de qualquer orientação sobre nossos produtos, pode chamar aqui a qualquer hora.",
    "Obrigada você por nos acompanhar! 💛 É uma alegria saber que estamos juntos nessa.",
    "Que bom que gostou 😊 Qualquer dúvida, pode contar com a gente!",
    "Fico muito feliz com isso! Se quiser conhecer melhor nosso trabalho, acesse lojadoavo.com.br 😊",
    "Obrigada de volta! 💛 Se precisar de ajuda na escolha de algum produto, é só me chamar.",
    "Que ótimo! 😊 Fico à disposição sempre. Qualquer dúvida sobre segurança e autonomia 60+, pode contar com a equipe.",
    "Boa demais ouvir isso! 💛 Nosso propósito é exatamente esse — fazer a diferença pra quem precisa.",
    "Obrigada! 😊 Se surgir qualquer dúvida sobre adaptação ou produtos, estou por aqui.",
    "Fico feliz em poder ajudar! Qualquer coisa, pode contar com a Loja do Avô 💛",
    "Que bom! 😊 Se quiser bater um papo sobre alguma necessidade específica, pode chamar aqui.",
]

RESPOSTAS_DUVIDA_PRODUTO = [
    "Claro! Me conta um pouco mais sobre a necessidade — assim consigo te orientar melhor sobre qual produto faz mais sentido 😊",
    "Com prazer! Para te ajudar da melhor forma, você poderia me contar um pouco mais sobre a situação? 😊",
    "Ótima pergunta! Dependendo da necessidade, temos várias opções. Me conta mais sobre o que está buscando 💛",
    "Posso te ajudar sim! Nossa equipe conta com fisioterapeuta especialista em geriatria. Qual é a principal necessidade? 😊",
    "Vamos encontrar a melhor opção juntos! Me conta: é pra você ou para um familiar? E qual a principal dificuldade no dia a dia? 💛",
    "Com certeza! Temos especialistas que podem te orientar. Me fala mais sobre a situação pra eu te indicar o produto certo 😊",
    "Fico feliz em ajudar! A escolha certa faz muita diferença. Me conta: qual é a principal necessidade — mobilidade, segurança no banheiro, conforto? 💛",
    "Claro! Pra te ajudar bem, preciso entender melhor. A necessidade é pra prevenção de quedas, mobilidade ou adaptação do ambiente? 😊",
    "Com prazer em ajudar! Me conta um pouco mais — é uma necessidade imediata ou está planejando adaptar a casa? 💛",
    "Perfeito! Nossa equipe é especialista nisso. Me conta mais sobre a situação e te oriento na melhor escolha 😊",
]

RESPOSTAS_DUVIDA_ENTREGA = [
    "Entregamos para todo o Brasil! O prazo varia por região, mas fica disponível no momento da compra no site 😊",
    "Trabalhamos com entrega nacional! O frete e prazo aparecem automaticamente quando você coloca seu CEP no carrinho 💛",
    "Fazemos entrega em todo o território nacional 😊 O prazo exato aparece no checkout. Há alguma região específica que queira saber?",
    "Entregamos para qualquer lugar do Brasil! Assim que fizer o pedido, você recebe o código de rastreamento por e-mail 💛",
    "Claro! Entrega para todo o Brasil. O prazo aparece no site ao adicionar seu CEP. Normalmente entre 3 e 10 dias úteis dependendo da região 😊",
    "Sim, entregamos em todo o Brasil 😊 O valor do frete e o prazo ficam visíveis no carrinho antes de finalizar o pedido.",
    "Trabalhamos com entrega nacional 💛 O rastreamento é enviado por e-mail após o despacho. Tem alguma dúvida específica?",
    "Entrega em todo o território nacional! Ao colocar o CEP no site, você já vê o valor e prazo estimado 😊",
    "Sim! Entregamos para todo o Brasil. Dependendo da sua localidade, o prazo pode variar. Quer que eu te oriente a calcular? 💛",
    "Com certeza! Entrega nacional. O prazo fica disponível ao inserir o CEP na página do produto ou no carrinho 😊",
]

RESPOSTAS_DUVIDA_CUPOM = [
    "O cupom PRIMEIRACOMPRA10 dá 10% de desconto na sua primeira compra no site lojadoavo.com.br 😊 É só inserir no campo 'cupom' na finalização do pedido.",
    "Ótima pergunta! O cupom PRIMEIRACOMPRA10 é aplicado direto no carrinho — campo 'cupom de desconto' — e dá 10% OFF na primeira compra 💛",
    "O PRIMEIRACOMPRA10 dá 10% de desconto na primeira compra! Você aplica no checkout, no campo de cupom 😊 Tem validade por tempo limitado.",
    "Simples! No carrinho do site, tem um campo pra inserir o cupom. Coloca PRIMEIRACOMPRA10 e o desconto de 10% é aplicado automaticamente 💛",
    "O cupom PRIMEIRACOMPRA10 é válido pra qualquer produto na primeira compra do site 😊 Basta inserir no campo de cupom ao finalizar.",
    "Claro! PRIMEIRACOMPRA10 = 10% OFF na primeira compra. É só digitar no campo de cupom na etapa de pagamento 💛",
    "O cupom é exclusivo pra primeira compra e dá 10% de desconto 😊 Insere PRIMEIRACOMPRA10 no checkout do site lojadoavo.com.br.",
    "Funcionamento simples: adicione os produtos no carrinho, insira o cupom PRIMEIRACOMPRA10 e o desconto de 10% aparece automaticamente 💛",
    "PRIMEIRACOMPRA10 dá 10% de desconto e é válido para qualquer produto na primeira compra 😊 Aplique no campo de cupom no fechamento do pedido.",
    "Esse cupom dá 10% OFF na primeira compra — é pra qualquer produto do site 💛 Só não se acumula com outras promoções vigentes.",
]

RESPOSTAS_ADAPTACAO_RESIDENCIAL = [
    "Adaptação residencial é uma das nossas especialidades 😊 Barras de apoio, tapetes antiderrapantes, iluminação... Qual cômodo você quer adaptar primeiro?",
    "Ótimo assunto! A adaptação do lar pode fazer uma diferença enorme na segurança e autonomia. Me conta: qual é a maior preocupação hoje? Banheiro, escadas, quarto? 💛",
    "Com prazer em ajudar! Nosso time tem fisioterapeuta especialista em geriatria pra orientar as melhores soluções. Qual é o ambiente que mais precisa de atenção? 😊",
    "A prevenção de quedas começa em casa! Posso te orientar sobre os produtos mais indicados. Me conta: é pra seu lar ou de um familiar? 💛",
    "Adaptação residencial é algo que a gente leva muito a sério 😊 Quais são as principais dificuldades no dia a dia? Assim consigo te indicar o que realmente faz diferença.",
    "Boa decisão! Adaptar o ambiente reduz risco de quedas e aumenta a autonomia consideravelmente 💛 Me conta a situação pra eu orientar melhor.",
    "Temos soluções completas pra adaptação residencial 😊 Do banheiro à cozinha. Qual área está causando mais preocupação?",
    "Adaptar o lar é investir em segurança e qualidade de vida 💛 Me conta mais sobre a situação — quem mora lá, qual a mobilidade atual — e te oriento nos produtos certos.",
    "Perfeito! Esse é um dos nossos focos principais. Barras de apoio, tapetes, elevadores de assento... Me conta o que está buscando 😊",
    "Com certeza posso ajudar! Nossos especialistas orientam sobre a adaptação ideal para cada situação. Me fala mais sobre a necessidade 💛",
]

RESPOSTAS_MOBILIDADE_SEGURANCA = [
    "Mobilidade e segurança andam juntas 😊 Me conta mais sobre a situação — nível de atividade, dificuldades atuais — e te oriento nas melhores opções.",
    "Ótimo que está pensando nisso! Bengalas, andadores, muletas adaptadas... cada situação pede uma solução. Me conta mais 💛",
    "Nossa equipe tem fisioterapeuta especialista pra indicar exatamente o produto certo pra cada situação de mobilidade 😊 Me conta o que está enfrentando.",
    "Com prazer! Pra te ajudar bem, preciso entender: a dificuldade é de equilíbrio, dor, força nas pernas? Assim indico o produto ideal 💛",
    "Mobilidade é liberdade 😊 E temos produtos que fazem muita diferença nisso. Me conta a situação pra eu orientar direito.",
    "Cada caso de mobilidade é único! Me conta mais sobre a necessidade — faixa etária, tipo de dificuldade — e te indico o que funciona melhor 💛",
    "Perfeito! Segurança e mobilidade são o coração do nosso trabalho 😊 Me conta um pouco mais pra eu te dar a orientação certa.",
    "Temos soluções pra diferentes níveis de mobilidade — desde bengalas até cadeiras de rodas adaptadas 💛 Me conta o que está buscando.",
    "Ajudar com isso é nosso propósito! 😊 Me fala mais sobre a situação — quem precisa, qual a principal limitação — e te oriento com cuidado.",
    "Claro! Mobilidade bem apoiada muda completamente a qualidade de vida 💛 Me conta a situação e te ajudo a encontrar a melhor solução.",
]


# ══════════════════════════════════════════════════════════════════
# FUNÇÕES DE SELEÇÃO
# ══════════════════════════════════════════════════════════════════

def get_mensagem_principal() -> str:
    return random.choice(MENSAGENS_PRINCIPAIS)

def get_abertura() -> str:
    return random.choice(ABERTURAS)

def get_fechamento() -> str:
    return random.choice(FECHAMENTOS)

def get_resposta(contexto: str) -> str:
    mapa = {
        "obrigado": RESPOSTAS_OBRIGADO,
        "produto": RESPOSTAS_DUVIDA_PRODUTO,
        "entrega": RESPOSTAS_DUVIDA_ENTREGA,
        "cupom": RESPOSTAS_DUVIDA_CUPOM,
        "adaptacao": RESPOSTAS_ADAPTACAO_RESIDENCIAL,
        "mobilidade": RESPOSTAS_MOBILIDADE_SEGURANCA,
    }
    pool = mapa.get(contexto, RESPOSTAS_OBRIGADO)
    return random.choice(pool)


# ══════════════════════════════════════════════════════════════════
# DETECÇÃO DE INTENÇÃO
# ══════════════════════════════════════════════════════════════════

def detectar_intencao(texto: str) -> str:
    t = texto.lower()

    if any(p in t for p in ["obrigad", "valeu", "grat", "agradec"]):
        return "obrigado"

    if any(p in t for p in ["entrega", "frete", "prazo", "envio", "chega", "cep", "encomend"]):
        return "entrega"

    if any(p in t for p in ["cupom", "desconto", "promo", "10%", "código", "codigo"]):
        return "cupom"

    if any(p in t for p in ["adapta", "banheiro", "escada", "corrimão", "corrimao", "barra de apoio", "residenc"]):
        return "adaptacao"

    if any(p in t for p in ["andar", "mobilidade", "bengala", "andador", "cadeira", "equilíbrio", "equilibrio", "caminha", "cair", "queda", "dor"]):
        return "mobilidade"

    if any(p in t for p in ["produto", "tem", "vend", "comprar", "preço", "preco", "quanto custa", "valor", "catálogo", "catalogo"]):
        return "produto"

    return "produto"
