# Modelo de dados — Roupa de Domingo

Banco: PostgreSQL 16. ORM: Prisma. Schema em
`backend-roupa-de-domingo/prisma/schema.prisma`.

## Diagrama

```
User 1─n Address
User 1─n Order 1─n OrderItem ──n─1 ProductVariant ──n─1 Product
User 1─1 Cart  1─n CartItem  ──n─1 ProductVariant
Order 1─1 Payment
Order 1─1 Fulfillment
Product n─1 Category
Product 1─n ProductImage
User 1─n EasterEggDiscovery n─1 EasterEgg 0─1 Coupon
Order n─0 Coupon
```

## Entidades

### User

| Campo                 | Tipo                   | Nota                                                      |
| --------------------- | ---------------------- | --------------------------------------------------------- |
| id                    | uuid PK                |                                                           |
| email                 | string unique          | login                                                     |
| passwordHash          | string                 | bcrypt                                                    |
| name                  | string                 |                                                           |
| phone                 | string?                |                                                           |
| document              | string?                | CPF                                                       |
| role                  | enum CUSTOMER \| ADMIN | default CUSTOMER                                          |
| humorLevel            | int                    | 0–100, "tolerância ao humor ácido" (easter egg de perfil) |
| createdAt / updatedAt | datetime               |                                                           |

### Address

`id, userId, label, recipient, zipCode, street, number, complement?, district, city, state, isDefault, createdAt`

### Category

`id, slug unique, name, description?, emoji?` — `camisetas`, `canecas`, `capas-de-celular`, `secretos`

### Product

| Campo                | Tipo                                                                    | Nota                          |
| -------------------- | ----------------------------------------------------------------------- | ----------------------------- |
| id                   | uuid PK                                                                 |                               |
| slug                 | string unique                                                           | URL                           |
| name                 | string                                                                  |                               |
| description          | text                                                                    |                               |
| humor                | enum ACIDO \| SARCASTICO \| EXISTENCIAL \| ABSURDO \| PASSIVO_AGRESSIVO | eixo editorial                |
| basePriceCents       | int                                                                     | preço em centavos             |
| categoryId           | fk                                                                      |                               |
| tags                 | string[]                                                                | busca                         |
| isFeatured           | bool                                                                    | vitrine                       |
| isSecret             | bool                                                                    | só aparece após easter egg    |
| isActive             | bool                                                                    |                               |
| printProviderSku     | string?                                                                 | SKU no parceiro de estamparia |
| rating / ratingCount | float / int                                                             | social proof                  |

### ProductVariant

`id, productId, sku unique, size?, color?, model?, priceCents, isAvailable, printProviderVariantId?`

- Camiseta: `size` (P/M/G/GG/XGG) + `color`
- Caneca: `size` (325ml/475ml)
- Capa: `model` (iPhone/Galaxy/Moto...)

### ProductImage

`id, productId, url, alt, position`

### Cart / CartItem

- `Cart`: `id, userId? unique, sessionId? unique, couponId?, createdAt, updatedAt`
- `CartItem`: `id, cartId, variantId, quantity, customText?` (+ unique `[cartId, variantId]`)
- Um carrinho pertence a um usuário **ou** a uma sessão anônima.

### Coupon

`id, code unique, description, type (PERCENT|FIXED|FREE_SHIPPING), value, minSubtotalCents, maxUses?, usedCount, isSecret, expiresAt?, isActive`

### Order

| Campo                                                           | Tipo          | Nota                                                                          |
| --------------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------- |
| id                                                              | uuid PK       |                                                                               |
| number                                                          | string unique | ex. `RD-7F3K9A` — vira `external_reference` no MP                             |
| userId?                                                         | fk            | permite convidado                                                             |
| status                                                          | enum          | PENDING, PAID, IN_PRODUCTION, SHIPPED, DELIVERED, CANCELLED, REFUNDED, FAILED |
| customerName / customerEmail / customerPhone / customerDocument | string        | snapshot                                                                      |
| shipping\*                                                      | campos        | snapshot do endereço                                                          |
| subtotalCents, discountCents, shippingCents, totalCents         | int           | calculado no servidor                                                         |
| couponId?                                                       | fk            |                                                                               |
| shippingMethod, estimatedDays                                   | string / int  |                                                                               |
| trackingCode?                                                   | string        |                                                                               |
| notes?                                                          | text          |                                                                               |
| timeline                                                        | json          | histórico `[{status, at, note}]`                                              |

### OrderItem

`id, orderId, variantId?, productName, variantLabel, sku, unitPriceCents, quantity, totalCents, imageUrl?, customText?`
→ snapshot completo: o pedido não é afetado por mudanças futuras no produto.

### Payment

| Campo              | Tipo                                                              | Nota                                  |
| ------------------ | ----------------------------------------------------------------- | ------------------------------------- |
| id                 | uuid PK                                                           |                                       |
| orderId            | fk unique                                                         |                                       |
| provider           | string                                                            | `mercadopago` / `mock`                |
| preferenceId?      | string                                                            | id da Preference                      |
| providerPaymentId? | string                                                            | id do pagamento no MP                 |
| status             | enum PENDING, APPROVED, IN_PROCESS, REJECTED, REFUNDED, CANCELLED |                                       |
| method?            | string                                                            | pix, credit_card, boleto...           |
| installments?      | int                                                               |                                       |
| amountCents        | int                                                               |                                       |
| initPoint?         | string                                                            | URL de redirecionamento               |
| rawPayload         | json                                                              | resposta crua do provider (auditoria) |
| paidAt?            | datetime                                                          |                                       |

### Fulfillment

`id, orderId unique, provider, providerOrderId?, status (QUEUED|SENT|IN_PRODUCTION|SHIPPED|DELIVERED|ERROR), trackingCode?, trackingUrl?, lastError?, rawPayload, sentAt?, updatedAt`

### EasterEgg / EasterEggDiscovery

- `EasterEgg`: `id, code unique, title, hint, message, trigger, rewardCouponId?, points, isActive`
- `EasterEggDiscovery`: `id, easterEggId, userId?, sessionId?, discoveredAt` (+ unique `[easterEggId, userId]` e `[easterEggId, sessionId]`)

## Estados do pedido

```
PENDING ──pagamento aprovado──► PAID ──print job criado──► IN_PRODUCTION
   │                                                            │
   ├─rejeitado─► FAILED                                         ▼
   ├─expirado──► CANCELLED                                   SHIPPED ──► DELIVERED
   └─estorno───► REFUNDED
```

## Dados do seed

- 4 categorias
- 14 produtos (5 camisetas, 4 canecas, 4 capas, 1 secreto) com variantes e imagens
- 5 cupons (2 secretos, liberados por easter egg)
- 9 easter eggs catalogados
- Usuários: `cliente@roupadedomingo.com` / `admin@roupadedomingo.com` — senha `domingo123`
