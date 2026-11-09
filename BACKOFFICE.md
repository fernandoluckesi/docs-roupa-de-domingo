# Backoffice e operação de pedidos

Desde 09/11/2026 a loja produz, embala e posta os pedidos. Não há mais parceiro de print on demand.

A equipe trabalha no **backoffice** (`backoffice/`, app separado), que usa as rotas `/api/admin/*` do backend.

## Fluxo de um pedido

```
Pagamento aprovado ─▶ A produzir ─▶ Em produção ─▶ Embalado ─▶ Postado ─▶ Entregue
     (automático)       QUEUED       IN_PRODUCTION    PACKED     SHIPPED    DELIVERED
```

| Etapa | Quem move | O que acontece |
| --- | --- | --- |
| A produzir | sistema, quando o Mercado Pago aprova | o pedido entra na fila com o serviço (PAC/SEDEX) vindo do frete escolhido |
| Em produção | equipe | o pedido do cliente passa para "Em produção" |
| Embalado | equipe | registra peso e medidas da caixa; hora de imprimir a etiqueta |
| Postado | equipe, **com o código de rastreio** | o pedido fica "Enviado" e o cliente recebe um e-mail com o link de rastreio dos Correios |
| Entregue | equipe | começa a contar o prazo de arrependimento (7 dias, CDC art. 49) |

Regras:
- Dá para voltar um passo (Em produção → A produzir, Embalado → Em produção) para corrigir engano. Postado e Entregue não voltam.
- O rastreio aceita o formato dos Correios `AB123456789BR`. Pode ser corrigido depois da postagem.
- A "nota para o cliente" entra no histórico do pedido, que o cliente vê. A "nota interna" só a equipe vê.
- Pedido estornado ou cancelado sai da fila, mesmo que já tenha etapa aberta.
- Cancelar pela loja só vale para pedido **não pago**. Pedido pago é estornado pelo fluxo de devolução.

## Telas do backoffice

- **Painel:** a linha de produção com a contagem por etapa, os pedidos aguardando pagamento, os problemas (cancelado, estornado, recusado, devolução aberta) e as vendas de hoje e dos últimos 30 dias.
- **Pedidos:** abas por etapa, busca por número, nome ou e-mail, filtro de período e seleção em lote para imprimir etiquetas.
- **Detalhe do pedido:** endereço pronto para copiar, CPF mascarado (com botão para mostrar), itens com foto, variante e texto personalizado, pagamento, nota fiscal, controles da expedição e histórico.
- **Produção:** lista agregada por SKU (quantas peças de cada estampa, tamanho e cor) para a bancada, imprimível. Tem o botão "Iniciar produção de todos".
- **Etiquetas:**
  - etiqueta de endereço 10×15 cm (térmica) ou A4 com 4 por folha, com o código de barras do CEP e do rastreio;
  - Declaração de Conteúdo dos Correios, para quem envia sem nota fiscal;
  - romaneio de conferência.

## Etiquetas e Correios

O remetente sai das variáveis `SENDER_*` do backend: nome, CPF/CNPJ, telefone, e-mail e endereço com CEP. Sem elas, o backoffice mostra um aviso e a etiqueta sai sem remetente.

Hoje a etiqueta é de **endereçamento**: a postagem é feita no balcão ou com etiqueta comprada na agência, e o código de rastreio é digitado no backoffice.

Próximo passo opcional: contrato com os Correios e a API de pré-postagem (CWS). Com ela, o código de rastreio e a etiqueta oficial passam a ser gerados automaticamente na etapa "Embalado".

## Acesso

- A equipe fica na tabela **`admin_users`**, separada dos clientes (`users`): login próprio (`/api/admin/auth/login`), cookie próprio (`rd_admin_session`) e senha própria. Conta de cliente nunca abre o backoffice, e a sessão do backoffice não vale na loja.
- Depois da senha, o login pede um código de 6 dígitos enviado ao e-mail do admin (Resend). Por isso o SMTP do backend precisa estar configurado.
- Admins são criados pelo seed `seed:admin` do backend, que roda em todo deploy: com `ADMIN_EMAIL`, `ADMIN_NAME` e `ADMIN_INITIAL_PASSWORD` definidos, cria o admin se ele ainda não existir (a senha nunca fica no código). Depois do primeiro deploy, apague `ADMIN_INITIAL_PASSWORD`.
- Toda chamada de admin fica na trilha de auditoria, inclusive as leituras, porque acessam dado pessoal. Os eventos da expedição estão em [AUDITORIA.md](AUDITORIA.md).

## API (backend)

| Rota | Uso |
| --- | --- |
| `GET /api/admin/orders/summary` | contagens do painel |
| `GET /api/admin/orders?stage=&q=&from=&to=&page=` | lista por etapa (`to_produce`, `in_production`, `packed`, `shipped`, `delivered`, `awaiting_payment`, `issues`, `all`) |
| `GET /api/admin/orders/:number` | pedido completo |
| `PATCH /api/admin/orders/:number/fulfillment` | etapa, rastreio, serviço, peso e medidas, notas |
| `POST /api/admin/orders/:number/cancel` | cancela pedido não pago |
| `POST /api/admin/orders/labels` | dados das etiquetas e da declaração; marca como impressas |
| `GET /api/admin/orders/production-list?stage=` | lista de produção por SKU |
| `GET /api/admin/shipping/sender` | remetente configurado |
