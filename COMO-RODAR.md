# Como rodar — Roupa de Domingo

## Pré-requisitos

Docker Desktop (Compose v2). Nada mais: Node e Postgres rodam dentro dos containers.

### Rede corporativa com proxy (passo obrigatório nesse caso)

Se a sua rede intercepta TLS, o `npm install` **dentro do container** falha com
`SELF_SIGNED_CERT_IN_CHAIN`: o Windows confia na CA do proxy, o Node do container
não. Gere o bundle de certificados antes do primeiro build:

```powershell
cd refs\RD
powershell -ExecutionPolicy Bypass -File scripts\export-corporate-ca.ps1
```

Isso cria `certs/corporate-ca.pem` (não versionado), que os Dockerfiles montam via
`NODE_EXTRA_CA_CERTS` durante a instalação de dependências. Em rede sem proxy o
passo é inofensivo; basta que o diretório `certs/` exista.

## Subir tudo

```bash
cd refs/RD
docker compose up --build
```

Na primeira execução o backend aplica a migration e roda o seed automaticamente.
O build leva alguns minutos; a API só responde depois do `migrate deploy` + `seed`.

| Serviço  | URL                                                       |
| -------- | --------------------------------------------------------- |
| Loja     | http://localhost:5273                                     |
| API      | http://localhost:3333/api                                 |
| Swagger  | http://localhost:3333/api/docs                            |
| Health   | http://localhost:3333/health                              |
| Postgres | localhost:5432 (`domingo` / `domingo` / `roupadedomingo`) |

> A loja usa a porta **5273**, não a 5173 padrão do Vite, para não conflitar com
> outros projetos rodando no host. Mude com `FRONTEND_PORT` no `.env`.

Parar: `Ctrl+C` e depois `docker compose down`.
Zerar o banco: `docker compose down -v`.

## Validar automaticamente

```bash
bash scripts/smoke-test.sh
```

São 30 asserções cobrindo catálogo, carrinho, cupom, frete, checkout, aprovação de
pagamento, print job da estamparia, easter eggs, autenticação e autorização.

## Credenciais de demonstração

| Perfil  | E-mail                       | Senha        |
| ------- | ---------------------------- | ------------ |
| Cliente | `cliente@roupadedomingo.com` | `domingo123` |
| Admin   | `admin@roupadedomingo.com`   | `domingo123` |

Cupons públicos: `DOMINGO10` (10%) e `FRETEGRATIS` (acima de R$ 149).
Os cupons secretos saem dos easter eggs.

## Fluxo de compra sem credenciais do Mercado Pago (padrão)

`PAYMENT_DRIVER=mock`. O pedido é criado normalmente, mas o redirecionamento
vai para a tela `/pagamento/simulado/:orderNumber`, que imita o Checkout Pro e
permite aprovar, recusar ou deixar pendente.

1. Adicione itens ao carrinho.
2. Informe o CEP (ex. `01310-100`) para calcular o frete.
3. Finalize em `/checkout` e clique em **Pagar com Mercado Pago**.
4. Na tela simulada, escolha **Pagar e aprovar**.
5. O backend marca o pedido como `PAID` e envia o print job à estamparia mock.
6. Em `/conta/pedidos/:number`, use **Atualizar status da produção** para ver a timeline avançar.

O mock avança sozinho com o tempo: `QUEUED → IN_PRODUCTION` (30s) `→ SHIPPED` (60s)
`→ DELIVERED` (120s). Para acelerar, suba com `PRINT_MOCK_SPEED=10`.

Aprovar via API, sem passar pela tela:

```bash
curl -X POST http://localhost:3333/api/payments/mock/RD-XXXXXX/approve
```

## Fluxo com Mercado Pago real (sandbox)

1. Crie uma aplicação em [Mercado Pago Developers](https://www.mercadopago.com.br/developers/panel/app) e copie as credenciais de teste.
2. Crie `refs/RD/.env` a partir de `.env.example`:

```env
PAYMENT_DRIVER=mercadopago
MP_ACCESS_TOKEN=TEST-xxxxxxxxxxxx
MP_PUBLIC_KEY=TEST-xxxxxxxxxxxx
MP_USE_SANDBOX=true
```

3. Para receber o webhook no localhost, exponha a API:

```bash
ngrok http 3333
```

E coloque a URL pública no `.env`:

```env
MP_NOTIFICATION_URL=https://SEU-ID.ngrok-free.app/api/payments/webhook
```

4. `docker compose up -d --force-recreate backend`

Agora o botão do checkout leva para a tela real do Mercado Pago. Use os
[cartões de teste](./MERCADO-PAGO.md#cartões-de-teste-sandbox) com nome do
titular `APRO` para aprovar.

## Rodar fora do Docker

```bash
# Postgres
docker compose up -d postgres

# Backend
cd backend-roupa-de-domingo
copy .env.example .env    # ajuste DATABASE_URL para @localhost:5432
npm install
npx prisma generate
npm run db:setup          # migrate deploy + seed
npm run start:dev

# Frontend (outro terminal)
cd frontend-roupa-de-domingo
copy .env.example .env
npm install
npm run dev
```

## Comandos úteis

| Objetivo              | Comando                                                          |
| --------------------- | ---------------------------------------------------------------- |
| Logs do backend       | `docker compose logs -f backend`                                 |
| Shell no backend      | `docker compose exec backend sh`                                 |
| Reaplicar o seed      | `docker compose exec backend npm run seed`                       |
| Prisma Studio         | `docker compose exec backend npx prisma studio`                  |
| psql                  | `docker compose exec postgres psql -U domingo -d roupadedomingo` |
| Rebuild de um serviço | `docker compose up -d --build backend`                           |

## Smoke test manual

- [ ] `GET /health` responde `status: ok` com `database: up`
- [ ] Home carrega vitrine e categorias
- [ ] Catálogo filtra por categoria, humor e busca; paginação funciona
- [ ] Página de produto troca variante e o preço acompanha
- [ ] Adicionar ao carrinho atualiza o contador no header
- [ ] CEP calcula frete; econômico vs. expresso mudam o total
- [ ] Cupom `DOMINGO10` aplica 10% e aparece no resumo
- [ ] Checkout valida campos obrigatórios e CPF
- [ ] Checkout redireciona para a URL de pagamento
- [ ] Após aprovar, o pedido fica `PAID` e depois `IN_PRODUCTION`
- [ ] Timeline do pedido mostra o histórico
- [ ] Cadastro e login funcionam; carrinho anônimo é mesclado no login
- [ ] Endereço salvo pré-preenche o checkout
- [ ] Rota inexistente mostra o 404 e libera o troféu
- [ ] Konami code (↑↑↓↓←→←→BA) troca o tema e entrega o cupom `CAOS30`
- [ ] Digitar `desculpa` entrega `DESCULPA15`
- [ ] 7 cliques no logo ligam o modo domingo
- [ ] Quantidade 42 em um item libera frete grátis
- [ ] 5s de hover no rodapé libera a confissão
- [ ] Console do navegador mostra a arte ASCII e a vaga
- [ ] `/trofeus` reflete o progresso e mostra o rank
- [ ] Com 4 troféus, o produto secreto aparece no catálogo

## Problemas comuns

**Porta em uso.** Ajuste `BACKEND_PORT`, `FRONTEND_PORT` ou `POSTGRES_PORT` no `.env`.

**Frontend não fala com a API.** `VITE_API_URL` precisa apontar para `localhost`,
não para o nome do serviço: o browser roda no host, fora da rede do Compose.

**Hot reload não dispara no Windows.** Já está com `usePolling: true` no Vite. Se
ainda assim não funcionar, reinicie o container do frontend.

**Migration não aplicou.** `docker compose exec backend npx prisma migrate deploy`.
Para começar do zero: `docker compose down -v && docker compose up --build`.

**Webhook do Mercado Pago não chega.** O MP não alcança `localhost`. Use ngrok e
preencha `MP_NOTIFICATION_URL`, ou valide o fluxo com `PAYMENT_DRIVER=mock`.
