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

## 6. Driver para o backend (`PrintfulPrintProvider`)

Rascunho pronto para `src/modules/fulfillment/providers/printful-print.provider.ts`. Ele implementa
a interface atual sem mudar o domínio. Depois, registre `printful` na factory do `FulfillmentModule`
e exponha `print.storeId` (env `PRINTFUL_STORE_ID`) no config.

```ts
import { Injectable, InternalServerErrorException, Logger } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import axios, { AxiosInstance } from "axios";
import {
  CreatePrintOrderInput,
  PrintOrderResult,
  PrintOrderStatus,
  PrintProvider,
} from "./print-provider.interface";

const STATUS_MAP: Record<string, PrintOrderStatus> = {
  draft: "QUEUED",
  pending: "QUEUED",
  onhold: "QUEUED",
  inprocess: "IN_PRODUCTION",
  partial: "IN_PRODUCTION",
  fulfilled: "SHIPPED",
  failed: "ERROR",
  canceled: "ERROR",
};

@Injectable()
export class PrintfulPrintProvider implements PrintProvider {
  readonly name = "printful";
  private readonly logger = new Logger(PrintfulPrintProvider.name);
  private readonly client: AxiosInstance;
  private readonly autoConfirm: boolean;

  constructor(config: ConfigService) {
    this.client = axios.create({
      baseURL: config.get<string>("print.apiUrl") || "https://api.printful.com",
      timeout: 20000,
      headers: {
        Authorization: `Bearer ${config.get<string>("print.apiKey")}`,
        "X-PF-Store-Id": config.get<string>("print.storeId") ?? "",
        "Content-Type": "application/json",
      },
    });
    // Em dev, deixe false: o pedido fica em draft e nada é cobrado
    this.autoConfirm = config.get<string>("NODE_ENV") === "production";
  }

  async createOrder(input: CreatePrintOrderInput): Promise<PrintOrderResult> {
    const r = input.recipient;
    const body = {
      external_id: input.externalId,
      shipping: input.shippingMethod || "STANDARD",
      recipient: {
        name: r.name,
        address1: `${r.street}, ${r.number}`,
        address2: [r.complement, r.district].filter(Boolean).join(" - ") || undefined,
        city: r.city,
        state_code: r.state,
        country_code: "BR",
        zip: r.zipCode,
        phone: r.phone ?? undefined,
        tax_number: (r.document ?? "").replace(/\D/g, ""),
      },
      items: input.items.map((item) => ({
        external_variant_id: item.providerVariantId ?? item.sku,
        quantity: item.quantity,
      })),
    };

    try {
      const { data } = await this.client.post(
        `/orders${this.autoConfirm ? "?confirm=true" : ""}`,
        body,
      );
      return this.toResult(data.result);
    } catch (error) {
      const detail = axios.isAxiosError(error)
        ? JSON.stringify(error.response?.data?.error ?? error.message)
        : (error as Error).message;
      this.logger.error(`Printful recusou o pedido ${input.externalId}: ${detail}`);
      throw new InternalServerErrorException(
        "A estamparia nao respondeu. O pedido fica na fila para reenvio.",
      );
    }
  }

  async getOrder(providerOrderId: string): Promise<PrintOrderResult> {
    const { data } = await this.client.get(`/orders/${providerOrderId}`);
    return this.toResult(data.result);
  }

  async cancelOrder(providerOrderId: string): Promise<void> {
    await this.client.delete(`/orders/${providerOrderId}`);
  }

  private toResult(order: any): PrintOrderResult {
    const shipment = order.shipments?.[0];
    return {
      providerOrderId: String(order.id),
      status: STATUS_MAP[order.status] ?? "QUEUED",
      trackingCode: shipment?.tracking_number ?? null,
      trackingUrl: shipment?.tracking_url ?? null,
      raw: order,
    };
  }
}
```

Pontos de atenção:

- `quoteShipping` do contrato documentado ainda não está na interface real. Quando entrar, use `POST /shipping/rates` (seção 4.1).
- O webhook atual valida `x-print-signature`. Para o Printful, crie a rota
  `/fulfillment/webhook/printful` validando `?secret=`, como explicado na seção 5.
- Seed: preencha `printProviderVariantId` das variantes P/M/G/GG/XGG com os `external_variant_id` da tabela 2.

---

## 7. Teste rápido (sem cobrança)

1. Crie o token (seção 3) e exporte `PRINT_API_KEY`.
2. Rode o `curl` da seção 4.2. Ele deve responder `status: "draft"` e mostrar `costs`.
3. Confira em https://www.printful.com/dashboard/default/orders: o pedido aparece como *Draft*.
4. Apague o rascunho com `DELETE /orders/{id}`. Só use `/confirm` quando quiser um pedido real (é cobrado).

## Referências

- Documentação da API: https://developers.printful.com/docs/
- Catálogo público (sem token): `GET https://api.printful.com/products/509`
