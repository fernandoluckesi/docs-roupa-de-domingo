# Integração Mercado Pago — Checkout Pro

## Estratégia

Usamos **Checkout Pro**: o backend cria uma `Preference` e devolve o `init_point`;
o frontend faz `window.location.href = initPoint`, levando o cliente para a tela
real de pagamento do Mercado Pago (cartão, Pix, boleto). Nenhum dado de cartão
passa pela nossa aplicação.

Dois drivers, selecionados por `PAYMENT_DRIVER`:

| Driver        | Quando usar                           | Comportamento                                                                                 |
| ------------- | ------------------------------------- | --------------------------------------------------------------------------------------------- |
| `mercadopago` | com `MP_ACCESS_TOKEN` real            | chama a API do MP e devolve o `init_point` (ou `sandbox_init_point` se `MP_USE_SANDBOX=true`) |
| `mock`        | desenvolvimento local sem credenciais | devolve uma URL interna do frontend que simula a tela do MP e permite aprovar/rejeitar        |

## Fluxo

```
Frontend                Backend                      Mercado Pago
   │  POST /api/orders     │                               │
   ├──────────────────────►│ cria Order PENDING            │
   │                       │ cria Payment PENDING          │
   │                       │  POST /checkout/preferences   │
   │                       ├──────────────────────────────►│
   │                       │◄── id, init_point ────────────┤
   │◄── { order, paymentUrl } ──┤                          │
   │  window.location = paymentUrl                         │
   ├──────────────────────────────────────────────────────►│  cliente paga
   │◄── redirect back_urls ────────────────────────────────┤
   │  GET /pagamento/sucesso?external_reference=RD-XXXX    │
   │                       │◄── POST /api/payments/webhook ┤
   │                       │  GET /v1/payments/:id ───────►│
   │                       │  Order PAID + print job       │
   │  GET /api/orders/RD-XXXX (polling na tela de retorno) │
```

## Preference enviada

```json
{
  "external_reference": "RD-7F3K9A",
  "statement_descriptor": "ROUPADEDOMINGO",
  "items": [
    {
      "id": "CAM-ACID-M-PRETA",
      "title": "Camiseta — Sorria, é de graça (o resto não)",
      "description": "Tamanho M · Preta",
      "category_id": "fashion",
      "quantity": 1,
      "currency_id": "BRL",
      "unit_price": 89.9
    },
    {
      "id": "SHIPPING",
      "title": "Frete — Sedex",
      "quantity": 1,
      "currency_id": "BRL",
      "unit_price": 24.9
    }
  ],
  "payer": {
    "name": "Maria",
    "surname": "Souza",
    "email": "cliente@roupadedomingo.com",
    "identification": { "type": "CPF", "number": "12345678909" },
    "address": {
      "zip_code": "01310100",
      "street_name": "Av. Paulista",
      "street_number": "1000"
    }
  },
  "back_urls": {
    "success": "http://localhost:5273/pagamento/sucesso",
    "pending": "http://localhost:5273/pagamento/pendente",
    "failure": "http://localhost:5273/pagamento/falha"
  },
  "auto_return": "approved",
  "notification_url": "https://SEU_TUNEL/api/payments/webhook",
  "expires": true,
  "expiration_date_to": "<agora + 24h>",
  "metadata": { "orderNumber": "RD-7F3K9A", "source": "roupa-de-domingo-web" }
}
```

Desconto de cupom entra como item negativo não é permitido pelo MP, então o
desconto é aplicado **rateado no preço unitário dos itens** antes de montar a
preference — o total da preference sempre fecha com `order.totalCents`.

## Webhook

`POST /api/payments/webhook`

O MP envia `{ "type": "payment", "data": { "id": "123456" } }` (ou `topic=payment`
em querystring). O handler:

1. Extrai o `paymentId`.
2. Faz `GET https://api.mercadopago.com/v1/payments/{id}` com o access token — **nunca** confia no payload.
3. Lê `external_reference` → localiza a `Order`.
4. Mapeia o status:

| MP status                               | Payment    | Order                    |
| --------------------------------------- | ---------- | ------------------------ |
| `approved`                              | APPROVED   | PAID → dispara print job |
| `pending` / `in_process` / `authorized` | IN_PROCESS | PENDING                  |
| `rejected`                              | REJECTED   | FAILED                   |
| `cancelled`                             | CANCELLED  | CANCELLED                |
| `refunded` / `charged_back`             | REFUNDED   | REFUNDED                 |

5. Salva `rawPayload`, responde **200** sempre (o MP reenvia em caso de erro; erro nosso não deve gerar retry infinito em loop de falha lógica).
6. Idempotente: se o pedido já está `PAID` com o mesmo `providerPaymentId`, não reprocessa.

### Notificação em ambiente local

O MP não alcança `localhost`. Opções:

- `ngrok http 3333` e colocar a URL pública em `MP_NOTIFICATION_URL`;
- ou usar `PAYMENT_DRIVER=mock` e aprovar manualmente:

```bash
curl -X POST http://localhost:3333/api/payments/mock/RD-7F3K9A/approve
```

## Credenciais

```env
PAYMENT_DRIVER=mercadopago
MP_ACCESS_TOKEN=TEST-0000000000000000-000000-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-000000000
MP_PUBLIC_KEY=TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MP_USE_SANDBOX=true
MP_NOTIFICATION_URL=https://seu-tunel.ngrok.io/api/payments/webhook
```

Pegue em [Mercado Pago Developers → Suas integrações → Credenciais](https://www.mercadopago.com.br/developers/panel/app).

## Cartões de teste (sandbox)

| Bandeira   | Número              | CVV | Validade |
| ---------- | ------------------- | --- | -------- |
| Mastercard | 5031 4332 1540 6351 | 123 | 11/30    |
| Visa       | 4235 6477 2802 5682 | 123 | 11/30    |

Nome do titular define o resultado: `APRO` aprova, `OTHE` recusa por erro geral,
`CONT` deixa pendente. CPF de teste: `12345678909`.

> Conteúdo reescrito a partir da documentação pública do Mercado Pago para fins de integração.
