# Trilha de auditoria

Tudo que importa para segurança, para o cliente e para o caixa fica registrado na tabela `audit_logs`:

- quem fez a ação (cliente, admin, parceiro ou sistema);
- o que foi feito e sobre qual alvo;
- quando e de onde (hash do IP, user-agent e id da requisição);
- se deu certo ou falhou.

Serve para investigar um incidente, responder a uma reclamação ou chargeback e provar o que aconteceu com um pedido.

## Como funciona

- **`AuditService.record()`**: os services chamam esse método nos pontos de negócio. A gravação é assíncrona e uma falha só vira log, então a auditoria nunca derruba nem atrasa a operação principal.
- **`AuditInterceptor`**: grava automaticamente toda rota `@Roles(ADMIN)`, inclusive as leituras, com o corpo da requisição mascarado.
- **Contexto da requisição**: um middleware guarda a requisição atual (`AsyncLocalStorage`), e assim o service sabe quem é o usuário logado, o IP e o `X-Request-Id` sem receber isso como parâmetro.
  - O cabeçalho `X-Request-Id` volta em toda resposta. Com ele dá para cruzar a trilha com os logs do Railway.

## Quem aparece como autor (`actorType`)

| Tipo | Quando |
| --- | --- |
| `CUSTOMER` | cliente logado, ou a própria conta no login e no cadastro |
| `ADMIN` | equipe; só nesse caso o e-mail é gravado (`actorEmail`) |
| `ANONYMOUS` | requisição sem login (convidado, "esqueci a senha", login que falhou) |
| `PROVIDER` | webhook de parceiro (Mercado Pago) |
| `SYSTEM` | rotina interna (limpeza por retenção) |

## Eventos

O alvo de todo evento de pedido é o **número do pedido** (`targetType = order`). Os eventos de conta usam o id do usuário (`targetType = user`).

**Segurança e acesso** (`AUTH`)

| Evento | Detalhes gravados |
| --- | --- |
| `auth.register`, `auth.register.confirmed` | versão dos termos, opt-in de marketing |
| `auth.login.success` | se o login passou pelo código por e-mail (admin) |
| `auth.login.failed` | motivo (`invalid_credentials`, `account_locked`, `email_not_verified`, `login_code_invalid`), se a conta existe, hash do e-mail digitado |
| `auth.account.locked` | tentativas e minutos de bloqueio |
| `auth.logout`, `auth.sessions.revoked` | — |
| `auth.code.sent`, `auth.code.failed`, `auth.code.locked` | finalidade do código (`register`, `email-change`, `password-change`, `password-reset`, `login`), tentativas |
| `auth.password.change_requested`, `auth.password.changed`, `auth.password.change_failed` | — |
| `auth.password.reset_requested`, `auth.password.reset` | método (código ou link antigo) |
| `auth.email.change_requested`, `auth.email.changed`, `auth.email.change_failed` | e-mails antigo e novo, mascarados |
| `auth.email.verified` | — |

**Conta** (`ACCOUNT`)

| Evento | Detalhes gravados |
| --- | --- |
| `account.profile.updated` | só os nomes dos campos alterados, nunca os valores |
| `account.address.created`, `account.address.updated`, `account.address.deleted` | id do endereço |
| `account.deleted`, `account.delete_failed` | motivo da falha (senha errada, pedido em andamento) |

**Privacidade** (`PRIVACY`)

| Evento | Detalhes gravados |
| --- | --- |
| `privacy.data.exported` | quantos pedidos e endereços |
| `privacy.consent.changed` | tipo de consentimento e escolha |

**Pedidos** (`ORDER`)

| Evento | Detalhes gravados |
| --- | --- |
| `order.created` | itens, valores, cupom, frete, UF, versão dos termos, se é convidado |
| `order.checkout_blocked` | antifraude: pedidos pendentes demais |
| `order.status_changed` | `from` → `to` e a origem: `customer_cancel`, `admin_cancel`, `payment`, `fulfillment` ou `return` |
| `order.cancel_failed` | — |
| `order.coupon_redeemed` | cupom e desconto |

**Pagamentos** (`PAYMENT`)

| Evento | Detalhes gravados |
| --- | --- |
| `payment.checkout_created` | provedor, preferência, valor |
| `payment.status_changed` | `from` → `to`, status do provedor, id do pagamento, método, parcelas, valor; origem `webhook` ou `simulation` |
| `payment.amount_mismatch` | valor pago diferente do pedido (pedido não é liberado) |
| `payment.webhook.rejected` | assinatura inválida |
| `payment.webhook.failed` | erro ao processar |
| `payment.orphaned` | pagamento sem pedido |
| `payment.refunded`, `payment.refund_failed` | valor, total ou parcial, protocolo da devolução |

**Entrega** (`FULFILLMENT`)

| Evento | Detalhes gravados |
| --- | --- |
| `fulfillment.queued` | pagamento aprovado, pedido entrou na fila de produção; serviço (PAC/SEDEX) |
| `fulfillment.status_changed` | `from` → `to` (A produzir → Em produção → Embalado → Postado → Entregue), código de rastreio, campos alterados |
| `fulfillment.updated` | nomes dos campos de embalagem, rastreio ou nota interna que mudaram, sem os valores |

**Trocas e devoluções** (`RETURN`)

| Evento | Detalhes gravados |
| --- | --- |
| `return.requested` | protocolo, tipo, itens, dias desde a entrega |
| `return.status_changed` | `from` → `to`, código de postagem, valor do reembolso |

**Nota fiscal** (`INVOICE`)

| Evento | Detalhes gravados |
| --- | --- |
| `invoice.issued` | número, série, valor |
| `invoice.failed` | erro |

**SAC** (`CONTACT`)

| Evento | Detalhes gravados |
| --- | --- |
| `contact.created` | protocolo, assunto, número do pedido |
| `contact.status_changed` | `from` → `to` |

**Admin e sistema**

| Evento | Detalhes gravados |
| --- | --- |
| `admin.<Modulo>.<acao>` (`ADMIN`) | toda rota de admin: método, rota, status HTTP, corpo mascarado |
| `audit.retention.purged` (`SYSTEM`) | quantos registros a limpeza apagou |
| `admin.seed.created`, `admin.seed.password_reset` (`SYSTEM`) | admin do backoffice criado (ou senha redefinida) pelo `seed:admin` |
| `admin.login.success`, `admin.login.failed`, `admin.login.code_sent`, `admin.account.locked` (`AUTH`) | login do backoffice (tabela `admin_users`): motivo da falha, tentativas, hash do e-mail digitado |

## Proteção dos dados (LGPD)

- **Cliente fica pseudonimizado.** O registro guarda só o id do cliente, nunca o e-mail. Quando a conta é excluída, a trilha continua apontando para um id anonimizado.
- **Detalhes mascarados.** Tudo que vai em `payload` passa por `redact()`, que esconde CPF, e-mail, telefone, endereço, senha, token e código.
- **Texto livre fica fora da trilha.** O motivo da devolução, a mensagem do SAC e o motivo da exclusão ficam só na tabela de origem, porque podem conter dado pessoal.
- **IP só em hash.** A rota é gravada sem query string.
- **Login com e-mail desconhecido** grava só o hash do e-mail digitado. Assim dá para identificar um ataque de lista de senhas sem guardar o e-mail.

## Imutabilidade e retenção

- Um trigger no Postgres bloqueia qualquer `UPDATE` em `audit_logs`, então registro gravado não muda.
- A limpeza por prazo usa `DELETE` e roda 1 minuto depois do boot e depois uma vez por dia.
- O prazo é `AUDIT_RETENTION_DAYS`.
  - Padrão: **1825 dias** (5 anos), que cobre a prescrição do CDC (art. 27) e o prazo fiscal.
  - Mínimo forçado: **183 dias**, por causa do Marco Civil da Internet (art. 15).

## Consultar

A rota é `GET /api/admin/audit-logs` (admin com 2FA), e a própria consulta também fica auditada.

| Filtro | Descrição |
| --- | --- |
| `category`, `outcome`, `actorType` | valores dos enums |
| `action` | prefixo, ex.: `auth.login` ou `payment.` |
| `actorId` | tudo que um usuário fez |
| `targetType` + `targetId` | ex.: `order` + `RD-5YCFQP` dá a história completa do pedido |
| `requestId` | tudo de uma requisição |
| `from`, `to` | período (ISO 8601) |
| `page`, `pageSize` | `pageSize` vai até 200 |

**Exemplos:**

```
GET /api/admin/audit-logs?targetType=order&targetId=RD-5YCFQP
GET /api/admin/audit-logs?action=auth.login.failed&from=2026-11-01T00:00:00Z
GET /api/admin/audit-logs?category=PAYMENT&outcome=FAILURE
```

## Como adicionar um evento

Injete `AuditService`. O módulo é global, então não precisa importar.

```ts
this.audit.record({
  category: AuditCategory.ORDER,
  action: "order.algo_aconteceu",
  target: { type: "order", id: order.number },
  data: { from, to },
});
```

Siga o padrão `dominio.acao` e coloque em `data` só o necessário: nada de texto livre nem dado pessoal sem máscara.
