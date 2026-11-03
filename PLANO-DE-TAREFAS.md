# Roupa de Domingo — Plano de Tarefas

> Loja virtual de roupas, canecas e capas de celular com estampas de humor ácido,
> operada via dropshipping de estamparia, com easter eggs espalhados pela experiência.

**Stack**

- Frontend: `frontend-roupa-de-domingo` — React 18 + Vite + TypeScript + styled-components + axios
- Backend: `backend-roupa-de-domingo` — NestJS 10 + TypeScript + Prisma + PostgreSQL
- Pagamento: Mercado Pago (Checkout Pro — redirecionamento real para o `init_point`)
- Dropshipping: provider de estamparia (adapter com driver `mock` para rodar local)
- Infra local: Docker Compose (postgres + backend + frontend)

**Legenda:** `[ ]` pendente · `[x]` concluído · `[~]` parcial/stub intencional

---

## 0. Descoberta e documentação

- [x] 0.1 Definir escopo, stack e premissas
- [x] 0.2 Criar `docs/PLANO-DE-TAREFAS.md` (este documento)
- [x] 0.3 Criar `docs/ARQUITETURA.md`
- [x] 0.4 Criar `docs/MODELO-DE-DADOS.md`
- [x] 0.5 Criar `docs/MERCADO-PAGO.md` (fluxo de checkout + webhook)
- [x] 0.6 Criar `docs/EASTER-EGGS.md` (catálogo, gatilhos, recompensas)
- [x] 0.7 Criar `docs/DROPSHIPPING.md` (contrato com a estamparia)
- [x] 0.8 Criar `docs/COMO-RODAR.md`

## 1. Infraestrutura local (Docker)

- [x] 1.1 `docker-compose.yml` com postgres 16, backend e frontend
- [x] 1.2 Healthcheck do postgres + `depends_on` condicional
- [x] 1.3 `Dockerfile` do backend (dev com hot reload + target de produção)
- [x] 1.4 `Dockerfile` do frontend (dev Vite + target de build/nginx)
- [x] 1.5 `.env.example` na raiz e em cada app
- [x] 1.6 Volume nomeado para o banco e bind mount do código
- [x] 1.7 Script de bootstrap (`migrate deploy` + `seed`) no start do backend
- [x] 1.8 Base `node:20` no backend (Alpine/slim não têm OpenSSL para os engines do Prisma)
- [x] 1.9 `scripts/export-corporate-ca.ps1` + `NODE_EXTRA_CA_CERTS` para builds atrás de proxy com TLS interceptado
- [x] 1.10 Frontend na porta 5273 para não conflitar com outros projetos Vite no host

## 2. Backend — fundação

- [x] 2.1 Projeto NestJS (package.json, tsconfig, nest-cli, eslint/prettier)
- [x] 2.2 `main.ts` com CORS, `ValidationPipe` global, prefixo `/api`, Swagger em `/api/docs`
- [x] 2.3 `ConfigModule` com validação de env
- [x] 2.4 `PrismaModule` + `PrismaService` (lifecycle hooks)
- [x] 2.5 Filtro global de exceções + interceptor de resposta
- [x] 2.6 Módulo `health` (`GET /api/health`)

## 3. Backend — modelo de dados

- [x] 3.1 `schema.prisma`: User, Address
- [x] 3.2 Product, ProductVariant, ProductImage, Category
- [x] 3.3 Cart, CartItem
- [x] 3.4 Order, OrderItem, Payment
- [x] 3.5 Coupon, EasterEgg, EasterEggDiscovery
- [x] 3.6 Fulfillment (print job do dropshipping)
- [x] 3.7 Migration inicial versionada
- [x] 3.8 Seed: categorias, 12+ produtos de humor ácido, variantes, cupons, easter eggs, usuário demo

## 4. Backend — autenticação e usuários

- [x] 4.1 `POST /api/auth/register` (bcrypt)
- [x] 4.2 `POST /api/auth/login` (JWT access token)
- [x] 4.3 `GET /api/auth/me`
- [x] 4.4 `JwtStrategy`, `JwtAuthGuard`, `OptionalJwtGuard`, `RolesGuard`, decorator `@CurrentUser`
- [x] 4.5 CRUD de endereços do usuário
- [x] 4.6 `PATCH /api/users/me` (perfil)

## 5. Backend — catálogo

- [x] 5.1 `GET /api/products` com filtros (categoria, humor, busca, tags, preço, paginação, ordenação)
- [x] 5.2 `GET /api/products/:slug` com variantes e imagens
- [x] 5.3 `GET /api/categories`
- [x] 5.4 `GET /api/products/featured` (vitrine da home)
- [x] 5.5 Endpoints admin de produto (create/update/delete protegidos por role)

## 6. Backend — carrinho

- [x] 6.1 Carrinho por usuário autenticado ou por `x-session-id` anônimo
- [x] 6.2 `GET /api/cart`, `POST /api/cart/items`, `PATCH /api/cart/items/:id`, `DELETE /api/cart/items/:id`, `DELETE /api/cart`
- [x] 6.3 Merge do carrinho anônimo no login
- [x] 6.4 Cálculo de subtotal/frete/desconto no servidor
- [x] 6.5 Aplicação e validação de cupom (`POST /api/cart/coupon`)

## 7. Backend — pedidos e pagamento (Mercado Pago)

- [x] 7.1 `POST /api/orders` (checkout: snapshot de itens, endereço, totais)
- [x] 7.2 Serviço Mercado Pago: criação de `Preference` com items, payer, back_urls, external_reference
- [x] 7.3 Retorno do `init_point` / `sandbox_init_point` para redirecionamento real
- [x] 7.4 `POST /api/payments/webhook` (notificação de pagamento → consulta na API → atualiza Order/Payment)
- [x] 7.5 `GET /api/orders` e `GET /api/orders/:number` (histórico e acompanhamento)
- [x] 7.6 Máquina de estados do pedido (PENDING → PAID → IN_PRODUCTION → SHIPPED → DELIVERED / CANCELLED)
- [x] 7.7 Driver `mock` de pagamento para rodar sem credenciais (`PAYMENT_DRIVER=mock`)
- [x] 7.8 Endpoint de simulação de aprovação no modo mock (`POST /api/payments/mock/:orderNumber/approve`)

## 8. Backend — dropshipping da estamparia

- [x] 8.1 Interface `PrintProvider` (createOrder, getOrder, quoteShipping, cancelOrder)
- [x] 8.2 Driver `MockPrintProvider` (gera providerOrderId, tracking e evolui status)
- [x] 8.3 Envio automático do print job quando o pagamento é aprovado
- [x] 8.4 `POST /api/fulfillment/webhook` (status de produção/envio do parceiro)
- [x] 8.5 Cotação de frete por CEP (`POST /api/shipping/quote`)

## 9. Backend — easter eggs

- [x] 9.1 `GET /api/easter-eggs` (somente os já descobertos + contagem total)
- [x] 9.2 `POST /api/easter-eggs/:code/discover` (registra descoberta, idempotente)
- [x] 9.3 Recompensa: cupom secreto liberado na descoberta
- [x] 9.4 `GET /api/easter-eggs/progress` (troféus / % de descoberta)
- [x] 9.5 Easter egg de backend: header `X-Powered-By-Domingo` e rota `GET /api/teapot` (418)

## 10. Frontend — fundação

- [x] 10.1 Projeto Vite + React + TS (package.json, tsconfig, vite.config, index.html)
- [x] 10.2 Tema e design tokens (`styles/theme.ts`) + `GlobalStyle`
- [x] 10.3 Cliente axios com baseURL, interceptors de token e `x-session-id`
- [x] 10.4 Camada de serviços (products, cart, orders, auth, payments, easterEggs, shipping)
- [x] 10.5 Rotas com react-router-dom + lazy loading
- [x] 10.6 Contextos: Auth, Cart, EasterEgg, Toast

## 11. Frontend — componentes e páginas

- [x] 11.1 Layout: Header com busca/carrinho, Footer, Container
- [x] 11.2 Componentes base: Button, Input, Select, Badge, Card, Modal, Spinner, QuantityStepper, Toast
- [x] 11.3 `ProductCard` + grid de catálogo
- [x] 11.4 Home (hero ácido, vitrine, categorias, faixa de easter egg)
- [x] 11.5 Catálogo com filtros (categoria, humor, busca, ordenação)
- [x] 11.6 Página de produto (galeria, seleção de variante, add ao carrinho)
- [x] 11.7 Carrinho (itens, cupom, resumo, frete)
- [x] 11.8 Checkout (dados, endereço com CEP, resumo, botão "Pagar com Mercado Pago")
- [x] 11.9 Redirecionamento real para o `init_point` do Mercado Pago
- [x] 11.10 Páginas de retorno: sucesso / pendente / falha
- [x] 11.11 Login e cadastro
- [x] 11.12 Minha conta: perfil, endereços, pedidos
- [x] 11.13 Detalhe do pedido com timeline de status
- [x] 11.14 Página 404 com humor ácido
- [x] 11.15 Página `/trofeus` (progresso dos easter eggs)

## 12. Frontend — easter eggs

- [x] 12.1 Hook `useKonamiCode` → modo caos (tema invertido + cupom)
- [x] 12.2 7 cliques no logo → "modo domingo de manhã"
- [x] 12.3 Digitar `desculpa` em qualquer tela → desconto de arrependimento
- [x] 12.4 Carrinho vazio aberto 3x → sermão motivacional ácido
- [x] 12.5 Mensagens no `console` (ASCII art + vaga de emprego)
- [x] 12.6 Hover longo (5s) no rodapé → confissão da marca
- [x] 12.7 Quantidade 42 de um item → resposta para tudo
- [x] 12.8 404 com easter egg próprio
- [x] 12.9 Produto secreto desbloqueável
- [x] 12.10 Notificação/toast de easter egg descoberto + registro no backend

## 13. Qualidade e fechamento

- [x] 13.1 `README.md` na raiz de `refs/RD`
- [x] 13.2 Scripts de conveniência (`npm run dev`, `docker compose up`)
- [x] 13.3 Validação de build/typecheck (backend e frontend compilam sem erro)
- [x] 13.4 Checklist de smoke test manual documentado
- [x] 13.5 `scripts/smoke-test.sh` — 30 asserções end-to-end contra a API rodando
- [x] 13.6 Stack validado no Docker: 3 containers de pé, smoke test 30/30
- [~] 13.7 Testes unitários/E2E de código — fora do escopo pedido (não solicitado)

### Resultado da validação

```
docker compose ps
  postgres   Up (healthy)   5432
  backend    Up             3333
  frontend   Up             5273

bash scripts/smoke-test.sh
  Passou: 30   Falhou: 0
```

---

## Premissas assumidas

1. **Mercado Pago**: o fluxo usa Checkout Pro. Sem credenciais reais, `PAYMENT_DRIVER=mock`
   gera uma tela de pagamento simulada; com `MP_ACCESS_TOKEN` preenchido, o backend cria uma
   Preference real e o frontend redireciona para o `init_point` do Mercado Pago.
2. **Dropshipping**: nenhum provider real foi contratado, então existe um adapter com driver
   `mock`. Trocar para um provider real é implementar a interface `PrintProvider`.
3. **Estoque**: produção on-demand, logo não há controle de estoque — apenas disponibilidade da variante.
4. **Pagamento em moeda BRL** e frete calculado por faixa de CEP (tabela simplificada).
