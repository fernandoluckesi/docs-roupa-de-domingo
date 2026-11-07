# Printful: API para disparar pedidos

Este guia mostra como disparar pedidos da camiseta de exemplo pela API do Printful
e como ligar isso ao `PrintProvider` do backend (ver [DROPSHIPPING.md](DROPSHIPPING.md)).

> Levantado em 03/11/2026 na conta Printful do Fernando. Os IDs abaixo são reais.

---

## 1. Como o Printful funciona (resumo)

- **Catálogo**: produtos "em branco" (`product_id`). Cada cor e tamanho é uma `variant_id` do catálogo.
- **Loja (store)**: o lugar onde ficam os seus produtos já estampados. Para integração própria
  usa-se uma loja do tipo **Manual order platform / API**.
- **Sync product / sync variant**: o produto que você criou no Design Maker (arte e posição já
  definidas), publicado na loja. Cada tamanho vira uma *sync variant* com um `external_id`.
  Para pedir esse produto pela API, **basta informar a variante**, sem reenviar arquivos.
- **Pedido**: entra como `draft` (rascunho, sem cobrança). Ao **confirmar**, o Printful cobra o
  cartão/saldo da conta e manda para produção. Não existe sandbox: o rascunho é o "modo teste".
- **Entrega no Brasil**: das camisetas masculinas, só **6 produtos** entregam no Brasil. A única
  produzida **localmente** (parceiro Dimona, estoque BR em todas as variantes) é a
  **Men's Fitted Straight Cut T-Shirt** (`product_id 509`), com tamanhos brasileiros P–XGG.
  Exemplo do problema: a Gildan 64000 (`product_id 12`) tem estoque BR em só 7 de 249 variantes
  (ex.: Branca só no XL). Por isso a camiseta de exemplo usa o 509.

## 2. O que foi criado na conta

| Item                 | Valor                                                              |
| -------------------- | ------------------------------------------------------------------ |
| Loja                 | **Roupa de Domingo**: Manual order / API, Brasil, BRL             |
| `store_id`           | `19007611`                                                         |
| Produto (sync)       | **Camiseta Roupa de Domingo - Exemplo**                            |
| `sync_product_id`    | `488823609`                                                        |
| Base do catálogo     | Men's Fitted Straight Cut T-Shirt (Dimona Quality T-shirt), `509` |
| Técnica              | DTG, só frente                                                    |
| Arte                 | Texto "ROUPA DE DOMINGO", fonte Bebas Neue, preta, centralizada no alto do peito |
| Cor                  | Branca                                                             |
| Custo Printful       | R$ 53,95 por peça (R$ 49,09 no plano Growth)                       |
| Preço de varejo cadastrado | R$ 70,50 (padrão da Printful; só vale para nota/packing slip) |
| Frete Printful (BR)  | R$ 24,79 a R$ 68,69; prazo estimado de 11 a 12 dias                |

Painel do produto: https://www.printful.com/dashboard/product-templates/published/19007611/488823609

### Variantes

| Tamanho | `external_variant_id` (sync) | `variant_id` (catálogo) |
| ------- | ---------------------------- | ----------------------- |
| P       | `6aea4518912a04`             | `12804`                 |
| M       | `6aea4518912a22`             | `12805`                 |
| G       | `6aea4518912a33`             | `12806`                 |
| GG      | `6aea4518912a58`             | `12807`                 |
| XGG     | `6aea4518912a67`             | `12808`                 |

Guarde o `external_variant_id` em `ProductVariant.printProviderVariantId` (já existe no schema).

### Catálogo completo (04/11/2026)

Além da camiseta original, 18 produtos foram criados por API (`backend/scripts/printful/`). Em cada sync
product, `external_id` = slug do produto. Em cada sync variant, `external_id` = SKU da loja
(ex.: `CAM-SORRIA-PT-M`), por isso `printProviderVariantId` = SKU em `prisma/catalog.ts`.

| Categoria | Produtos | Base Printful (catálogo) | Variantes | Produção | Custo | Venda |
| --------- | -------- | ------------------------ | --------- | -------- | ----- | ----- |
| Camisetas | 6 (inclui a secreta) | 509 Dimona, DTG frente | Branca e Preta, P–XGG | **Brasil**, 9–10 dias | R$ 53,95 | R$ 89,90 (secreta R$ 119,90) |
| Moletons | 2 | 146 Gildan 18500, DTG frente | Preto e Marinho, P–XGG | Brasil quando há estoque, senão exterior | R$ 119,95 | R$ 219,90 |
| Canecas | 4 | 19 White Glossy Mug 11 oz | 325 ml | **Brasil**, 9–10 dias | R$ 44,95 | R$ 69,90 |
| Capas | 4 | 181 Clear Case iPhone + 267 Clear Case Samsung | iPhone 13–17 e Galaxy S23–S25 | Exterior, 10–25 dias | R$ 52,45–60,95 | R$ 99,90 |
| Garrafas | 2 | 382 Stainless Steel Water Bottle 17 oz | Branca e Preta | Exterior, 10–15 dias | R$ 132,95 | R$ 219,90 |

- Artes: PNG transparente gerado por `render.js`, publicado em `https://<front>/designs/`.
- Fotos do site: mockups do mockup generator da Printful, em `frontend/public/products/`.
- Capas e garrafas vêm de fora do Brasil: o prazo é maior e o cliente **pode pagar imposto de
  importação** na entrega (regras dos Correios / Receita para remessas internacionais).
- Em produção, o catálogo é aplicado por `npm run catalog:sync` a cada deploy (upsert por slug/SKU;
  variantes antigas ficam indisponíveis, pedidos não são apagados).
O `sync_variant_id` numérico também serve e pode ser obtido com `GET /store/products/488823609`.

> Existe também uma loja "Personal orders" (`19007165`) criada automaticamente pela Printful.
> Ela não é usada aqui.

---

## 3. Token de acesso (fazer manualmente)

O token **não** foi gerado: é uma credencial e precisa ser criado por você.

1. Acesse https://developers.printful.com/tokens e clique em **Create token** (Private token).
2. Escopo: escolha a loja **Roupa de Domingo** e marque pelo menos `orders`, `sync_products`,
   `webhooks` e `shipping_rates` (leitura e escrita).
3. Coloque o token no `.env` (nunca no git):

```env
PRINT_PROVIDER=printful
PRINT_API_URL=https://api.printful.com
PRINT_API_KEY=<token privado>
PRINTFUL_STORE_ID=19007611
PRINTFUL_CONFIRM_ORDERS=false   # true = confirma e cobra
PRINT_WEBHOOK_SECRET=<string aleatória longa>
```

Todas as chamadas usam:

```
Authorization: Bearer $PRINT_API_KEY
X-PF-Store-Id: 19007611        # obrigatório se o token for da conta inteira; inofensivo se for da loja
Content-Type: application/json
```

Limite de taxa: cerca de 120 requisições por minuto. Acima disso a API responde `429`
(respeite o header `Retry-After`).

---

## 4. Fluxo de um pedido

```
pagamento aprovado
  └─► POST /orders               (draft, sem cobrança)  → guarda order.id
       └─► POST /orders/{id}/confirm                    → cobra e vai para produção
            └─► webhook package_shipped                 → tracking → Order SHIPPED
```

Em desenvolvimento, pare no `draft`. Para conferir o custo sem criar nada, use `POST /orders/estimate-costs`.

### 4.1 Cotar frete

```bash
curl -s https://api.printful.com/shipping/rates \
  -H "Authorization: Bearer $PRINT_API_KEY" -H "X-PF-Store-Id: 19007611" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": { "country_code": "BR", "state_code": "SP", "city": "São Paulo", "zip": "01310-100" },
    "items": [ { "variant_id": 12805, "quantity": 1 } ],
    "currency": "BRL",
    "locale": "pt_BR"
  }'
```

A resposta traz `result[]` com `id` (ex.: `STANDARD`), `name`, `rate`, `minDeliveryDays` e `maxDeliveryDays`.
O `id` é o valor que vai em `shipping` no pedido.

### 4.2 Criar o pedido (rascunho)

```bash
curl -s https://api.printful.com/orders \
  -H "Authorization: Bearer $PRINT_API_KEY" -H "X-PF-Store-Id: 19007611" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "RD-7F3K9A",
    "shipping": "STANDARD",
    "recipient": {
      "name": "Maria Silva",
      "address1": "Av. Paulista, 1000",
      "address2": "Apto 12 - Bela Vista",
      "city": "São Paulo",
      "state_code": "SP",
      "country_code": "BR",
      "zip": "01310-100",
      "phone": "+5511999999999",
      "email": "cliente@example.com",
      "tax_number": "12345678909"
    },
    "items": [
      { "external_variant_id": "6aea4518912a22", "quantity": 1 }
    ],
    "retail_costs": { "currency": "BRL", "subtotal": "89.90", "shipping": "14.90" },
    "packing_slip": { "store_name": "Roupa de Domingo", "message": "Obrigado pela compra!" }
  }'
```

Regras para entrega no Brasil:

- `tax_number` (CPF ou CNPJ, só dígitos) é **obrigatório**. Sem ele, o pedido falha.
- `state_code` usa a sigla da UF (`SP`, `RJ`, ...).
- O Printful não tem campos para número e bairro. Junte rua e número em `address1`, e complemento e bairro em `address2`.
- `external_id` deve ser único por pedido. Use o `order.number` da loja; ele também permite consultar por `@RD-7F3K9A`.

Resposta (resumo):

```json
{
  "code": 200,
  "result": {
    "id": 123456789,
    "external_id": "RD-7F3K9A",
    "status": "draft",
    "costs": { "currency": "BRL", "subtotal": "53.95", "shipping": "24.79", "tax": "0.00", "total": "78.74" },
    "shipments": []
  }
}
```

Os valores acima são ilustrativos. O custo real vem em `result.costs`.

Para criar e confirmar numa chamada só, use `POST /orders?confirm=true` (isso **cobra** na hora).

### 4.3 Confirmar (envia para produção e cobra)

```bash
curl -s -X POST https://api.printful.com/orders/123456789/confirm \
  -H "Authorization: Bearer $PRINT_API_KEY" -H "X-PF-Store-Id: 19007611"
```

A conta Printful precisa ter um cartão cadastrado ou saldo na carteira (Billing).

### 4.4 Consultar, alterar e cancelar

| Ação                       | Chamada                                                |
| -------------------------- | ------------------------------------------------------ |
| Consultar pelo id          | `GET /orders/123456789`                                |
| Consultar pelo nosso número | `GET /orders/@RD-7F3K9A`                              |
| Alterar (só `draft`/`failed`) | `PUT /orders/{id}` (mesmo corpo do POST)            |
| Cancelar                   | `DELETE /orders/{id}` (só antes de entrar em produção) |
| Estimar custo              | `POST /orders/estimate-costs` (mesmo corpo do POST)    |
| Listar a loja              | `GET /store/products` e `GET /store/products/488823609` |

### 4.5 Status do Printful e status do domínio

| Printful (`result.status`) | `PrintOrderStatus`                         |
| -------------------------- | ------------------------------------------ |
| `draft`, `pending`         | `QUEUED`                                   |
| `inprocess`, `partial`     | `IN_PRODUCTION`                            |
| `fulfilled`                | `SHIPPED` (tracking em `shipments[]`)      |
| `onhold`                   | `QUEUED` (gera alerta: revisar no painel)  |
| `failed`, `canceled`       | `ERROR`                                    |

O Printful não informa a entrega final (`DELIVERED`). Para isso, consulte o rastreio dos
Correios/transportadora, ou marque o pedido como entregue manualmente.

---

## 5. Webhooks

Cadastre uma vez (a URL precisa ser pública; em dev use o ngrok):

```bash
curl -s https://api.printful.com/webhooks \
  -H "Authorization: Bearer $PRINT_API_KEY" -H "X-PF-Store-Id: 19007611" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://SEU-DOMINIO/api/fulfillment/webhook/printful?secret=<PRINT_WEBHOOK_SECRET>",
    "types": ["package_shipped", "package_returned", "order_failed", "order_canceled", "order_put_hold", "order_updated"]
  }'
```

- A v1 **não assina** os webhooks. Valide o `secret` da URL no controller e consulte
  `GET /orders/@{external_id}` antes de confiar no payload.
- Payload do `package_shipped` (campos usados):

```json
{
  "type": "package_shipped",
  "created": 1762200000,
  "store": 19007611,
  "data": {
    "order": { "id": 123456789, "external_id": "RD-7F3K9A", "status": "fulfilled" },
    "shipment": {
      "carrier": "CORREIOS",
      "service": "PAC",
      "tracking_number": "BR123456789BR",
      "tracking_url": "https://..."
    }
  }
}
```

Ele mapeia direto para o contrato atual de `POST /api/fulfillment/webhook`:
`external_id ← data.order.external_id`, `provider_order_id ← data.order.id`,
`status ← "shipped"`, `tracking_code ← data.shipment.tracking_number`, `tracking_url ← data.shipment.tracking_url`.

Para consultar ou remover: `GET /webhooks` e `DELETE /webhooks`.

---

## 6. Integração no backend (implementada)

| Peça | Onde |
| ---- | ---- |
| Driver | `src/modules/fulfillment/providers/printful-print.provider.ts` |
| Seleção do driver | `FulfillmentModule`: `PRINT_PROVIDER=printful` + `PRINT_API_KEY` (sem token, cai no mock) |
| Config | `print.printful.storeId` / `print.printful.confirmOrders` (`configuration.ts`) |
| Webhook | `POST /api/fulfillment/webhook/printful?secret=<PRINT_WEBHOOK_SECRET>` |
| Reenvio manual | `POST /api/fulfillment/:orderNumber/dispatch` (admin; só pedidos `PAID`) |
| Produto no seed | `camiseta-roupa-de-domingo` ("Roupa de Domingo (a original)"), branca P–XGG, com os `external_variant_id` da seção 2 |

Comportamento:

- Pagamento aprovado → `dispatchOrder` → `POST /orders` na Printful, referenciando a sync variant
  (`external_variant_id`). A arte já está na Printful; nada de arquivo é enviado.
- `PRINTFUL_CONFIRM_ORDERS=false` (padrão): o pedido fica **em rascunho** na Printful. Localmente o
  pedido continua `PAID`, o `Fulfillment` fica `SENT` com o id da Printful, e a timeline ganha a nota
  "Rascunho criado na estamparia". Nada é cobrado.
- `PRINTFUL_CONFIRM_ORDERS=true`: cria com `?confirm=true` (cobra e produz). O pedido vai para `IN_PRODUCTION`.
- `economico` e `expresso` viram `STANDARD`: é o único método da Printful para o Brasil.
- CPF/CNPJ vai **com máscara** (`000.000.000-00` / `00.000.000/0000-00`). Sem máscara a Printful
  responde `400 CPF number must match a pattern`.
- Item sem `printProviderVariantId` faz o envio falhar com `Itens sem variante Printful: <skus>` em
  `Fulfillment.lastError`. Desde 04/11/2026 todos os produtos do catálogo existem na Printful (seção 2).
- O campo "texto personalizado" da página de produto **não** chega à Printful: a sync variant tem arte fixa.

### Frete real no carrinho e no checkout

`ShippingService` (`src/modules/shipping/shipping.service.ts`) cota o frete na Printful
(`POST /shipping/rates`, `currency: BRL`) sempre que o carrinho recebe um CEP (`GET /api/cart?zipCode=`).

- A UF vem do CEP, por faixa dos Correios (`stateFromZipCode`), porque a Printful exige `state_code`.
- Só entram na cotação os itens com `printProviderVariantId` (`external_variant_id`).
- O resultado tem preço em centavos, `minDays`/`maxDays` e `estimatedDeliveryDate`. O front mostra
  "9 a 10 dias · chega até 16/11". `source: "printful"` indica cotação real.
- O checkout usa a mesma cotação dos totais do carrinho e grava `estimatedDays = maxDays` no pedido.
- Cache em memória de 10 minutos por CEP + itens, timeout de 8 s.
- **Fallback:** sem token, carrinho sem itens Printful, ou erro/timeout da API, o serviço usa a tabela
  local por região (log `Cotacao Printful falhou ... Usando tabela local`). O carrinho nunca quebra por
  causa da Printful.
- O frete grátis acima de `FREE_SHIPPING_THRESHOLD_CENTS` (R$ 249) continua valendo: a loja absorve o custo real.
- No Brasil só existe `STANDARD`, então aparece uma opção só. Se a Printful liberar `EXPRESS`, ele vira `expresso`.

Cotações de 04/11/2026: SP, 1 camiseta: R$ 68,69 (9 a 10 dias); RJ, 2 camisetas: R$ 101,69.

Docker: o backend recebe `NODE_EXTRA_CA_CERTS=/certs/corporate-ca.pem` (bundle de `scripts/export-corporate-ca.ps1`)
para conseguir chamar a Printful e o Mercado Pago atrás do proxy corporativo.

## 7. Testes realizados (03/11/2026)

| Teste | Resultado |
| ----- | --------- |
| Token (`GET /stores`) | 200, escopo da loja Roupa de Domingo |
| API → pedido RD-5LQFYX | Rascunho Printful **#184580582**, 1× M, arte `default` + `preview` |
| Front (localhost:5273) → checkout → pagamento simulado → pedido RD-93N68M | Rascunho Printful **#184581183** |
| `scripts/smoke-test.sh` | 30/30 (cria um rascunho a cada execução) |
| Webhook com segredo errado / pedido inexistente | 401 / `matched:false` |

Os rascunhos ficam em https://www.printful.com/dashboard/default/orders. Para apagar: `DELETE /orders/{id}`.

**Margem:** um pedido de teste custou **R$ 122,64** na Printful (R$ 53,95 da peça + R$ 68,69 de frete fixo),
mas o cliente pagou R$ 104,80 (R$ 89,90 + R$ 14,90 da tabela local). Com a tabela de frete atual, cada
camiseta dava prejuízo. Desde 04/11/2026 o cliente paga o frete real da Printful (seção 6). Acima de
R$ 249 o frete grátis ainda sai do bolso da loja (≈ R$ 100 para 3 camisetas): revise o limite.

### Como repetir

```bash
cd refs/RD
# .env na raiz: PRINT_PROVIDER=printful, PRINT_API_KEY, PRINTFUL_STORE_ID, PRINTFUL_CONFIRM_ORDERS=false
docker compose up -d --build
bash scripts/smoke-test.sh
```

Pelo front: abra http://localhost:5273/produto/camiseta-roupa-de-domingo, compre e aprove na tela de
pagamento simulado. O rascunho aparece no painel da Printful em segundos.

Mudanças em `src/` não recarregam sozinhas no Docker do Windows: rode `docker compose restart backend`
(o seed recria o banco a cada start).

## Referências

- Documentação da API: https://developers.printful.com/docs/
- Catálogo público (sem token): `GET https://api.printful.com/products/509`
