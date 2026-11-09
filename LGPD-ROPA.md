# Registro das Operações de Tratamento (ROPA)

LGPD, art. 37: o controlador mantém registro das operações de tratamento de dados
pessoais. Este é o registro do Roupa de Domingo, mantido junto com o código para
não envelhecer separado dele. Revisar sempre que um campo, provedor ou finalidade mudar.

| Campo | Valor |
| --- | --- |
| Controlador | Roupa de Domingo Comércio de Vestuário Ltda. (dados provisórios em `frontend/src/config/company.ts`) |
| Encarregado (DPO) | Equipe de Privacidade, privacidade@roupadedomingo.com.br |
| Última revisão | 04/11/2026 |

## Operações

| # | Operação | Titulares | Dados | Finalidade | Base legal (art. 7º) | Retenção | Compartilhamento | Onde no sistema |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Cadastro e conta | Clientes | nome, e-mail, telefone, CPF (opcional), hash da senha | criar e manter a conta | V, execução de contrato | até a exclusão da conta | Railway (hospedagem) | `users` |
| 2 | Endereços | Clientes | destinatário, CEP, endereço | entrega dos pedidos | V | até o cliente remover ou excluir a conta | Railway | `addresses` |
| 3 | Pedido e entrega | Clientes e convidados | nome, e-mail, telefone, CPF, endereço, itens | vender, produzir e entregar | V | 5 anos (obrigação fiscal, art. 16, I) | Correios (nome, endereço, conteúdo e valor declarado na etiqueta), Railway | `orders`, `order_items`, `fulfillments`; equipe acessa pelo backoffice (acesso auditado) |
| 4 | Pagamento | Compradores | nome, e-mail, CPF, valor | cobrar o pedido | V | 5 anos; guardamos só status, método, parcelas, valor e ids | Mercado Pago | `payments` (payload minimizado) |
| 5 | Nota fiscal | Compradores | nome, CPF, endereço, itens, valores | obrigação fiscal | II, obrigação legal | 5 anos | emissor de NF-e (a contratar), SEFAZ | `invoices` |
| 6 | Trocas e devoluções | Compradores | pedido, itens, motivo | direito de arrependimento e vício (CDC) | II e V | 5 anos (prescrição do CDC, art. 27) | Correios (postagem reversa) | `return_requests` |
| 7 | SAC | Qualquer pessoa | nome, e-mail, mensagem, nº do pedido | atendimento (Decreto 7.962, art. 4º) | V e IX (legítimo interesse em responder) | 5 anos | provedor de e-mail | `contact_messages` |
| 8 | Prova de consentimento | Clientes e visitantes | versão aceita, escolha, data, hash do IP, user-agent | comprovar consentimento (art. 8º, §2º) | II | 5 anos | — | `consent_records` |
| 9 | Marketing por e-mail | Clientes que optaram | nome, e-mail | novidades e ofertas | I, consentimento (revogável em Minha conta) | até revogar | provedor de e-mail | `users.marketingOptIn` |
| 10 | Segurança da conta | Clientes | tentativas de login, tokens de e-mail (hash), segredo 2FA (cifrado) | evitar fraude e invasão | IX, legítimo interesse; II | tokens: até o uso ou 48h; bloqueio: 15 min | — | `users`, `auth_tokens` |
| 11 | Trilha de auditoria | Clientes, convidados e administradores | evento, id do cliente (e-mail só de admin), alvo, hash do IP, user-agent, detalhes mascarados | segurança da conta, prova de pedidos, pagamentos e trocas, rastrear acesso a dados pessoais | II, VI (defesa em processo) e IX | 5 anos (`AUDIT_RETENTION_DAYS`, mínimo 6 meses) | — | `audit_logs` ([AUDITORIA.md](./AUDITORIA.md)) |
| 12 | Registros de acesso | Visitantes | IP, data/hora, rota | Marco Civil da Internet, art. 15 | II | 6 meses | Railway (logs da plataforma) | logs do Railway |
| 13 | Carrinho e troféus de convidado | Visitantes | id de sessão aleatório | carrinho sem cadastro | V e IX | até limpar o navegador | — | `carts`, `easter_egg_discoveries` |

## Transferência internacional (art. 33)

- **Railway Corporation (EUA):** hospedagem. Mesma pendência contratual.

## Medidas de segurança (art. 46)

- CPF e segredo 2FA cifrados em repouso (AES-256-GCM).
- Senhas com bcrypt (custo 12) e política mínima.
- Sessão em cookie httpOnly + SameSite=Lax, CSRF por cabeçalho, revogação de sessões.
- Rate limit, bloqueio após 5 tentativas e 2FA obrigatório para administradores.
- Logs e auditoria com dados mascarados.
- Cabeçalhos de segurança: helmet, CSP, HSTS e Referrer-Policy.
- Backups com restauração testada (`backend/scripts/backup`).
- `npm audit` e varredura de segredos no CI.

## Direitos do titular (art. 18)

Atendidos em Minha conta → Privacidade e dados:

- exportação em JSON, que cobre confirmação, acesso, portabilidade e compartilhamento;
- correção dos dados;
- revogação do marketing;
- exclusão com anonimização.

Também pelo e-mail do encarregado. O prazo de resposta é de 15 dias.
