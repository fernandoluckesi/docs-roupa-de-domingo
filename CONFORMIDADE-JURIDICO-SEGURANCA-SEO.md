# Conformidade — Jurídico, Segurança e SEO

Checklist do que um e-commerce de roupas precisa ter no Brasil, cruzado com o que
o Roupa de Domingo tem hoje.

| Marca | Significado |
| --- | --- |
| `[x]` | implementado e verificado (código + teste ponta a ponta de 04/11/2026) |
| `[~]` | implementado em código, mas depende de uma ação fora dele (contrato, dado real, conta de terceiro) |
| `[ ]` | ausente |

> **Aviso:** este documento é um guia técnico de engenharia, não parecer
> jurídico. Textos de políticas, prazos e cláusulas devem ser revisados por
> advogado antes de operar comercialmente.

---

## Resumo do estado atual

| Área | Pronto | Observação |
| --- | --- | --- |
| Páginas legais | 100% | 9 páginas: termos, privacidade, trocas, cookies, quem somos, contato/SAC, entrega, pagamentos, guia de tamanhos |
| LGPD | ~95% | Aceite versionado, prova de consentimento, exportação, exclusão, CPF cifrado. Falta o contrato com operadores (DPA) |
| Direito do consumidor (CDC) | ~95% | Arrependimento e defeito no próprio site, SAC com protocolo. Falta CNPJ e endereço reais |
| Segurança de aplicação | ~95% | helmet, CSP, HSTS, rate limit, bloqueio, cookie httpOnly, 2FA admin, auditoria |
| Pagamento | ~90% | Assinatura e valor do webhook conferidos, estorno integrado. NF-e é mock até contratar um emissor |
| SEO | ~85% | Meta por rota (SSR leve via SSI), JSON-LD, sitemap, robots, OG. Faltam Search Console e medição de Web Vitals |

### Antes de operar comercialmente (fora do código)

1. **Dados da empresa.**
   - Trocar razão social, CNPJ, IE, endereço e telefone **fictícios** em `frontend/src/config/company.ts`. É o único lugar a alterar.
   - O CNPJ provisório tem dígito verificador inválido de propósito.
2. **Revisão jurídica** dos textos das 9 páginas.
3. **NF-e.**
   - Contratar o emissor (Focus NFe, eNotas, NFE.io...) e obter o certificado A1.
   - Trocar o driver `mock` de `invoices.module.ts`.
   - Definir com a contabilidade o regime e a tabela de ICMS/DIFAL.
4. **Variáveis no Railway (backend).**

   | Variável | Valor |
   | --- | --- |
   | `DATA_ENCRYPTION_KEY` | gerar com `openssl rand -base64 32`; depois rodar `npm run data:encrypt -- --rotate` |
   | `MAIL_DRIVER` | `smtp` |
   | `SMTP_*` | dados do provedor |
   | `MAIL_SAC_INBOX` | caixa do SAC |

5. **Contratos com operadores:** Railway, com cláusulas-padrão da ANPD para transferência internacional.
6. **Ferramentas externas:** cadastrar o site no Google Search Console e enviar o `sitemap.xml`.

---

## 1. Identificação do fornecedor (obrigatório)

Base: Decreto 7.962/2013, art. 2º.

- [~] Razão social e CNPJ visíveis em todas as páginas: rodapé e `/quem-somos`, vindos de `src/config/company.ts`. **Os dados são fictícios.**
- [~] Endereço físico completo: rodapé e `/quem-somos` (fictício).
- [x] E-mail de contato (SAC): rodapé, `/contato` e `/quem-somos`.
- [~] Telefone e WhatsApp: exibidos, mas fictícios.
- [x] Página "Quem somos" (`/quem-somos`) e "Contato" (`/contato`).
- [x] SAC com prazo de 5 dias úteis (art. 4º).
  - `POST /api/contact` gera o protocolo `SAC-AAAAMMDD-XXXXXX` e a data limite em dias úteis.
  - O cliente recebe e-mail de recibo e a caixa do SAC recebe a mensagem.
  - A fila do admin fica em `GET /api/admin/contact`.

## 2. Termos de Uso

- [x] Página `/termos`, com botão para imprimir ou salvar em PDF.
- [x] Objeto do contrato e aceite explícito.
- [x] Regras de cadastro e responsabilidade pela senha.
- [x] Política de preços e correção de erro de precificação.
- [x] Propriedade intelectual das estampas.
- [x] Conduta proibida e limites de uso.
- [x] Foro (domicílio do consumidor prevalece) e legislação.
- [x] Data de vigência e histórico de versões (`LEGAL_VERSIONS`).
- [x] Aceite no cadastro: checkbox obrigatório. A versão aceita fica gravada em `users.termsVersion` e `consent_records`.
- [x] Aceite no checkout, que vale também para convidado. O pedido grava a versão na timeline.

### Específico do produto

- [x] Ressalva de conteúdo humorístico/satírico.
- [x] Não uso de marcas ou imagens de terceiros.
- [x] Notice-and-takedown: assunto "Direito autoral" no `/contato` e e-mail dedicado.
- [x] Classificação indicativa.

## 3. Política de Privacidade (LGPD)

- [x] Página `/privacidade`.
- [~] Controlador e encarregado (art. 41): exibidos, mas os dados do controlador são fictícios.
- [x] Dados por finalidade, base legal (art. 7º) e retenção. O detalhe está em [`LGPD-ROPA.md`](./LGPD-ROPA.md).
- [x] Operadores nomeados e transferência internacional: Mercado Pago, Correios, Railway e e-mail.
- [x] Como exercer os direitos e canal do encarregado.
- [x] `Payment.rawPayload` minimizado.
  - Ficam só status, método, parcelas, valor, datas e ids.
  - Sem parceiro de produção: os dados de entrega só saem da loja na etiqueta dos Correios.
- [x] Retenção: pedidos por 5 anos sem vínculo após a exclusão da conta.

### Direitos do titular (art. 18), em Minha conta → Privacidade e dados

- [x] Confirmação e acesso: `GET /api/users/me/export` devolve tudo em JSON.
- [x] Portabilidade: mesmo JSON, em download.
- [x] Correção: `PATCH /api/users/me`.
- [x] Eliminação: `DELETE /api/users/me` exige senha e anonimiza a conta. Pedido em andamento bloqueia.
- [x] Revogação de consentimento de marketing: `PATCH /api/users/me/consents`.
- [x] Com quem os dados são compartilhados: `GET /api/users/me/sharing`, também incluído na exportação.
- [x] ROPA (art. 37): [`LGPD-ROPA.md`](./LGPD-ROPA.md).
- [x] Plano de resposta a incidente (art. 48): [`PLANO-RESPOSTA-INCIDENTES.md`](./PLANO-RESPOSTA-INCIDENTES.md).

## 4. Cookies e rastreamento

- [x] Banner com aceitar, recusar e configurar. "Recusar opcionais" tem o mesmo peso visual de "Aceitar todos".
- [x] Bloqueio antes do consentimento.
  - Tema e easter eggs só gravam no navegador com consentimento de "preferências".
  - Tags futuras devem checar `hasConsent()`.
- [x] Página `/cookies` com a lista por categoria e duração.
- [x] Escolha registrada no servidor (`consent_records`) e versionada. Uma versão nova da política pede a escolha de novo.
- [x] Reabrir as preferências a qualquer momento, pelo rodapé ou por `/cookies`.
- [x] Fontes servidas pelo próprio site (`@fontsource`), sem o Google Fonts receber o IP do visitante.
- [x] Sem analytics nem pixels hoje. Ao adicionar um, carregá-lo só com `hasConsent("statistics")` ou `"marketing"`.

## 5. Direitos do consumidor (CDC + Decreto 7.962/2013)

### Direito de arrependimento (art. 49)

- [x] Política de 7 dias corridos a partir do recebimento (`/trocas-e-devolucoes`).
- [x] Devolução integral, incluindo o frete. Com todos os itens, o estorno é o total do pedido.
- [x] Fluxo no site: "Solicitar devolução" em `/conta/pedidos/<número>` (`POST /api/orders/:n/returns`). Convidado usa o e-mail da compra.
- [x] Status visível no pedido: solicitada → aprovada (com código de postagem) → recebida → reembolsada. Cada mudança gera e-mail.
- [x] Devolução pelo mesmo meio de pagamento: `REFUNDED` chama o estorno do Mercado Pago, com idempotência.

### Vício do produto

- [x] Troca por defeito em 90 dias (produto durável, art. 26, II). O rodapé dizia 30 e foi corrigido.
- [x] Prazo de 30 dias para sanar (art. 18), descrito na política.

### Informação do produto e da entrega

- [x] Preço total, frete por CEP, subtotal, desconto e total antes de confirmar.
- [x] Resumo e número do pedido.
- [x] Prazo por CEP na página do produto.
- [x] Tabela de medidas real (medidas das peças base) em `/guia-de-tamanhos` e no produto.
- [x] Composição do tecido e instruções de lavagem.
- [x] Variação de cor entre tela e impressão.
- [x] Aviso de que a produção sob demanda soma prazo de produção e envio.
- [x] Aviso de envio do exterior e possíveis tributos de importação: capas, garrafas e alguns moletons.
- [x] Contrato acessível para arquivar: termos e trocas imprimíveis, e o e-mail de confirmação resume o contrato.
- [x] E-mail de confirmação do pedido. Também há e-mails de pagamento aprovado, nota fiscal e devolução.

### Preço e ofertas

- [x] Preço em centavos inteiros.
- [x] Regras do cupom visíveis (`/termos#cupons`).
- [x] Sem preço "de/por" sem histórico. Não há promoção "de/por" no site.
- [x] Parcelamento honesto.
  - Removido o "6x sem juros", que não estava configurado.
  - O site informa "até 12x; juros, se houver, exibidos pelo Mercado Pago".
  - A preferência foi limitada a 12x.

## 6. Pagamento

- [x] Cartão nunca passa pela aplicação (Checkout Pro), escopo SAQ-A.
- [x] Status confirmado no servidor com reconsulta à API.
- [x] Processamento idempotente, `external_reference` e token só no servidor.
- [x] **Validação da assinatura do webhook** (`x-signature`, HMAC-SHA256 com `MP_WEBHOOK_SECRET`).
- [x] **Conferência do valor pago** contra `order.totalCents`. Uma divergência maior que 1 centavo não libera a produção e marca o pedido para análise.
- [x] Meios de pagamento e parcelamento exibidos antes do checkout (`/pagamentos`, produto e checkout).
- [x] Política de reembolso e estorno (`/pagamentos`, `/trocas-e-devoluções`).
- [x] Antifraude e limite de tentativas: máximo de 5 pedidos pendentes por pessoa por hora, além do rate limit do checkout (10 a cada 10 minutos) e dos cupons (10 por minuto).
- [~] Nota fiscal eletrônica.
  - O fluxo completo existe: o pagamento aprovado gera a nota, envia o e-mail e mostra no pedido.
  - O driver atual é **mock** (`MOCK-1-000001`, sem validade fiscal) até contratar um emissor.

## 7. Segurança de aplicação

- [x] `ValidationPipe` com whitelist, Prisma parametrizado, CORS restrito e filtro de exceção.
- [x] **helmet**: CSP `default-src 'none'` na API, HSTS, Referrer-Policy e CORP. O Swagger tem CSP própria.
- [x] **Rate limit** (`@nestjs/throttler`) de 120/min global por IP real (`TRUST_PROXY_HOPS=2`). Limites por rota:

  | Rota | Limite |
  | --- | --- |
  | Login | 8/min |
  | Cadastro | 5/min |
  | Esqueci a senha | 3 a cada 15 min |
  | SAC | 5 a cada 10 min |
  | Cupom | 10/min |
  | Checkout | 10 a cada 10 min |
  | Exportação | 5/h |
  | Exclusão de conta | 3/h |

- [x] CSP no site (nginx): `script-src 'self'`. A única exceção é o ViaCEP.
- [x] HSTS no nginx e redirect HTTP → HTTPS. O healthcheck do Railway fica fora do redirect.
- [x] Cabeçalhos extras: X-Frame-Options DENY, Permissions-Policy e COOP.
- [x] **JWT em cookie `httpOnly` + `SameSite=Lax`**, fora do `localStorage`. O token antigo é apagado.
  - Toda escrita autenticada por cookie exige o cabeçalho `X-Requested-With: rd-web` (proteção contra CSRF).
- [x] Revogação de sessão: `tokenVersion` no token.
  - Revoga em logout em todos os dispositivos, troca ou redefinição de senha, exclusão de conta e desativação do 2FA.
  - Logout (`POST /auth/logout`) apaga o cookie.
- [x] Política de senha: 8+ caracteres, letras e números, fora das mais comuns. Bloqueio de 15 minutos após 5 falhas.
- [x] Recuperação de senha: token de uso único, guardado só como hash, válido por 1 hora. A resposta é igual exista ou não a conta.
- [x] Verificação de e-mail no cadastro: link de 48 horas e reenvio em Minha conta.
- [x] **Código por e-mail no login de admin** (`ADMIN_LOGIN_CODE_REQUIRED`): depois da senha, um código de 6 dígitos vai para o e-mail da conta (15 min, 5 tentativas, uso único). Só a sessão aberta com o código acessa as rotas de admin. O 2FA por app autenticador foi removido em 09/11/2026.
- [x] Swagger desligado em produção por padrão (`SWAGGER_ENABLED`).
- [x] Trilha de auditoria completa ([AUDITORIA.md](./AUDITORIA.md)): login, senha, e-mail, 2FA, conta, consentimentos, pedidos, pagamentos, entrega, trocas, notas, SAC e toda rota `@Roles(ADMIN)`. Insert-only (trigger), retenção de 5 anos e cliente pseudonimizado.
- [x] Mascaramento de CPF, e-mail e telefone nos logs e na auditoria (`privacy.util.ts`).
- [x] **Criptografia em repouso do CPF e do segredo 2FA** (AES-256-GCM).
  - Valores antigos são cifrados no deploy (`dist/prisma/encrypt-documents.js`).
  - A rotação de chave usa `--rotate`.
- [x] Backup com restauração testada.
  - `scripts/backup/backup.sh` e `restore-test.sh` foram executados em 04/11/2026 com sucesso: 2 usuários, 19 produtos, 233 variantes e 2 pedidos.
  - Em produção, somar o backup do volume do Railway.
- [x] `npm audit` (alta e crítica) no CI e Dependabot.
  - Vulnerabilidades altas corrigidas com `overrides` (body-parser, express, multer, lodash, js-yaml) e Nest 10.4.22.
  - Restam 2 moderadas no backend, que exigem o NestJS 11, e 2 no frontend, que exigem o React Router 7.
- [x] Varredura de segredos commitados: gitleaks no CI.
- [x] Demonstração de login (`cliente@... / domingo123`) só aparece em dev.

> **Atenção:** o seed de produção criou usuários de demonstração com senha
> conhecida. Troque as senhas ou remova esses usuários no banco de produção.
> O admin já não acessa nada sem 2FA.

## 8. SEO

- [x] `robots.txt` com as rotas privadas bloqueadas e o sitemap declarado.
- [x] **`sitemap.xml`** dinâmico, servido pelo nginx a partir do backend. Contém as páginas estáticas e os produtos ativos com imagem; o produto secreto fica de fora.
- [x] **Meta tags por rota**.
  - No navegador: `react-helmet-async` (`Seo`, `RouteSeo`).
  - Para robôs e previews de link: SSI no nginx injeta `/api/seo/head?path=...` no `<head>` (SSR leve sem trocar o stack).
- [x] Open Graph e Twitter Card, com imagem padrão de 1200×630 (`/og-default.png`) e foto do produto.
- [x] `rel="canonical"` sem query string: o filtro do catálogo aponta para `/catalogo`.
- [x] **JSON-LD `Product`** com `AggregateOffer` e `AggregateRating`; `Organization`; `BreadcrumbList`.
- [x] `alt` descritivo, `width`/`height` e `loading="lazy"` nas imagens. A imagem principal usa `fetchpriority=high`.
- [x] `<h1>` único por página.
- [x] Favicon (SVG e PNG), `apple-touch-icon` e `manifest.webmanifest`.
- [x] Breadcrumb visível no produto e nas páginas legais.
- [x] Conteúdo editorial de cauda longa: guia de tamanhos, entrega e pagamentos.
- [x] `noindex` nas rotas privadas: conta, checkout, carrinho, pagamento e login.
- [ ] Imagens em WebP/AVIF. Os mockups da Printful são JPG; converter no build é a próxima otimização.
- [ ] Google Search Console e envio do sitemap (ação manual).
- [ ] Core Web Vitals medidos em produção (PageSpeed Insights ou CrUX), depois do deploy.
- [ ] `hreflang`: não se aplica, o site só existe em pt-BR.

## 9. Acessibilidade (WCAG 2.1 AA)

- [x] Contraste mínimo de 4.5:1 medido nos 3 temas.
  - Corrigidos `textFaint` em todos.
  - No tema "domingo": accent, perigo e sucesso.
  - No tema "caos": texto sobre o rosa.
- [x] Link "Pular para o conteúdo" e foco visível global.
- [x] `aria-label` nos controles de ícone (fechar aviso, miniaturas, código 2FA).
- [x] Erros de formulário com `aria-describedby` e `aria-invalid` no cadastro, senha, contato, devolução e checkout (termos).
- [x] `prefers-reduced-motion` respeitado.
- [ ] Teste com leitor de tela (NVDA ou VoiceOver): fazer manualmente antes do lançamento.

## 10. Fiscal e operacional

- [~] Emissão de NF-e por pedido: fluxo pronto, driver mock (ver seção 6).
- [ ] Cálculo de ICMS/DIFAL por UF: depende do regime tributário definido pela contabilidade.
  - O campo `INVOICE_APPROX_TAX_PERCENT` atende a Lei 12.741 (tributos aproximados) quando a contabilidade informar o percentual.
- [ ] Registro contábil das vendas: com a contabilidade.
- [x] Guarda de documentos fiscais por 5 anos: pedidos e notas não são apagados, só desvinculados na exclusão da conta.
- [x] Printful descontinuada (09/11/2026): produção e envio próprios; sem transferência internacional para produção.
- [x] Definição do importador: o consumidor pessoa física é o importador nas remessas do exterior, informado antes da compra no produto e em `/entrega`.

---

## Variáveis novas (backend)

| Variável | Para quê | Produção |
| --- | --- | --- |
| `DATA_ENCRYPTION_KEY` | AES-256 do CPF e do 2FA | **gerar** (`openssl rand -base64 32`). Sem ela, usa a chave derivada do `JWT_SECRET` |
| `MAIL_DRIVER`, `MAIL_FROM`, `MAIL_SAC_INBOX`, `SMTP_*` | e-mails transacionais | `smtp` + dados do provedor (hoje `log`: só console) |
| `TRUST_PROXY_HOPS` | IP real para o rate limit | `2` (padrão em produção) |
| `SWAGGER_ENABLED` | `/api/docs` | vazio (desligado em produção) |
| `ADMIN_2FA_REQUIRED` | 2FA no admin | `true` |
| `MAX_FAILED_LOGINS`, `LOGIN_LOCK_MINUTES` | bloqueio | `5` / `15` |
| `INVOICE_APPROX_TAX_PERCENT` | Lei 12.741 | informado pela contabilidade |

## Referências

- [Lei 13.709/2018 — LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [Lei 8.078/1990 — CDC](https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm)
- [Decreto 7.962/2013 — comércio eletrônico](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/decreto/d7962.htm)
- [Lei 12.965/2014 — Marco Civil da Internet](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l12965.htm)
- [ANPD — Regulamento de comunicação de incidente](https://www.gov.br/anpd/pt-br)
- [Google — dados estruturados de produto](https://developers.google.com/search/docs/appearance/structured-data/product)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- Documentação interna: [`LGPD-ROPA.md`](./LGPD-ROPA.md), [`PLANO-RESPOSTA-INCIDENTES.md`](./PLANO-RESPOSTA-INCIDENTES.md), [`MERCADO-PAGO.md`](./MERCADO-PAGO.md)
