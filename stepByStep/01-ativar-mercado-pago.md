# Passo a passo — Ativar o Mercado Pago como meio de pagamento

## Resumo da situação

A integração com o Mercado Pago (Checkout Pro) **já está implementada** no projeto.
O que falta é apenas **colar as credenciais reais**.

O `refs/RD/.env` já está com todas as variáveis criadas e valores mock de
placeholder. O driver está em `PAYMENT_DRIVER=mock` de propósito: com
`mercadopago` e um token falso, a API do MP responde 401 e o checkout quebra.
Hoje o fluxo usa a tela simulada em `/pagamento/simulado/:orderNumber`.

O que já existe no código:

| Peça                                                                  | Onde                                                                  |
| --------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Criação da `Preference` (items, payer, back_urls, external_reference) | `backend/src/modules/payments/mercado-pago.service.ts`                |
| Seleção do driver (`mercadopago` vs `mock`)                           | `PaymentsService.driver` / `MercadoPagoService.isConfigured`          |
| Webhook `POST /api/payments/webhook` com reconsulta na API do MP      | `payments.controller.ts` + `PaymentsService.handleMercadoPagoWebhook` |
| Mapa de status MP → `PaymentStatus` / `OrderStatus`, idempotente      | `mapMpStatus` + `applyPaymentSnapshot`                                |
| Disparo do print job na aprovação                                     | `applyPaymentSnapshot` → `fulfillment.dispatchOrder`                  |
| Redirecionamento para o `init_point`                                  | `frontend/src/pages/Checkout.tsx`                                     |
| Páginas de retorno sucesso / pendente / falha                         | `frontend/src/pages/PaymentResult.tsx` + rotas no `App.tsx`           |
| Repasse das variáveis para o container                                | `docker-compose.yml` (serviço `backend`, linhas 50-54)                |

Portanto: **não é preciso escrever código.** Siga os passos abaixo.

---

## Passo 1 — Criar a aplicação no Mercado Pago

1. Acesse [Mercado Pago Developers → Suas integrações](https://www.mercadopago.com.br/developers/panel/app)
   e faça login com a conta que vai receber os pagamentos.
2. Clique em **Criar aplicação**.
3. Preencha:
   - **Nome**: `Roupa de Domingo`
   - **Produto a integrar**: `Pagamentos online` → **Checkout Pro**
   - **Modelo de integração**: produtos/serviços próprios (não marketplace)
4. Salve. Você cai no painel da aplicação.

## Passo 2 — Copiar as credenciais de teste

No painel da aplicação, vá em **Credenciais de teste** e copie:

- `Public Key` → começa com `TEST-`
- `Access Token` → começa com `TEST-`

> Use **sempre** as credenciais de teste primeiro. As de produção cobram de
> verdade. A troca para produção está no Passo 7.

## Passo 3 — Expor o backend para receber o webhook

O Mercado Pago não alcança `localhost`. Sem túnel, o pedido fica travado em
`PENDING` porque a notificação nunca chega.

Em um terminal separado, deixe rodando:

```bash
ngrok http 3333
```

Copie a URL `https://...ngrok-free.app` que aparecer. Ela muda a cada reinício do
ngrok no plano gratuito — se reiniciar, atualize o `.env` e recrie o backend.

> Não tem ngrok? Alternativas: `cloudflared tunnel --url http://localhost:3333`
> ou validar o fluxo com `PAYMENT_DRIVER=mock` (sem Mercado Pago real).

## Passo 4 — Substituir os placeholders no `.env` da raiz

As variáveis já existem em `refs/RD/.env`. Só troque os valores mock pelos reais:

| Variável              | Valor atual (mock)                        | Trocar por                                     |
| --------------------- | ----------------------------------------- | ---------------------------------------------- |
| `PAYMENT_DRIVER`      | `mock`                                    | `mercadopago`                                  |
| `MP_ACCESS_TOKEN`     | `TEST-0000...-000000000`                  | o Access Token de teste do Passo 2             |
| `MP_PUBLIC_KEY`       | `TEST-00000000-0000-...`                  | a Public Key de teste do Passo 2               |
| `MP_USE_SANDBOX`      | `true`                                    | mantenha `true` enquanto usar credencial TEST- |
| `MP_NOTIFICATION_URL` | `https://changeme.ngrok-free.app/api/...` | a URL do ngrok do Passo 3 + mesmo caminho      |

Pontos de atenção:

- `PAYMENT_DRIVER=mercadopago` **e** `MP_ACCESS_TOKEN` válido: os dois são
  exigidos por `MercadoPagoService.isConfigured`. Se faltar um, o sistema volta
  silenciosamente para o mock (aparece um `WARN` no log).
- `MP_USE_SANDBOX=true` faz o backend devolver o `sandbox_init_point`, que é o
  que funciona com credenciais `TEST-`.
- Mantenha `MP_NOTIFICATION_URL` terminando em `/api/payments/webhook`; troque
  apenas o host.
- O `.env` não é versionado. Não comite credenciais e não coloque chaves em
  `docs/keys.txt`.

## Passo 5 — Recriar o backend

```bash
cd refs/RD
docker compose up -d --force-recreate backend
```

As variáveis são lidas na subida do processo; editar o `.env` sem recriar o
container não tem efeito.

Confirme que o driver virou real:

```bash
curl http://localhost:3333/api/payments/config
```

Esperado:

```json
{
  "driver": "mercadopago",
  "simulated": false,
  "message": "Checkout Pro ativo. O cliente e redirecionado para o Mercado Pago."
}
```

Se vier `"driver": "mock"`, revise o Passo 4 e veja o log:
`docker compose logs -f backend`.

## Passo 6 — Testar a compra ponta a ponta

1. Abra http://localhost:5273 e adicione um item ao carrinho.
2. Informe o CEP (ex. `01310-100`) para calcular o frete.
3. Em `/checkout`, preencha os dados (CPF de teste: `12345678909`) e clique em
   **Pagar com Mercado Pago**.
4. Você deve ser levado para o domínio `mercadopago.com.br` (não para
   `/pagamento/simulado/...`).
5. Pague com um cartão de teste, usando o **nome do titular** para controlar o
   resultado:

   | Resultado desejado | Nome do titular | Cartão                           | CVV | Validade |
   | ------------------ | --------------- | -------------------------------- | --- | -------- |
   | Aprovado           | `APRO`          | Mastercard `5031 4332 1540 6351` | 123 | 11/30    |
   | Recusado           | `OTHE`          | Visa `4235 6477 2802 5682`       | 123 | 11/30    |
   | Pendente           | `CONT`          | qualquer um acima                | 123 | 11/30    |

6. Após aprovar, o MP redireciona para `/pagamento/sucesso?external_reference=RD-XXXXXX`.
7. Verifique no terminal do ngrok que chegou um `POST /api/payments/webhook` com
   status 200, e confira o pedido:

```bash
curl http://localhost:3333/api/payments/RD-XXXXXX/status
```

O pedido deve estar `PAID` com o pagamento `APPROVED`, e o print job já disparado
para a Printful (hoje em modo rascunho, porque `PRINTFUL_CONFIRM_ORDERS=false`).

## Passo 7 — Ir para produção (quando for cobrar de verdade)

1. No painel do Mercado Pago, complete a **homologação** da aplicação (dados da
   empresa, política de privacidade, testes obrigatórios). Sem isso as
   credenciais de produção não liberam.
2. Troque no `.env` do ambiente real (Railway — ver `docs/RAILWAY.md`):

```env
PAYMENT_DRIVER=mercadopago
MP_ACCESS_TOKEN=APP_USR-...
MP_PUBLIC_KEY=APP_USR-...
MP_USE_SANDBOX=false
MP_NOTIFICATION_URL=https://api.seudominio.com/api/payments/webhook
```

3. `MP_USE_SANDBOX=false` passa a usar o `init_point` real.
4. `FRONTEND_URL` precisa ser o domínio público: ele monta as `back_urls` da
   preference. Com `auto_return: "approved"` o MP **rejeita** a preference se a
   URL de sucesso não for alcançável publicamente.
5. Cadastre a URL do webhook também em **Suas integrações → Webhooks**, evento
   `payment`, para ter reenvio e histórico de notificações no painel.

---

## Como voltar para o modo simulado

Para desenvolver sem depender do MP, basta:

```env
PAYMENT_DRIVER=mock
```

e `docker compose up -d --force-recreate backend`. O checkout volta para a tela
simulada, e você pode aprovar via API:

```bash
curl -X POST http://localhost:3333/api/payments/mock/RD-XXXXXX/approve
```

(Os endpoints `mock/*` ficam bloqueados com o MP real configurado — `simulate()`
lança `BadRequestException`.)

---

## Problemas comuns

**`Nao foi possivel iniciar o pagamento no Mercado Pago`** no checkout.
Veja `docker compose logs backend`: o erro real da API do MP é logado. Causas
frequentes: token inválido/expirado, `auto_return` com `back_urls` inacessível,
ou valor de item com mais de 2 casas decimais.

**Erro de certificado (`SELF_SIGNED_CERT_IN_CHAIN`) ao chamar a API do MP.**
Rede corporativa com TLS interceptado. Gere o bundle de CAs:

```powershell
cd refs\RD
powershell -ExecutionPolicy Bypass -File scripts\export-corporate-ca.ps1
```

O compose já monta `certs/corporate-ca.pem` em `NODE_EXTRA_CA_CERTS`. Depois,
recrie o backend.

**Pagamento aprovado no MP mas pedido continua `PENDING`.**
O webhook não chegou. Confirme que o ngrok está no ar, que `MP_NOTIFICATION_URL`
tem o caminho completo `/api/payments/webhook` e que a URL no `.env` é a do túnel
atual. Você pode forçar o reenvio pelo painel do MP em **Webhooks → Notificações**.

**O webhook responde 200 mas `processed: false`.**
É o comportamento proposital para não gerar retry infinito. O motivo vai no log:
pagamento sem `external_reference` correspondente, ou credencial ausente.

**Redireciona para `/pagamento/simulado/...` mesmo com credenciais.**
`PAYMENT_DRIVER` ainda está `mock`, o token está vazio, ou o container não foi
recriado após editar o `.env`.

---

## Referências

- [Checkout Pro — Mercado Pago Developers](https://www.mercadopago.com.br/developers/pt/docs/checkout-pro/landing)
- [Notificações Webhooks](https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks)
- [Cartões de teste](https://www.mercadopago.com.br/developers/pt/docs/checkout-pro/additional-content/your-integrations/test/cards)
- Documentação interna: [`../MERCADO-PAGO.md`](../MERCADO-PAGO.md) e [`../COMO-RODAR.md`](../COMO-RODAR.md)

> Trechos da documentação pública do Mercado Pago foram reescritos para adequação
> às restrições de licenciamento de conteúdo.
