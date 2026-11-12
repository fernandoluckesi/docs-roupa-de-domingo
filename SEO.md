# SEO e medição — Roupa de Domingo

O que existe e como ligar cada peça. Tudo que depende de conta externa é opcional:
sem a variável, a peça fica desligada e o site funciona igual.

## Já funcionando, sem configuração

| Item | Onde |
| --- | --- |
| `sitemap.xml` dinâmico (páginas + produtos ativos com imagem) | backend `modules/seo` → nginx `/sitemap.xml` |
| `robots.txt` (privadas bloqueadas, robôs de IA declarados por nome) | frontend `public/robots.txt` |
| `llms.txt` (resumo da loja para assistentes de IA) | frontend `public/llms.txt` |
| Title, meta description, canonical, Open Graph, Twitter Card por rota | `RouteSeo`/`Seo` (navegador) + backend `/api/seo/head` via SSI (robôs sem JS) |
| JSON-LD: Organization + WebSite (home), Product com preço e avaliação, Breadcrumb | backend `seo.module.ts`, frontend `Breadcrumb.tsx` |
| `noindex` em conta, checkout, carrinho, pagamento, login, troféus, `/segredo`, `/tchau` | `RouteSeo.tsx` e `PRIVATE_PREFIXES` do backend |

Palavras-chave principais nos títulos e descrições: "camisetas engraçadas", "humor ácido",
"moletons", "canecas", "presente criativo". Ao mudar o texto de uma rota pública, mude nos
dois lugares (`RouteSeo.tsx` e `STATIC_PAGES` no backend) e mantenha a descrição com até
~155 caracteres (o Google corta o resto).

## Google Search Console (passo manual)

1. Em search.google.com/search-console, adicione a propriedade **Domínio** `roupadedomingo.com.br`.
2. Copie o registro TXT `google-site-verification=...` e crie no Cloudflare (DNS → TXT, nome `@`).
3. Depois de verificado, em **Sitemaps** envie `https://roupadedomingo.com.br/sitemap.xml`.

Alternativa sem DNS (propriedade "Prefixo do URL"): copie só o código da meta tag para a
variável `VITE_GOOGLE_SITE_VERIFICATION` do serviço frontend no Railway. O mesmo vale para o
Bing Webmaster Tools com `VITE_BING_SITE_VERIFICATION` (o Bing também importa do Search Console).

## Google Analytics 4 e Meta Pixel

Variáveis do serviço **frontend** no Railway (são lidas no build; após criar, faça redeploy):

| Variável | Formato | Categoria de cookie |
| --- | --- | --- |
| `VITE_GA_MEASUREMENT_ID` | `G-XXXXXXXXXX` | Estatísticas |
| `VITE_META_PIXEL_ID` | só dígitos | Marketing |

Comportamento (`src/lib/analytics.ts`, `components/analytics/AnalyticsLoader.tsx`):

- Nenhum script do Google ou da Meta é baixado antes do consentimento da categoria.
- Revogar desliga o envio na hora e apaga `_ga*`, `_fbp`, `_fbc`.
- Eventos: `page_view`/`PageView` a cada rota, `view_item`/`ViewContent` no produto,
  `add_to_cart`/`AddToCart`, `begin_checkout`/`InitiateCheckout` e `purchase`/`Purchase`
  (uma vez por pedido pago). Só produto, valor e número do pedido: nunca nome, e-mail ou CPF.
- A CSP (`nginx/security-headers.inc`) libera apenas os domínios dessas duas ferramentas.

Ao ligar qualquer uma, as políticas de cookies e de privacidade passam a citá-la e mudam de
versão (`2026-11-12`), então o aviso de cookies reaparece para todos escolherem de novo.
