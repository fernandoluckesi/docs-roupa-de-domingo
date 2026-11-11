# Easter eggs — Roupa de Domingo

A loja vende humor ácido; os easter eggs falam na mesma voz. Cada um tem `code`,
gatilho, mensagem e, em alguns casos, recompensa real (cupom).

Toda descoberta vai para `POST /api/easter-eggs/:code/discover` e aparece em
`/trofeus`. São idempotentes: descobrir duas vezes não duplica nem re-premia.

## Catálogo

| #   | code                        | Gatilho                                   | Mensagem                                                                                   | Recompensa                                     |
| --- | --------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------ | ---------------------------------------------- |
| 1   | `KONAMI_CAOS`               | Konami code (↑↑↓↓←→←→BA) em qualquer tela | "Você digitou um código de 1986 para ganhar desconto em 2026. Respeito."                   | cupom `CAOS30` (30%)                           |
| 2   | `LOGO_SETE_CLIQUES`         | 7 cliques no logo                         | "Sete cliques. O logo não vai mudar de ideia sobre você."                                  | ativa "modo domingo de manhã" (tema esmaecido) |
| 3   | `PEDIDO_DE_DESCULPAS`       | digitar `desculpa` em qualquer tela       | "Aceitamos o pedido de desculpas que você nem devia ter feito. Toma 15%."                  | cupom `DESCULPA15`                             |
| 4   | `CARRINHO_VAZIO_TRES_VEZES` | abrir o carrinho vazio 3x                 | "Terceira vez olhando o vazio. Isso não é compra, é terapia — e a nossa é mais barata."    | —                                              |
| 6   | `RODAPE_CONFISSAO`          | hover de 5s no rodapé                     | "Ninguém lê rodapé. Então: a gente também não sabe o que está fazendo. Bem-vindo."         | —                                              |
| 7   | `QUARENTA_E_DOIS`           | quantidade 42 de um item                  | "42 unidades. A resposta para tudo, inclusive para 'quantas camisetas iguais são demais'." | frete grátis                                   |
| 8   | `QUATRO_ZERO_QUATRO`        | acessar uma rota inexistente              | "Esta página não existe. Igual aos seus planos de domingo à noite."                        | —                                              |
| 9   | `PRODUTO_SECRETO`           | descobrir 4 easter eggs                   | libera o produto secreto no catálogo                                                       | acesso ao produto `isSecret`                   |

### Pegadinha do desconto (só frontend, não conta troféu)

`components/easter-eggs/FakeDiscountPrank.tsx`:

1. Após 30s no site (fora de carrinho, checkout, pagamento, conta, login e das
   rotas silenciosas de `config/quietRoutes.ts`, e com o aviso de cookies já
   respondido), abre um modal "Você ganhou 20% de desconto!".
2. O botão "Quero" faz o modal fugir para outro ponto da tela (hover no desktop,
   toque no celular, Enter no teclado). "Não quero" e Esc fecham.
3. Depois de 12 fugas ou 16s, o modal fecha e aparece o snackbar
   "Como é engraçado te fazer de trouxa."
4. 20s depois, um modal sem botões: "Achou mesmo que iria ganhar desconto assim
   fácil? ... ache o código secreto olhando para o teto." Após 6s troca para
   "Você olhou mesmo? haha" e some num fade de 3s. Não bloqueia cliques.

Não existe código: é só a piada. Aparece **uma única vez por navegador**
(`rd:fakeDiscountShown` no localStorage, categoria Essencial: só evita repetir uma
janela já vista e não identifica ninguém). Só começa a contar os 30s depois do
aviso de humor respondido.

### Aviso de humor (entrada do site)

`components/easter-eggs/HumorWarning.tsx`: na primeira visita do navegador, em
qualquer tela menos as rotas silenciosas (`/segredo`, destino do QR Code, e
`/tchau`), um modal avisa: "Este é um site de humor, contém sarcasmos, ofensas e
piadas de qualidade duvidosa".

- "Não sou gato gago pra ficar de "mimimi"": grava `rd:humorWarningAccepted`
  (localStorage, Essencial) e libera o site. O banner de cookies e a pegadinha do
  desconto esperam essa resposta.
- "Sou pamonha mole, quero sair 😭": leva para `/tchau` (`pages/Goodbye.tsx`,
  conteúdo provisório). Não grava nada: se a pessoa voltar, vê o aviso de novo.

### Backend também tem

- Header `X-Powered-By-Domingo` em toda resposta, com frases rotativas.
- `GET /api/teapot` → HTTP 418 "Sou um bule. Não faço café, nem milagre."
- `GET /api/docs` com descrição em tom ácido.

## Implementação

**Frontend** — `EasterEggContext` + hooks:

| Hook             | Usado por |
| ---------------- | --------- |
| `useKonamiCode`  | #1        |
| `useClickStreak` | #2        |
| `useTypedPhrase` | #3        |
| `useLongHover`   | #6        |

Contadores de sessão (#4) ficam no `sessionStorage`; #7 é verificado no
`QuantityStepper`; #5 dispara uma vez no mount do `App`.

Ao disparar: `discover(code)` → toast temático → atualiza troféus → se houver
cupom, mostra o código e já o aplica no carrinho quando possível.

**Backend** — easter eggs vêm do seed. `GET /api/easter-eggs` só devolve
`message` dos já descobertos; os outros aparecem como bloqueados com `hint`.
Isso evita spoiler via DevTools na aba Network.

## Regras de bom gosto

1. Easter egg nunca bloqueia a compra nem quebra o fluxo.
2. Nada pisca, grita ou toca som sem o usuário pedir.
3. Humor ácido sobre a própria marca e sobre situações, nunca sobre o usuário de forma ofensiva.
4. Tudo é reversível (modo caos e modo domingo têm botão de sair).
5. `prefers-reduced-motion` desliga os efeitos visuais.
