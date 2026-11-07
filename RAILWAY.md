# Deploy no Railway

Projeto Railway: **overflowing-perception**, ambiente `production`
(https://railway.com/project/9419ca47-9a9b-4ae3-bc47-fd2a6041b275).

| Serviço                     | Origem                                        | Estado em 03/11/2026                  |
| --------------------------- | --------------------------------------------- | ------------------------------------- |
| `Postgres`                  | Template PostgreSQL do Railway, com volume `postgres-volume` | Online, sem acesso público  |
| `backend-roupa-de-domingo`  | GitHub `fernandoluckesi/backend-roupa-de-domingo`, branch `main` | **Active** (commit `4d02898`): migrations aplicadas, catálogo carregado (15 produtos, 123 variantes), sem domínio público |
| `frontend-roupa-de-domingo` | GitHub `fernandoluckesi/frontend-roupa-de-domingo`, branch `main` | **Active** (commit `8777dfe`): nginx serve o build e repassa `/api` ao backend pela rede privada. Sem domínio público ainda |

---

## 1. Como o backend usa o banco

- `DATABASE_URL=${{Postgres.DATABASE_URL}}` é uma **referência** à variável do serviço Postgres. O Railway
  troca pelo valor real na rede interna (`postgres.railway.internal`), então a senha não fica copiada
  no backend. Se a senha do Postgres for trocada, o backend recebe a nova sozinho.
- O banco **não tem TCP proxy público**. Só os serviços do projeto o alcançam. Para abrir uma conexão de
  fora (DBeaver, psql), ative em Postgres → Settings → Networking → *TCP Proxy*. Isso cria
  `DATABASE_PUBLIC_URL`. Desligue quando terminar.
- No start do container (`Dockerfile.railway`):
  1. `prisma migrate deploy` aplica as migrations;
  2. `SEED_IF_EMPTY=true npm run seed` carrega categorias, produtos, cupons e easter eggs **só se o banco
     estiver vazio**. Se já existir produto, pedido ou usuário, nada é feito. Se o seed falhar, a API
     sobe mesmo assim e o log mostra `AVISO: seed falhou`;
  3. `node dist/src/main` sobe a API.
- Fora desse modo, o seed se recusa a rodar em produção (`NODE_ENV=production`), porque ele apaga todas
  as tabelas. Para forçar um reset, é preciso `SEED_ALLOW_RESET=true`.
- Em produção o seed **não cria** os usuários demo (`domingo123`). Veja a seção 3.3 para criar o admin.

## 2. Variáveis já configuradas no backend

| Variável                        | Valor                                    | Observação |
| ------------------------------- | ---------------------------------------- | ---------- |
| `DATABASE_URL`                  | `${{Postgres.DATABASE_URL}}`             | Referência ao Postgres |
| `NODE_ENV`                      | `production`                             | |
| `API_PREFIX`                    | `api`                                    | |
| `JWT_SECRET`                    | `${{secret(64)}}`                        | Gerado pelo Railway (64 caracteres). Ninguém precisa saber o valor |
| `JWT_EXPIRES_IN`                | `7d`                                     | |
| `PAYMENT_DRIVER`                | `mock`                                   | Trocar quando o Mercado Pago entrar (3.2) |
| `MP_USE_SANDBOX`                | `true`                                   | |
| `PRINT_PROVIDER`                | `printful`                               | Sem `PRINT_API_KEY`, o backend usa o mock automaticamente |
| `PRINT_API_URL`                 | `https://api.printful.com`               | |
| `PRINT_WEBHOOK_SECRET`          | `${{secret(48)}}`                        | Gerado pelo Railway. Vai na URL do webhook da Printful |
| `PRINTFUL_STORE_ID`             | `19007611`                               | Loja "Roupa de Domingo" |
| `PRINTFUL_CONFIRM_ORDERS`       | `false`                                  | Rascunho na Printful, sem cobrança |
| `FREE_SHIPPING_THRESHOLD_CENTS` | `24900`                                  | |

`PORT` não precisa ser definida: o Railway injeta, e o backend já a lê.

## 3. O que você precisa preencher

Estas variáveis são credenciais ou dependem de algo que ainda não existe, então não foram configuradas.
Para cadastrá-las: serviço → **Variables** → **New Variable**, depois **Deploy** na barra de mudanças.

### 3.1 Printful

| Variável        | Onde obter |
| --------------- | ---------- |
| `PRINT_API_KEY` | O token privado que você criou em https://developers.printful.com/tokens (o mesmo do `.env` local). Para produção, o ideal é criar um token separado. |

Depois do deploy, cadastre o webhook (seção 5 de [PRINTFUL-API.md](PRINTFUL-API.md)) com a URL
`https://<domínio do frontend>/api/fulfillment/webhook/printful?secret=<valor de PRINT_WEBHOOK_SECRET>`.
Para ver o valor: Variables → `PRINT_WEBHOOK_SECRET` → ícone de olho.

Enquanto o pagamento for `mock`, o backend **ignora** `PRINTFUL_CONFIRM_ORDERS=true` e mantém os pedidos
em rascunho. Sem essa trava, qualquer pessoa poderia "aprovar" um pagamento simulado e gerar cobrança
na Printful.

### 3.2 Mercado Pago

| Variável              | Valor |
| --------------------- | ----- |
| `PAYMENT_DRIVER`      | `mercadopago` |
| `MP_ACCESS_TOKEN`     | Access Token da aplicação em https://www.mercadopago.com.br/developers/panel/app (use o de teste primeiro) |
| `MP_PUBLIC_KEY`       | Public Key da mesma aplicação |
| `MP_USE_SANDBOX`      | `true` com credenciais de teste; `false` com as de produção |
| `MP_NOTIFICATION_URL` | `https://frontend-roupa-de-domingo-production.up.railway.app/api/payments/webhook` (opcional: o webhook já está cadastrado no painel) |
| `MP_WEBHOOK_SECRET`   | **Assinatura secreta** do painel → Configuração de webhooks (botão de olho). Valida o header `x-signature` |

Detalhes em [MERCADO-PAGO.md](MERCADO-PAGO.md). Enquanto `MP_ACCESS_TOKEN` estiver vazio, o checkout fica
simulado: qualquer um aprova o próprio pedido. **Não abra a loja ao público nesse estado.**

### 3.3 Usuário admin

Escolha uma das opções:

- **Antes do primeiro deploy:** defina `SEED_ADMIN_EMAIL` e `SEED_ADMIN_PASSWORD` no backend. A carga
  inicial cria o admin. Depois apague as duas variáveis.
- **Depois:** cadastre-se pelo front e promova a conta em Postgres → **Database** → **Data**
  (console SQL):

  ```sql
  UPDATE users SET role = 'ADMIN' WHERE email = 'seu-email@dominio.com';
  ```

### 3.4 Domínio público

Arquitetura: **só o frontend é público**. O nginx do front atende `/api/*` e repassa a requisição para
`http://backend-roupa-de-domingo.railway.internal:8080` pela rede privada do Railway. O bundle usa
`VITE_API_URL=/api` (mesma origem), então **não há CORS** e o backend fica fechado.

1. ✅ Frontend: `https://frontend-roupa-de-domingo-production.up.railway.app` (proxy `/api` testado em 04/11/2026). Era Settings → Networking → **Generate Domain**. A porta é a que o Railway injeta em `PORT`,
   e o nginx já escuta nela.
2. Backend → Variables: `FRONTEND_URL=https://<domínio do frontend>`. Esse valor é usado nas URLs de
   retorno do Mercado Pago e no link do e-mail/pedido.
3. Se a porta do backend mudar (hoje `PORT=8080`, injetada pelo Railway), defina no frontend
   `BACKEND_INTERNAL_URL=http://backend-roupa-de-domingo.railway.internal:<porta>`.

Os webhooks (Mercado Pago e Printful) também passam pelo domínio do front, porque `/api` é repassado:

- Mercado Pago: cadastrado no painel (ambiente Teste) com `https://frontend-roupa-de-domingo-production.up.railway.app/api/payments/webhook`
- Printful: `https://<domínio do frontend>/api/fulfillment/webhook/printful?secret=<PRINT_WEBHOOK_SECRET>`

Se preferir expor o backend direto, gere um domínio para ele, defina `CORS_ORIGIN` com o domínio do front
e faça o build do front com `VITE_API_URL=https://<domínio do backend>/api`.

## 4. Build

O `Dockerfile` principal usa `RUN --mount=type=bind` para injetar a CA do proxy corporativo no
`npm install` local. O Railway **rejeita** esse tipo de mount, e foi por isso que o primeiro deploy falhou com
`dockerfile invalid: flag '--mount=type=bind...' is missing a type=cache argument`.

A solução está no repositório do backend:

- `Dockerfile.railway` faz o build de produção sem mounts;
- `railway.json` aponta o build para ele e define o healthcheck em `/health`.

Também foram corrigidos:

- o caminho de start: o build gera `dist/src/main.js`, mas a imagem chamava `node dist/main`, que não existe;
- o `tsconfig.json`, que não era copiado para a imagem final. Sem ele, o ts-node do seed quebrava com `TS5109`.

### Frontend

O `Dockerfile` do frontend tinha o mesmo `RUN --mount=type=bind,from=certs`. A correção segue o mesmo modelo do backend:

- `Dockerfile.railway`: build Vite + nginx, sem mounts;
- `nginx.railway.conf.template`: `listen ${PORT}` e o proxy de `/api`. O `resolver` vem do
  `NGINX_ENTRYPOINT_LOCAL_RESOLVERS` da imagem oficial, para reavaliar o IP interno do backend a cada deploy;
- `railway.json`: aponta o build para o Dockerfile acima e define o healthcheck em `/`.

O backend passou a escutar em `::` (IPv6 + IPv4), porque a rede privada do Railway usa IPv6.

> **Cuidado:** no seu clone local, o `origin` do frontend aponta para
> `github.com/fernandoluckesi/backend-roupa-de-domingo.git`, e o do backend para `front-end-roupa-de-domingo.git`,
> que hoje redireciona para o repositório do backend. Um `git push` a partir do frontend iria para o repositório
> do **backend**, que é de onde o Railway faz o deploy. Corrija com
> `git remote set-url origin https://github.com/fernandoluckesi/frontend-roupa-de-domingo.git`.

## 5. Checklist

- [x] Postgres criado com volume
- [x] Variáveis do backend (seção 2)
- [x] `Dockerfile.railway` + `railway.json` + seed seguro para produção
- [x] Push do backend para `main` (`314f305`, `b6c5ae8`); deploy ativo
- [x] Frontend: `Dockerfile.railway` sem mounts + proxy `/api` (seção 4); deploy ativo
- [x] Domínio público do frontend
- [ ] `FRONTEND_URL=https://frontend-roupa-de-domingo-production.up.railway.app` no backend (3.4)
- [ ] `PRINT_API_KEY` (3.1)
- [ ] Admin (3.3)
- [x] Webhook do Mercado Pago cadastrado no painel (Teste)
- [ ] Mercado Pago (3.2): credenciais + `MP_WEBHOOK_SECRET`, antes de abrir ao público
- [ ] Webhook da Printful apontando para o domínio do frontend (`/api` é repassado)
