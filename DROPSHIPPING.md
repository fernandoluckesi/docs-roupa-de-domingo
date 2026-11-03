# Dropshipping de estamparia

Não há estoque. Quando o pagamento é aprovado, o pedido é enviado ao parceiro de
estamparia, que imprime, embala e envia direto ao cliente (white label).

## Contrato (porta)

`modules/fulfillment/providers/print-provider.interface.ts`

```ts
export interface PrintProvider {
  readonly name: string;
  createOrder(input: CreatePrintOrderInput): Promise<PrintOrderResult>;
  getOrder(providerOrderId: string): Promise<PrintOrderResult>;
  quoteShipping(input: QuoteShippingInput): Promise<ShippingQuote[]>;
  cancelOrder(providerOrderId: string): Promise<void>;
}
```

```ts
interface CreatePrintOrderInput {
  externalId: string; // order.number
  recipient: {
    name;
    phone;
    document;
    zipCode;
    street;
    number;
    complement?;
    district;
    city;
    state;
  };
  items: Array<{
    sku: string;
    providerVariantId?: string;
    quantity: number;
    artworkUrl?: string;
    customText?: string;
  }>;
  shippingMethod: string;
}

interface PrintOrderResult {
  providerOrderId: string;
  status: "QUEUED" | "IN_PRODUCTION" | "SHIPPED" | "DELIVERED" | "ERROR";
  trackingCode?: string;
  trackingUrl?: string;
  raw: unknown;
}
```

Drivers são escolhidos por `PRINT_PROVIDER` (`mock` por padrão).

## Driver mock

- Gera `providerOrderId` (`MOCK-XXXXXXXX`) e devolve `QUEUED`.
- A cada consulta avança o status conforme o tempo decorrido (configurável via `PRINT_MOCK_SPEED`):
  `QUEUED → IN_PRODUCTION (+30s) → SHIPPED (+60s, com tracking) → DELIVERED (+120s)`.
- Cotação de frete por faixa de CEP + peso estimado por tipo de produto.

Isso permite ver a timeline do pedido evoluindo em desenvolvimento, sem parceiro real.

## Webhook do parceiro

`POST /api/fulfillment/webhook`

```json
{
  "external_id": "RD-7F3K9A",
  "provider_order_id": "MOCK-8KD92A1C",
  "status": "shipped",
  "tracking_code": "BR123456789BR",
  "tracking_url": "https://rastreamento.correios.com.br/app/index.php?objeto=BR123456789BR"
}
```

Protegido por `PRINT_WEBHOOK_SECRET` no header `x-print-signature`.
Atualiza `Fulfillment` e espelha no `Order` (`SHIPPED`/`DELIVERED` + `trackingCode` + `timeline`).

## Pesos e frete (tabela do mock)

| Produto         | Peso  | Observação          |
| --------------- | ----- | ------------------- |
| Camiseta        | 250 g |                     |
| Caneca          | 600 g | embalagem reforçada |
| Capa de celular | 120 g |                     |

| Faixa de CEP (1º dígito) | Região         | Econômico             | Expresso          |
| ------------------------ | -------------- | --------------------- | ----------------- |
| 0–1                      | SP             | 5–7 dias / R$ 14,90   | 2 dias / R$ 24,90 |
| 2–3                      | RJ/ES/MG       | 6–9 dias / R$ 17,90   | 3 dias / R$ 29,90 |
| 4–5                      | BA/SE/PE/AL/PB | 8–12 dias / R$ 22,90  | 4 dias / R$ 36,90 |
| 6–7                      | CE/PI/MA/N/CO  | 10–15 dias / R$ 26,90 | 5 dias / R$ 42,90 |
| 8–9                      | PR/SC/RS       | 6–9 dias / R$ 18,90   | 3 dias / R$ 31,90 |

Frete grátis acima de `FREE_SHIPPING_THRESHOLD_CENTS` (padrão R$ 249,00) ou com cupom `FREE_SHIPPING`.

## Trocar por um provider real

> Provider escolhido: **Printful**. Veja [PRINTFUL-API.md](PRINTFUL-API.md) (loja, IDs, chamadas e driver).

1. Criar `providers/<nome>-print.provider.ts` implementando `PrintProvider`.
2. Registrar no `FulfillmentModule` (factory por `PRINT_PROVIDER`).
3. Preencher `printProviderSku` / `printProviderVariantId` nos produtos e variantes.
4. Ajustar o parser do webhook para o formato do parceiro.

Nada no domínio (`orders`, `payments`) precisa mudar.
