# Análise de acessos e vendas

Área **Análise** do backoffice (`/analytics`), no formato do Google Analytics, com dados coletados pela
própria loja: sem Google Analytics, sem cookie e sem plataforma de terceiros. Gratuito e sem limite.

## Relatórios

| Relatório | O que mostra |
| --- | --- |
| **Resumo** | Usuários ativos, novos usuários, tempo médio de engajamento, visualizações, vendas e receita, com a variação contra o período anterior e o gráfico diário (linha tracejada = período anterior). Também sessões, taxa de engajamento, rejeição, visualizações por sessão, conversão, e os cartões de canais, páginas, cidades, dispositivos e tempo real. |
| **Tempo real** | Usuários nos últimos 30 minutos, por minuto, páginas abertas, origem, cidade e eventos. Atualiza a cada 15 s. |
| **Aquisição** | Canais (QR Code, Instagram, TikTok, Google, direto...) com sessões, engajamento, pedidos, vendas, receita e conversão; QR Code por local impresso; campanhas (UTM); gerador de link para divulgar; download do QR das costas. |
| **Engajamento** | Páginas e telas (visualizações, usuários, tempo médio na página, entradas, taxa de saída), páginas de entrada (sessões, engajamento, rejeição, pedidos), buscas no site e eventos. |
| **Caminhos** | Exploração de caminhos: a partir do início da sessão ou de qualquer página, para onde as pessoas foram em até 4 passos, e as jornadas mais comuns. |
| **Monetização** | Funil de compra por sessão (viu produto → carrinho → checkout → pedido → pago), funil por canal e produtos (visualizações, adições ao carrinho, itens vendidos, receita). |
| **Local e tecnologia** | País, estado e cidade; novos x recorrentes; dispositivo, sistema, navegador, resolução da tela e idioma. |

Todos os relatórios têm período no topo (hoje, ontem, 7, 28 e 90 dias, este mês, mês passado ou datas
personalizadas). O período fica na URL, então o link pode ser compartilhado com a equipe.

## Definições (iguais às do Google Analytics 4)

| Termo | Definição |
| --- | --- |
| Usuário | navegador diferente (o mesmo celular voltando = 1 usuário) |
| Sessão | visita; termina após 30 min sem atividade ou quando a pessoa chega por outra origem |
| Sessão engajada | ficou 10 s ou mais com a página visível, ou viu 2 páginas ou mais |
| Taxa de rejeição | sessões não engajadas ÷ sessões |
| Tempo de engajamento | só conta com a aba visível (aba em segundo plano não conta) |
| Venda | pedido pago (pago, em produção, enviado, entregue) |
| Conversão | vendas ÷ usuários |
| Atribuição da venda | última origem não direta da pessoa nos 30 dias antes da compra |

## Como a coleta funciona

A loja envia para `POST /api/analytics/collect`:

- `page_view` a cada troca de página (na primeira, a origem: UTM, QR Code, anúncio, site de origem);
- `engagement`: o tempo com a página visível, ao trocar de página, ao sair e a cada 30 s;
- `event`: `view_item`, `add_to_cart`, `begin_checkout`, `search`. O `order_created` é gravado pelo
  próprio backend no checkout.

Classificação da origem, nesta ordem: QR Code (`/segredo`, com o local em `?q=`) → UTM → id de clique de
anúncio (`fbclid`, `gclid`, `ttclid`) → domínio de origem → direto. Robôs e pré-visualização de link
(WhatsApp, Facebook, buscadores) não contam.

## Cidade (localização aproximada)

O IP é usado só na hora para achar país, estado e cidade, e **não é guardado**. Duas opções gratuitas:

1. **Cloudflare (recomendado, o domínio já usa):** no painel do Cloudflare, *Rules → Settings / Managed
   Transforms → Add visitor location headers*. O backend lê `cf-ipcountry`, `cf-region` e `cf-ipcity`.
2. **Banco GeoIP local:** `npm run geoip:download` no backend baixa o DB-IP *IP to City Lite* (gratuito,
   licença CC BY 4.0, atualizado todo mês) para `data/geoip/` (fora do git). Para usar no deploy, rode o
   script no build/start ou aponte `GEOIP_DB_PATH` para o arquivo. A licença pede o crédito
   "IP Geolocation by DB-IP".

Sem nenhuma das duas, a cidade aparece como "(não definido)" e a tela de Local avisa.

## Idade e gênero

No Google Analytics, idade e gênero vêm dos perfis de anúncio do Google (quem está logado numa conta
Google), não do site. Um site sozinho não tem como saber isso de quem só visita. Alternativa: pedir a
data de nascimento (opcional) no cadastro e mostrar a idade de quem compra.

## Divulgando nas redes

Use o **Gerador de link** (Aquisição) em cada post, stories, bio ou anúncio. O Instagram e o TikTok
muitas vezes abrem links sem informar a origem; sem a UTM, essas visitas caem em "Direto".

Exemplo: `https://roupadedomingo.com.br/?utm_source=instagram&utm_medium=stories&utm_campaign=lancamento-dezembro`

## QR Code

- `segredo` (sem local): QR original de etiqueta e embalagem.
- `camiseta-costas`: costas da camiseta (`/segredo?q=costas`). Arte de impressão em
  `catalog/print-arts/qrcode/camiseta-costas-3000px.png`; também dá para baixar em Análise → Aquisição.
- Novo local impresso: adicione em `VARIANTS` no `frontend-roupa-de-domingo/scripts/gen-qrcode.cjs`.

## Limites

- Quem escaneia no celular e compra no computador aparece como duas pessoas.
- Quem limpa os dados do navegador vira um novo usuário.
- Quem recusa "Estatísticas" no banner conta só a chegada e a origem (sem páginas, tempo, local e eventos).
- GA4 e Meta Pixel continuam disponíveis na loja (com consentimento) para otimizar anúncios:
  `VITE_GA_MEASUREMENT_ID` e `VITE_META_PIXEL_ID`.

## Dados e LGPD

| Tabela | Conteúdo |
| --- | --- |
| `traffic_visits` (sessões) | origem, página de entrada, aparelho, sistema, navegador, tela, idioma, país/estado/cidade, novo ou recorrente, nº de páginas, tempo engajado e hash do id anônimo do carrinho |
| `page_views` | página, título, ordem na sessão e tempo engajado |
| `analytics_events` | evento, produto ou termo buscado (ou nº do pedido) e valor |

Sem IP, nome, e-mail, CPF ou cookie. Base legal: legítimo interesse (art. 7º, IX), informado na Política
de Privacidade e na de Cookies, com opção de recusar em "Estatísticas". O pedido guarda a origem em
`attributionChannel` / `attributionSource` / `attributionCampaign` / `attributionContent`.

## API

| Rota | Uso |
| --- | --- |
| `POST /api/analytics/collect` | coleta da loja (público, 120/min por IP) |
| `GET /api/admin/analytics/overview` | Resumo (com o período anterior) |
| `GET /api/admin/analytics/realtime` | Tempo real |
| `GET /api/admin/analytics/summary` | Aquisição |
| `GET /api/admin/analytics/pages?group=` | Engajamento |
| `GET /api/admin/analytics/paths?start=&group=` | Caminhos |
| `GET /api/admin/analytics/audience` | Local e tecnologia |
| `GET /api/admin/analytics/funnel` | Monetização |

As rotas de admin aceitam `from` e `to` (`AAAA-MM-DD`, horário de Brasília); padrão: últimos 28 dias.
