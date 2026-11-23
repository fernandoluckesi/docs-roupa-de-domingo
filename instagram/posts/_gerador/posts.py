# -*- coding: utf-8 -*-
"""Dados dos 20 posts + 1 criativo para impulsionar.

Cada post vira uma imagem 1080x1350 (feed 4:5) e um bloco no legendas.txt.
Templates: produto, frase, chat, lista, grid.
Use <em>...</em> nos títulos para destacar em verde-limão.
"""

P = "products/"  # relativo a frontend-roupa-de-domingo/public/

POSTS = [
    # ---------------------------------------------------------------- DIA 01
    dict(
        dia=1, data="2026-11-23", slug="apresentacao-marca", template="grid",
        chip="PRAZER, DESPRAZER",
        titulo="Roupa que diz <em>o que você não diz</em> em voz alta.",
        sub="Camisetas, moletons, canecas e garrafas com humor de péssima qualidade.",
        imgs=[P+"camiseta-hoje-eu-so-existo-f-preta.jpg", P+"caneca-te-ouvi-so-nao-escutei-branca.jpg",
              P+"garrafa-criticar-e-facil-queta-preta.jpg", P+"camiseta-na-minha-maquina-funciona-m-preta.jpg"],
        rodape="Siga antes que a gente perca a graça.",
        produto="Catálogo geral",
        legenda="""Oi. Somos a Roupa de Domingo. 👋

Fazemos camisetas, moletons, canecas e garrafas para quem já desistiu de explicar os próprios sentimentos com palavras próprias.

Aqui você encontra:
✅ Ironia de alta qualidade
✅ Algodão honesto para frases desonestas
❌ Bom senso (esgotado desde sempre)

Segue o perfil e ativa o sininho. Ou não. A gente finge que não liga. 🙃

👉 Catálogo no link da bio.

#roupadedomingo #camisetaengracada #humoracido #sarcasmo #camisetacomfrase""",
    ),
    # ---------------------------------------------------------------- DIA 02
    dict(
        dia=2, data="2026-11-24", slug="na-minha-maquina-funciona", template="produto",
        chip="PARA DEVS E MENTIROSOS",
        titulo="O bug está em produção.<br>A desculpa está <em>na camiseta.</em>",
        img=P+"camiseta-na-minha-maquina-funciona-m-preta.jpg",
        preco="R$ 99,90",
        rodape="Testada em produção. Funcionou na nossa máquina.",
        produto="Camiseta Na minha máquina funciona (preta)",
        legenda="""Na minha máquina funciona. 💻🔥

A frase mais dita da história da tecnologia agora pode ser dita sem abrir a boca. Economia de saliva e de responsabilidade.

Ideal para:
• Daily em que você não fez nada
• Deploy de sexta-feira às 17h58
• Explicar pro cliente que "é cache"

Marca aquele colega que culpa o ambiente de homologação. Ele sabe o que fez. 👇

🛒 R$ 99,90 no link da bio. Funciona no seu carrinho também (testamos).

#programador #dev #devhumor #namaquinafunciona #roupadedomingo #camisetaengracada""",
    ),
    # ---------------------------------------------------------------- DIA 03
    dict(
        dia=3, data="2026-11-25", slug="te-ouvi-so-nao-escutei", template="chat",
        chip="COMUNICAÇÃO NÃO-VIOLENTA (NÃO)",
        msgs=[("eles", "Você ouviu o que eu falei?"), ("eles", "Oi??"), ("eu", "Te ouvi.<br>Só não escutei. 🙂")],
        titulo="Agora também em <em>caneca</em>, pra você não precisar responder.",
        img=P+"caneca-te-ouvi-so-nao-escutei-branca.jpg",
        preco="R$ 64,90",
        produto="Caneca Te ouvi. Só não escutei (branca)",
        legenda="""Te ouvi. Só não escutei. ☕

Para aquela reunião que podia ser um e-mail, para aquele áudio de 4 minutos e para aquela pessoa que começa com "não quero ser chato, mas...".

A caneca responde por você enquanto você finge que está anotando.

Marca quem manda áudio de 4 minutos. A gente vai ouvir. Escutar, não. 👇

☕ R$ 64,90 no link da bio.

#caneca #canecapersonalizada #canecaengracada #sarcasmo #roupadedomingo #humor""",
    ),
    # ---------------------------------------------------------------- DIA 04
    dict(
        dia=4, data="2026-11-26", slug="esquenta-black-friday-paciencia", template="lista",
        chip="ESQUENTA BLACK FRIDAY",
        titulo="O que vai estar <em>90% off</em> nesta Black Friday:",
        itens=["Sua paciência", "Sua paciência na fila do site", "Sua paciência com o tio do grupo da família", "Sua paciência (já falamos?)"],
        img=P+"camiseta-paciencia-coice-de-porco-m-preta.jpg",
        rodape="Estampa: minha paciência está mais curta que coice de porco.",
        nota="Desconto real na paciência: <em style=\"font-style:normal;color:var(--lime)\">100%.</em>",
        produto="Camiseta Minha paciência está mais curta que coice de porco (preta)",
        legenda="""Esquenta Black Friday: a única coisa garantida com desconto é a sua paciência. 🫠

Nossa camiseta já vem com a mensagem pronta para todo mundo que te perguntar "qual é o cupom?" pela 15ª vez.

"Minha paciência está mais curta que coice de porco." 🐷

Salva este post para usar de resposta pronta nos próximos dias. 📌

🛒 Link na bio. Amanhã tem mais. Ou menos. Ainda não decidimos.

#blackfriday #esquentablackfriday #paciencia #camisetaengracada #roupadedomingo #humoracido""",
    ),
    # ---------------------------------------------------------------- DIA 05
    dict(
        dia=5, data="2026-11-27", slug="black-friday-honesta", template="grid",
        chip="BLACK FRIDAY HONESTA",
        titulo="Black Friday:<br>nossas piadas continuam <em>ruins pelo mesmo preço.</em>",
        sub="Frete grátis acima de R$ 249. Pelo menos isso é de graça.",
        imgs=[P+"camiseta-evite-acidentes-faca-de-proposito-m-preta.jpg", P+"caneca-aceita-que-doi-menos-branca.jpg",
              P+"moletom-socialmente-indisponivel-preta.jpg", P+"camiseta-te-ouvi-so-nao-escutei-f-preta.jpg"],
        rodape="Sem metade do dobro. Sem contador falso. Sem vergonha também.",
        produto="Catálogo geral (Black Friday)",
        legenda="""BLACK FRIDAY HONESTA. 🖤

Enquanto as lojas sobem o preço em outubro para "baixar" em novembro, a gente decidiu fazer algo revolucionário: não mentir.

O que tem:
✅ Frete grátis acima de R$ 249
✅ As mesmas piadas ruins de sempre
✅ Estampa sob demanda, feita só pra você

O que não tem:
❌ "Metade do dobro"
❌ Cronômetro falso dizendo que acaba em 3 minutos
❌ Juízo

Manda pro amigo que vai gastar 4 horas comparando preço para economizar R$ 2. 👇

🛒 Link na bio.

#blackfriday #blackfriday2026 #blackfridayhonesta #roupadedomingo #camisetaengracada #fretegratis""",
    ),
    # ---------------------------------------------------------------- DIA 06
    dict(
        dia=6, data="2026-11-28", slug="hoje-eu-so-existo", template="frase",
        chip="PLANO PARA O SÁBADO",
        frase="HOJE EU SÓ EXISTO <em>(E&nbsp;OLHE&nbsp;LÁ)</em>",
        img=P+"camiseta-hoje-eu-so-existo-f-preta.jpg",
        rodape="Tem em camiseta e em moletom. Para existir com conforto.",
        produto="Camiseta Hoje eu só existo (e olhe lá) (preta, modelo feminino)",
        legenda="""Planos para hoje:
☐ Academia
☐ Arrumar a casa
☐ Responder as mensagens
☑ Existir (e olhe lá)

Sábado é dia de fazer o mínimo com orgulho. A camiseta avisa por você, assim você nem precisa existir em voz alta. 😮‍💨

Comenta "EXISTO" se esse é seu único compromisso do fim de semana. 👇

🛒 Camiseta e moletom no link da bio.

#sabado #fimdesemana #preguica #camisetaengracada #roupadedomingo #mood""",
    ),
    # ---------------------------------------------------------------- DIA 07
    dict(
        dia=7, data="2026-11-29", slug="mais-inutil-que-feriado-no-domingo", template="produto",
        chip="DOMINGO, NATURALMENTE",
        titulo="Mais inútil que feriado no domingo.<br><em>Mas pelo menos com estilo.</em>",
        img=P+"camiseta-mais-inutil-que-feriado-no-domingo-m-preta.jpg",
        preco="R$ 99,90",
        rodape="A marca chama Roupa de Domingo. Era questão de tempo.",
        produto="Camiseta Mais inútil que feriado no domingo (preta)",
        legenda="""Existe dor maior do que feriado caindo no domingo? 😩

Existe: ser tão inútil quanto ele. Mas pelo menos agora você pode assumir isso com uma camiseta de algodão.

A gente se chama Roupa de Domingo. Era questão de tempo até fazer essa piada. Demorou. Igual você para sair da cama hoje.

Marca aquela pessoa que é o feriado no domingo do grupo. 👇

🛒 R$ 99,90 no link da bio.

#domingo #feriado #camisetaengracada #roupadedomingo #sarcasmo #humor""",
    ),
    # ---------------------------------------------------------------- DIA 08
    dict(
        dia=8, data="2026-11-30", slug="acordei-disposto", template="frase",
        chip="SEGUNDA-FEIRA, INFELIZMENTE",
        frase="ACORDEI DISPOSTO <em>(A VOLTAR A DORMIR)</em>",
        img=P+"moletom-acordei-disposto-preta.jpg",
        rodape="Moletom. Porque segunda-feira também é frio por dentro.",
        produto="Moletom Acordei disposto (preto)",
        legenda="""Bom dia para quem acordou disposto. ☀️

Disposto a voltar a dormir. 😴

O moletom que entende sua segunda-feira melhor do que seu chefe. Quentinho, confortável e honesto sobre suas reais intenções.

Comenta 😴 se você já está contando as horas para deitar de novo.

🛒 Moletom no link da bio. Peça hoje, use com vergonha amanhã.

#segundafeira #segunda #moletom #preguica #roupadedomingo #camisetaengracada""",
    ),
    # ---------------------------------------------------------------- DIA 09
    dict(
        dia=9, data="2026-12-01", slug="aceita-que-doi-menos", template="produto",
        chip="BEM-VINDO, DEZEMBRO",
        titulo="Faltam 30 dias para o ano acabar e você não fez nada.<br><em>Aceita que dói menos.</em>",
        img=P+"caneca-aceita-que-doi-menos-branca.jpg",
        preco="R$ 64,90",
        rodape="Spoiler da caneca: dói igual.",
        produto="Caneca Aceita que dói menos (dói igual) (branca)",
        legenda="""Dezembro chegou. 📅

Aquela lista de metas de janeiro está te olhando. A academia que você pagou e não foi também. O curso de inglês, idem.

Respira fundo, pega um café e aceita que dói menos.

(Spoiler: dói igual. Está escrito na caneca. Somos honestos.)

Marca alguém que vai prometer "ano que vem eu começo". 👇

☕ R$ 64,90 no link da bio.

#dezembro #fimdeano #metas #caneca #roupadedomingo #aceitaquedoimenos""",
    ),
    # ---------------------------------------------------------------- DIA 10
    dict(
        dia=10, data="2026-12-02", slug="voto-secreto-opiniao-nao", template="frase",
        chip="CEIA DE NATAL, AQUECIMENTO",
        frase="MEU VOTO É SECRETO. <em>MINHA OPINIÃO NÃO.</em>",
        img=P+"camiseta-voto-e-secreto-opiniao-nao-m-preta.jpg",
        rodape="Para a ceia com a família inteira. Boa sorte.",
        produto="Camiseta Meu voto é secreto. Minha opinião não. (preta)",
        legenda="""Faltam 3 semanas para a ceia de Natal. 🎄

Você já sabe que vai ter discussão. Seu tio já sabe. A tia do pavê já sabe.

Então vai preparado: com uma camiseta que avisa logo na entrada que você não vai ficar calado.

"Meu voto é secreto. Minha opinião não." 🗣️

Marca o parente que vai começar a discussão antes do peru sair do forno. 👇

🛒 R$ 99,90 no link da bio. Chega antes da briga.

#natal #ceiadenatal #familia #camisetaengracada #roupadedomingo #opiniao""",
    ),
    # ---------------------------------------------------------------- DIA 11
    dict(
        dia=11, data="2026-12-03", slug="easter-eggs-na-loja", template="easter",
        chip="DESAFIO (QUE VOCÊ VAI PERDER)",
        titulo="Existem <em>8 easter eggs</em> escondidos na nossa loja.",
        sub="Alguns liberam cupom de verdade. Nenhum aparece no menu.",
        dica="↑ ↑ ↓ ↓ ← → ← → B A",
        rodape="Você não vai achar nenhum. Prove o contrário.",
        produto="Site (easter eggs / troféus)",
        legenda="""DESAFIO: existem 8 easter eggs escondidos no nosso site. 🥚🕵️

Alguns liberam cupom de verdade. Nenhum aparece no menu. A gente não vai contar onde estão, porque somos uma marca que respeita a sua inteligência (mais ou menos).

Dica gratuita: códigos de videogame dos anos 80 ainda funcionam em 2026. 🎮

Achou algum? Comenta "ACHEI" e o número de troféus. Mentir também vale, a gente nem confere. 👇

🔗 Link na bio. Boa sorte. Você vai precisar.

#easteregg #desafio #konamicode #anos80 #roupadedomingo #gamer""",
    ),
    # ---------------------------------------------------------------- DIA 12
    dict(
        dia=12, data="2026-12-04", slug="evite-acidentes", template="frase",
        chip="CONSELHO PROFISSIONAL",
        frase="EVITE ACIDENTES. <em>FAÇA DE PROPÓSITO.</em>",
        img=P+"camiseta-evite-acidentes-faca-de-proposito-m-preta.jpg",
        rodape="Não nos responsabilizamos pelo que você vai fazer com esse conselho.",
        produto="Camiseta Evite acidentes. Faça de propósito. (preta)",
        legenda="""Dica de segurança da Roupa de Domingo: ⚠️

Evite acidentes.
Faça de propósito.

Simples. Eficaz. Juridicamente questionável.

Uma das mais vendidas da loja, porque todo mundo conhece alguém que vive assim (e às vezes esse alguém é você).

Sexta-feira, só um lembrete. 😇

Marca quem faz tudo "sem querer querendo". 👇

🛒 R$ 99,90 no link da bio.

#sextafeira #sexta #sarcasmo #camisetaengracada #roupadedomingo #maisvendidos""",
    ),
    # ---------------------------------------------------------------- DIA 13
    dict(
        dia=13, data="2026-12-05", slug="criticar-e-facil-garrafa", template="produto",
        chip="HIDRATAÇÃO COM OPINIÃO",
        titulo="Criticar é fácil.<br><em>Quero ver fazer pior.</em>",
        img=P+"garrafa-criticar-e-facil-queta-preta.jpg",
        rodape="Mantém a água gelada e o sarcasmo também.",
        produto="Garrafa Criticar é fácil, quero ver fazer pior (preta)",
        legenda="""Para aquela pessoa que critica tudo e não faz nada: 💧

"Criticar é fácil. Quero ver fazer pior."

A garrafa que mantém a água gelada, o sarcasmo também, e ainda dá uma indireta na academia, no trabalho e no churrasco de domingo.

Hidratação com opinião. Seu nutricionista aprova (a gente não perguntou).

Marca aquele crítico de plantão. 👇

🛒 Garrafas no link da bio.

#garrafa #garrafatermica #hidratacao #sarcasmo #roupadedomingo #presente""",
    ),
    # ---------------------------------------------------------------- DIA 14
    dict(
        dia=14, data="2026-12-06", slug="mimimi-gato-gago", template="frase",
        chip="DOMINGO SEM DRAMA",
        frase="SE EU GOSTASSE DE MIMIMI <em>EU COMPRAVA UM GATO GAGO.</em>", fs=80,
        img=P+"camiseta-se-eu-gostasse-de-mimimi-m-preta.jpg",
        rodape="Nenhum gato foi gago durante a produção desta estampa.",
        produto="Camiseta Se eu gostasse de mimimi eu comprava um gato gago (preta)",
        legenda="""Se eu gostasse de mimimi, eu comprava um gato gago. 🐱

Infelizmente não gosto, então comprei a camiseta.

Para usar no domingo em família, quando alguém começar a reclamar da comida que você nem fez.

(Gatos são ótimos. O mimimi não. Por favor, não mandem DM.)

Comenta 🐱 se você conhece alguém que precisa receber essa de presente. 👇

🛒 R$ 99,90 no link da bio.

#mimimi #gato #domingo #camisetaengracada #roupadedomingo #humor""",
    ),
    # ---------------------------------------------------------------- DIA 15
    dict(
        dia=15, data="2026-12-07", slug="amigo-secreto", template="lista",
        chip="GUIA DO AMIGO SECRETO",
        titulo="Presentes de amigo secreto <em>por nível de intimidade:</em>",
        itens=["Desconhecido → meia", "Colega de trabalho → chocolate", "Amigo → vale-presente", "Amigo de verdade → uma camiseta que ofende ele com carinho"],
        img=P+"camiseta-kkkkkkkkk-chorei-m-preta.jpg",
        rodape="Também temos canecas para quem você odeia levemente.",
        nota="Seja o amigo de verdade. <em style=\"font-style:normal;color:var(--lime)\">Ofenda com carinho.</em>",
        produto="Camiseta KKKKKKKKK KKKKKKKKK (CHOREI) (preta) + catálogo para presente",
        legenda="""Temporada de amigo secreto aberta. 🎁

Você sabe o que acontece todo ano: alguém dá meia, alguém dá chocolate derretido e alguém fala "não sabia o que comprar, então...".

Seja a pessoa que dá o presente que todo mundo quer ver aberto. Ofensivo na medida certa. Com carinho, mas sem afeto excessivo.

Camisetas, canecas, moletons e garrafas. Tem para o colega que você odeia levemente. 😌

Marca o grupo do amigo secreto. 👇

🛒 Link na bio. Estampamos sob demanda, então não deixe para a véspera.

#amigosecreto #amigooculto #presente #presentedenatal #roupadedomingo #natal""",
    ),
    # ---------------------------------------------------------------- DIA 16
    dict(
        dia=16, data="2026-12-08", slug="natural-quanto-luz-do-poste", template="produto",
        chip="BELEZA SEM FILTRO (COM FILTRO)",
        titulo="Sem filtro, sem maquiagem, sem edição.<br><em>Tão natural quanto a luz do poste.</em>",
        img=P+"camiseta-natural-quanto-luz-do-poste-f-preta.jpg",
        preco="R$ 99,90",
        rodape="100% algodão. 0% naturalidade.",
        produto="Camiseta Tão natural quanto a luz do poste (preta, modelo feminino)",
        legenda="""Eu acordei assim. ✨

Assim: com 3 filtros, ring light, ângulo de 45° e luz de poste.

Para quem é 100% natural (tipo a luz do poste) e assume isso com dignidade e algodão fio penteado.

Marca a amiga que sempre diz "nem me arrumei" e está pronta para o tapete vermelho. 👇

🛒 R$ 99,90 no link da bio. Foto sem edição. Mentira.

#semfiltro #natural #selfie #camisetaengracada #roupadedomingo #humor""",
    ),
    # ---------------------------------------------------------------- DIA 17
    dict(
        dia=17, data="2026-12-09", slug="mais-perdido-que-azeitona", template="frase",
        chip="RETROSPECTIVA 2026",
        frase="MAIS PERDIDO QUE <em>AZEITONA NA BOCA DE BANGUELO</em>",
        img=P+"camiseta-mais-perdido-que-azeitona-na-boca-de-banguelo-m-preta.jpg",
        rodape="Resumo do seu 2026 em uma estampa.",
        produto="Camiseta Mais perdido que azeitona na boca de banguelo (preta)",
        legenda="""Retrospectiva 2026 em uma frase: 🫒

Janeiro: "Esse ano vai!"
Junho: "Ainda dá tempo."
Dezembro: mais perdido que azeitona na boca de banguelo.

Se identificou? Não se preocupe, você não está sozinho. Está perdido, mas acompanhado.

Comenta 🫒 se esse foi o seu ano também. 👇

🛒 R$ 99,90 no link da bio. Pelo menos a compra você vai saber onde está (tem rastreio).

#retrospectiva #retrospectiva2026 #fimdeano #camisetaengracada #roupadedomingo #sarcasmo""",
    ),
    # ---------------------------------------------------------------- DIA 18
    dict(
        dia=18, data="2026-12-10", slug="nunca-uma-melhoria", template="frase",
        chip="ATUALIZAÇÃO DISPONÍVEL",
        frase="NUNCA UMA MELHORIA. <em>SEMPRE UMA PIORA.</em>",
        img=P+"camiseta-nunca-uma-melhoria-m-preta.jpg",
        rodape="Compatível com: seu celular, seu chefe, seu ex.",
        produto="Camiseta Nunca uma melhoria, sempre uma piora (preta)",
        legenda="""Nova atualização disponível. 📲

O que mudou:
• Bateria dura menos
• O botão mudou de lugar
• Agora tem IA no app da calculadora
• Nunca uma melhoria. Sempre uma piora.

A camiseta oficial de quem já desistiu de esperar que as coisas melhorem. Compatível com seu celular, seu chefe e seu ex.

Marca alguém que ainda acredita em "melhorias de desempenho". 👇

🛒 R$ 99,90 no link da bio.

#atualizacao #tecnologia #pessimismo #camisetaengracada #roupadedomingo #sarcasmo""",
    ),
    # ---------------------------------------------------------------- DIA 19
    dict(
        dia=19, data="2026-12-11", slug="socialmente-indisponivel", template="produto",
        chip="CONFRATERNIZAÇÃO DA FIRMA",
        titulo="Para o frio <em>e para esconder o rosto</em> depois da confraternização.",
        img=P+"moletom-socialmente-indisponivel-preta.jpg",
        rodape="Socialmente indisponível. Emocionalmente também.",
        produto="Moletom Socialmente indisponível (preto)",
        legenda="""Sexta-feira de confraternização da firma. 🥂

Você vai:
1. Prometer que vai embora cedo
2. Ficar até o fim
3. Fazer um discurso que ninguém pediu
4. Precisar deste moletom na segunda-feira

"Socialmente indisponível." O moletom para o frio e para esconder o rosto depois do que você fez (ou postou).

Marca o colega que vai precisar dele. 👇

🛒 Moletons no link da bio.

#confraternizacao #firma #festadefimdeano #moletom #roupadedomingo #sextafeira""",
    ),
    # ---------------------------------------------------------------- DIA 20
    dict(
        dia=20, data="2026-12-12", slug="presente-de-natal-ultimo-aviso", template="grid",
        chip="ÚLTIMO AVISO (QUE VOCÊ VAI IGNORAR)",
        titulo="Natal é dia 25.<br><em>Você vai deixar para o dia 24.</em>",
        sub="Estampamos sob demanda. Presente bom precisa de tempo. Você não tem.",
        imgs=[P+"camiseta-a-ultima-palavra-e-minha-em-casa-m-preta.jpg", P+"caneca-te-ouvi-so-nao-escutei-branca.jpg",
              P+"moletom-hoje-eu-so-existo-preta.jpg", P+"garrafa-criticar-e-facil-queta-preta.jpg"],
        rodape="Peça hoje. Chega antes do arrependimento.",
        produto="Catálogo geral (presentes de Natal)",
        legenda="""Último aviso de Natal. 🎄⏰

Que você vai ignorar, a gente sabe.

Mas fica registrado: cada peça é estampada sob demanda, só para você. Isso quer dizer que fica bonita, mas não sai do nada. Quem deixa para o dia 24 dá "vale-presente impresso em sulfite".

Presente para:
👕 O pai que tem a última palavra em casa (sim, senhora)
☕ A mãe que te ouve, mas não escuta
🧥 O irmão que só existe
💧 O tio crítico de plantão

Consulte o prazo de entrega para o seu CEP direto no site. 📦

Marca quem vai comprar presente na rodoviária no dia 24. 👇

🛒 Link na bio.

#natal #presentedenatal #natal2026 #presente #roupadedomingo #camisetaengracada""",
    ),
]

# --------------------------------------------------------------------- IMPULSIONAR
# Seguro para anúncios: sem palavrão, sem política, sem piada de aparência.
ANUNCIO = dict(
    dia=0, data="2026-11-23", slug="roupa-que-diz", template="anuncio",
    chip="+130 PRODUTOS COM INDIRETA",
    titulo="Roupa que diz <em>o que você não diz</em> em voz alta.",
    sub="Camisetas, moletons, canecas e garrafas com humor ácido. Estampadas sob demanda, só para você.",
    imgs=[P+"camiseta-hoje-eu-so-existo-f-preta.jpg", P+"camiseta-na-minha-maquina-funciona-m-preta.jpg",
          P+"caneca-te-ouvi-so-nao-escutei-branca.jpg"],
    selos=["Frete grátis acima de R$ 249", "Pix ou até 12x", "Estampa sob demanda"],
    cta="Escolha a sua indireta →",
    produto="Catálogo geral (anúncio)",
    legenda="""Você não precisa falar. A camiseta fala. 😶👕

Na Roupa de Domingo, cada estampa é uma indireta que você nunca teve coragem de mandar:

👕 "Hoje eu só existo (e olhe lá)"
💻 "Na minha máquina funciona"
☕ "Te ouvi. Só não escutei."

Mais de 130 produtos entre camisetas, moletons, canecas e garrafas. Feitas sob demanda, só para você (e para quem vai ler suas costas).

✅ Frete grátis acima de R$ 249
✅ Pix ou cartão em até 12x
✅ Algodão honesto para frases desonestas

👉 Toque em "Comprar agora" e escolha a sua indireta. Ela não vai se escolher sozinha (ainda).

#roupadedomingo #camisetaengracada #camisetacomfrase #humor #presente""",
)
