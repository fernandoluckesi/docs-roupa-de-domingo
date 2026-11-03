# Arquitetura — Roupa de Domingo

## Visão geral

```
┌──────────────────────────────┐
│  frontend-roupa-de-domingo   │  React 18 + Vite + styled-components + axios
│  :5173                       │
└───────────────┬──────────────┘
                │ REST /api (axios, JWT no header, x-session-id p/ carrinho anônimo)
                ▼
┌──────────────────────────────┐
│  backend-roupa-de-domingo    │  NestJS 10 + Prisma
│  :3333  /api  /api/docs      │
└───┬──────────┬───────────┬───┘
    │          │           │
    ▼          ▼           ▼
┌────────┐ ┌─────────┐ ┌───────────────────┐
│Postgres│ │ Mercado │ │ Print Provider    │
│ :5432  │ │  Pago   │ │ (estamparia DS)   │
└────────┘ └─────────┘ └───────────────────┘
```

Tudo roda via `docker compose up` a partir de `refs/RD`.

## Backend — organização em módulos

```
src/
├── main.ts                     bootstrap, CORS, Swagger, ValidationPipe, prefixo /api
├── app.module.ts
├── common/
│   ├── decorators/             @CurrentUser, @Roles, @Public
│   ├── guards/                 JwtAuthGuard, OptionalJwtGuard, RolesGuard
│   ├── filters/                AllExceptionsFilter
│   ├── interceptors/           EasterEggHeaderInterceptor
│   └── utils/                  money, slugify, orderNumber
├── config/                     configuration.ts + validação de env
├── prisma/                     PrismaModule, PrismaService, seed.ts, schema.prisma
└── modules/
    ├── health/
    ├── auth/                   register, login, me, JwtStrategy
    ├── users/                  perfil + endereços
    ├── catalog/                products, categories
    ├── cart/                   carrinho + cupom
    ├── orders/                 checkout, histórico, máquina de estados
    ├── payments/               Mercado Pago (real + mock), webhook
    ├── shipping/               cotação por CEP
    ├── fulfillment/            print provider adapter + webhook
    └── easter-eggs/            descoberta, progresso, recompensa
```

### Decisões

| Decisão                               | Motivo                                                                       |
| ------------------------------------- | ---------------------------------------------------------------------------- |
| Prisma em vez de TypeORM              | migrations declarativas e tipagem gerada, menos boilerplate                  |
| Totais calculados no servidor         | o cliente nunca define preço; evita manipulação no checkout                  |
| Snapshot de preço no `OrderItem`      | o pedido não muda se o produto for reprecificado depois                      |
| `external_reference` = `order.number` | correlaciona webhook do Mercado Pago com o pedido local                      |
| Adapter `PrintProvider`               | permite rodar local sem parceiro e trocar de fornecedor sem tocar no domínio |
| Carrinho com `sessionId`              | compra sem cadastro; no login o carrinho anônimo é mesclado                  |
| Easter eggs persistidos               | troféus sobrevivem ao reload e liberam cupons reais                          |

## Frontend — organização

```
src/
├── main.tsx / App.tsx          providers + rotas lazy
├── routes/                     definição das rotas
├── styles/                     theme.ts, global.ts, styled.d.ts
├── services/
│   ├── http.ts                 instância axios + interceptors
│   └── *.service.ts            products, cart, auth, orders, payments, shipping, easterEggs
├── contexts/                   AuthContext, CartContext, EasterEggContext, ToastContext
├── hooks/                      useKonamiCode, useTypedPhrase, useLongHover, useDebounce
├── components/
│   ├── layout/                 Header, Footer, Container
│   ├── ui/                     Button, Input, Select, Card, Badge, Modal, Spinner, Toast...
│   └── product/                ProductCard, ProductGrid, VariantPicker
└── pages/                      Home, Catalog, Product, Cart, Checkout, PaymentResult,
                                Login, Register, Account, Orders, OrderDetail, Trophies, NotFound
```

### Fluxo de dados

1. `axios` injeta `Authorization: Bearer <token>` (localStorage) e `x-session-id` (uuid persistido).
2. `CartContext` é a fonte única do carrinho; toda mutação volta do backend já recalculada.
3. `EasterEggContext` escuta gatilhos globais, dispara o toast e faz `POST /easter-eggs/:code/discover`.
4. No checkout, o front chama `POST /orders` e recebe `paymentUrl`; faz `window.location.href = paymentUrl`.

## Fluxo de compra ponta a ponta

```
Catálogo → Produto → Carrinho → Checkout
   → POST /api/orders           (cria Order PENDING + Payment + Preference MP)
   → redirect p/ init_point MP  (tela real do Mercado Pago)
   → back_url /pagamento/sucesso|pendente|falha
   → POST /api/payments/webhook (MP notifica; backend consulta e confirma)
   → Order PAID → cria print job no provider → IN_PRODUCTION
   → webhook do provider → SHIPPED (tracking) → DELIVERED
```

## Segurança

- Senhas com bcrypt (10 rounds).
- JWT assinado com `JWT_SECRET`, expiração configurável.
- `ValidationPipe` com `whitelist` e `forbidNonWhitelisted`.
- Webhooks validam `external_reference` e reconsultam o pagamento na API do Mercado Pago em vez de confiar no payload.
- Rotas administrativas protegidas por `RolesGuard` (`role: ADMIN`).
- CORS restrito a `CORS_ORIGIN`.
