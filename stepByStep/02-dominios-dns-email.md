# Passo a passo: domínios, DNS (Cloudflare) e e-mail (Resend)

Vale para **roupadedomingo.com.br** e **timedobairro.com.br**. O objetivo é deixar os dois funcionando como o
**hispora.com.br**: domínio registrado no registro.br, DNS no Cloudflare, site no Railway e e-mail
transacional saindo pelo Resend.

Este mesmo arquivo existe em `refs/RD/docs/stepByStep/` e em `refs/time-do-bairro/docs/`.

---

## Resumo: o que já está pronto e o que falta

| Etapa                                                     | roupadedomingo.com.br             | timedobairro.com.br                           |
| --------------------------------------------------------- | --------------------------------- | --------------------------------------------- |
| Zona criada no Cloudflare (plano Free)                    | ✅                                | ✅                                            |
| Configurações da zona iguais às do Hispora (SSL Full etc.) | ✅                                | ✅                                            |
| DMARC ajustado para `p=none` (igual ao Hispora)           | ✅                                | ✅                                            |
| Domínio cadastrado no Resend (região São Paulo)           | ✅                                | ✅ (pocketmed removido para liberar a vaga)    |
| Registros do Resend (DKIM, `send`, `rsend`) no Cloudflare | ✅                                | ✅                                            |
| Nameservers trocados no registro.br                       | ❌ **você** (passo 1)              | ❌ **você** (passo 1)                          |
| Remover o MX nulo `.`                                      | ❌ **você** (passo 3)              | ❌ **você** (passo 3)                          |
| Domínio personalizado no Railway + CNAMEs da raiz e `www` | ❌ passo 4                         | ❌ passo 4                                     |
| Variáveis de e-mail e URL no backend                      | ❌ passo 5                         | ❌ passo 5                                     |
| Receber e-mail (ex.: `sac@`), opcional                    | ❌ passo 6 (recomendado no RD)     | opcional                                      |

### Como o Hispora está montado (referência)

**Cloudflare: zona `hispora.com.br`**

| Tipo  | Nome                | Conteúdo                             | Proxy    |
| ----- | ------------------- | ------------------------------------ | -------- |
| CNAME | `@` (raiz)          | `<serviço>.up.railway.app` (web)     | Proxied  |
| CNAME | `www`               | `<serviço>.up.railway.app`           | Proxied  |
| TXT   | `_railway-verify`   | `railway-verify=…` (gerado pelo Railway) | DNS only |
| TXT   | `resend._domainkey` | chave DKIM gerada pelo Resend        | DNS only |

**Configurações da zona:** SSL/TLS **Full**, TLS 1.3 ligado, HTTP/3 ligado, Brotli ligado, IPv6 ligado e
"Always Use HTTPS" desligado. As duas zonas novas já estão assim.

**Resend:** domínio na região **São Paulo (sa-east-1)**, com return-path `send` e os registros DKIM,
`send`/`rsend` (SPF) e DMARC `p=none`.

---

## Passo 1: trocar os nameservers no registro.br (os dois domínios)

Sem este passo nada funciona: o Cloudflare só passa a responder pelo domínio depois dele.

1. Entre em [registro.br/painel](https://registro.br/painel/) com a sua conta.
2. Abra **roupadedomingo.com.br** → seção **DNS** → **Alterar servidores DNS**.
3. Apague os servidores atuais (`a.auto.dns.br`, `b.auto.dns.br`) e coloque:
   - `ian.ns.cloudflare.com`
   - `izabella.ns.cloudflare.com`
4. Salve.
5. Repita os passos 2 a 4 para **timedobairro.com.br**, com os mesmos dois servidores.
6. Espere. A propagação costuma levar de alguns minutos a algumas horas (no registro.br pode chegar a 24 h).
   - O Cloudflare manda um e-mail quando a zona fica **Active**.
   - Para conferir: Cloudflare → Domains, o status muda de *Pending* para *Active*.

> Se o registro.br avisar que o DNSSEC está ativo, desative antes de trocar. O Hispora está com DNSSEC
> desligado no Cloudflare.

---

## Passo 2: verificar os domínios no Resend (os dois)

✅ Já feito: os dois domínios estão cadastrados no Resend (São Paulo, return-path `send`, tracking desligado), e
os registros DKIM (`resend._domainkey`), `send` e `rsend` estão no Cloudflare como **DNS only**. O
`pocketmed.com.br` foi removido do Resend para liberar a 3ª vaga do plano gratuito.

Falta só verificar, **depois** que o passo 1 propagar (zona *Active* no Cloudflare):

1. Resend → **Domains** → abra o domínio.
2. Clique em **Restart** / **Verify DNS records**. "Not Started" é normal até você clicar.
3. Quando o status ficar **Verified**, o envio está liberado. Repita para o outro domínio.

> Se algum registro falhar, confira no Cloudflare se ele está como **DNS only** (nuvem cinza). Com proxy
> ligado, CNAME de e-mail não funciona.

---

## Passo 3: apagar o MX nulo nos dois domínios

O registro.br cria por padrão os registros de "domínio que não usa e-mail", e o Cloudflare importou
esses registros:

| Tipo | Nome   | Conteúdo           | O que fazer                                                    |
| ---- | ------ | ------------------ | -------------------------------------------------------------- |
| MX   | `@`    | `.` (MX nulo)      | **Apagar.** Diz ao mundo que o domínio não recebe e-mail; alguns provedores recusam mensagens de domínios assim |
| TXT  | `@`    | `v=spf1 -all`      | Pode manter. O Resend usa o SPF do subdomínio `send`, não o da raiz |
| TXT  | `_dmarc` | `v=DMARC1; p=none;` | Já ajustado. Manter                                          |

Como apagar: Cloudflare → zona → **DNS** → **Records** → linha **MX** com conteúdo `.` → **Edit** →
**Delete** → confirmar. Faça nos dois domínios.

> Eu tentei apagar e a ação foi bloqueada pela permissão do modo automático. Por isso fica com você.

---

## Passo 4: site no domínio (Railway + Cloudflare)

Igual ao Hispora: a raiz e o `www` apontam por CNAME para o serviço web no Railway.

### roupadedomingo.com.br

O serviço que recebe o tráfego é o **`frontend-roupa-de-domingo`**: o nginx serve o site e repassa `/api`
ao backend.

1. Railway → projeto do RD → serviço **frontend-roupa-de-domingo** → **Settings** → **Networking** →
   **Custom Domain** → digite `roupadedomingo.com.br` → porta = a mesma do domínio `*.up.railway.app`
   que já existe.
2. O Railway mostra dois valores:
   - um **CNAME** (algo como `xxxx.up.railway.app`)
   - um **TXT** `_railway-verify` com `railway-verify=…`
3. No Cloudflare (zona `roupadedomingo.com.br` → DNS → Add record):

   | Tipo  | Nome              | Conteúdo                         | Proxy                      |
   | ----- | ----------------- | -------------------------------- | -------------------------- |
   | CNAME | `@`               | o CNAME que o Railway mostrou    | **Proxied** (nuvem laranja) |
   | TXT   | `_railway-verify` | o valor `railway-verify=…`       | DNS only                   |

4. Repita os passos 1 a 3 para `www.roupadedomingo.com.br`:
   - Custom Domain `www.roupadedomingo.com.br` no mesmo serviço;
   - no Cloudflare, CNAME `www` com o valor que o Railway der, **Proxied**.
5. Espere o Railway marcar os dois domínios como verificados, com certificado emitido.
6. Teste `https://roupadedomingo.com.br` e `https://www.roupadedomingo.com.br`.

### timedobairro.com.br

O mesmo procedimento, no serviço web do Time do Bairro no Railway (o que serve o app web; hoje o
`APP_URL` local é `http://localhost:8081`).

- Se o Time do Bairro ainda não está no Railway, faça o deploy primeiro e depois siga os passos acima.
- Se o backend tiver domínio próprio (por exemplo `api.timedobairro.com.br`), adicione-o como Custom Domain
  no serviço do backend. Crie também o CNAME `api` no Cloudflare, Proxied.

> Se quiser, me peça para cadastrar os CNAMEs no Cloudflare quando o Railway gerar os valores.

---

## Passo 5: variáveis de ambiente nos backends (Railway → serviço → Variables)

### Chave do Resend

1. Resend → **API keys** → **Create API key**.
2. Preencha:
   - **Permission:** *Sending access*
   - **Domain:** o domínio específico (uma chave por projeto)
3. Copie a chave (`re_…`). Ela só aparece uma vez. Não cole em chat nem commite; vai só no Railway.

Os dois backends enviam por **SMTP** (nodemailer), e o Resend aceita SMTP:

| Campo   | Valor                                                   |
| ------- | ------------------------------------------------------- |
| Host    | `smtp.resend.com`                                       |
| Porta   | `465` (TLS direto) ou `587` (STARTTLS)                  |
| Usuário | `resend` (literalmente essa palavra)                    |
| Senha   | a API key `re_…`                                        |

### roupadedomingo: serviço `backend-roupa-de-domingo`

```env
MAIL_DRIVER=smtp
MAIL_FROM="Roupa de Domingo <nao-responda@roupadedomingo.com.br>"
MAIL_SAC_INBOX=sac@roupadedomingo.com.br
SMTP_HOST=smtp.resend.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=resend
SMTP_PASS=<API key re_... do Resend>
FRONTEND_URL=https://roupadedomingo.com.br
```

Depois que o domínio estiver no ar, atualize também:

- **Mercado Pago:** troque a URL do webhook no painel (Suas integrações → Webhooks) para
  `https://roupadedomingo.com.br/api/payments/webhook`. Se `MP_NOTIFICATION_URL` estiver definida, atualize
  com o mesmo valor.
- **Printful:** webhook em `https://roupadedomingo.com.br/api/fulfillment/webhook/printful?secret=<PRINT_WEBHOOK_SECRET>`.
- O domínio `*.up.railway.app` continua funcionando. Pode manter como reserva.

### timedobairro: serviço do backend

```env
MAIL_FROM="Time do Bairro <nao-responda@timedobairro.com.br>"
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=<API key re_... do Resend>
APP_URL=https://timedobairro.com.br
CORS_ORIGIN=https://timedobairro.com.br,https://www.timedobairro.com.br
```

Notas:

- O `MAIL_FROM` padrão no código ainda é `@timedobairro.app`. Defina a variável no Railway para usar o
  domínio `.com.br` verificado no Resend: e-mail com remetente de domínio não verificado é recusado.
- Aqui a variável da senha se chama `SMTP_PASSWORD`, e não `SMTP_PASS` como no RD.
- O mail service do Time do Bairro não tem opção `secure`, então use a porta **587** (STARTTLS).
- `CORS_ORIGIN` só é necessário se o front chamar o backend em outro domínio (ex.: `api.`).

Depois de salvar as variáveis, faça **Deploy** no Railway e teste um fluxo que envie e-mail (cadastro,
"esqueci a senha"). Resend → **Logs** mostra se saiu e se foi entregue.

---

## Passo 6 (opcional, recomendado no RD): receber e-mail no domínio

O Resend só **envia**. O Hispora não recebe e-mail no domínio. A Roupa de Domingo, porém, mostra
`sac@roupadedomingo.com.br` para o cliente (SAC, exigência do CDC), então esse endereço precisa receber
mensagens.

Caminho gratuito: **Cloudflare Email Routing** (repassa para o seu Gmail).

1. Faça o passo 3 antes (apagar o MX nulo).
2. Cloudflare → zona `roupadedomingo.com.br` → **Email** → **Email Routing** → **Get started**.
3. Crie a regra `sac@roupadedomingo.com.br` → encaminhar para o seu e-mail pessoal, e confirme o e-mail de
   verificação que chegar.
4. O Cloudflare oferece adicionar os registros MX e SPF dele. Aceite.
   - Os MX vão na raiz e não conflitam com o Resend, que usa `send.`.
   - O Cloudflare vai propor trocar o `v=spf1 -all` da raiz pelo SPF dele. Pode aceitar.
5. Envie um e-mail de teste para `sac@roupadedomingo.com.br`.

Para o Time do Bairro, faça o mesmo se algum endereço do domínio aparecer para os usuários.

---

## Checklist final

- [ ] Passo 1: nameservers do Cloudflare no registro.br (roupadedomingo)
- [ ] Passo 1: nameservers do Cloudflare no registro.br (timedobairro)
- [ ] Zonas **Active** no Cloudflare
- [x] Passo 2: os dois domínios cadastrados no Resend com os registros no Cloudflare
- [ ] Resend mostrando **Verified** nos dois domínios (clicar em verificar depois da propagação)
- [ ] Passo 3: MX `.` apagado nos dois domínios
- [ ] Passo 4: Custom Domain (raiz e `www`) no Railway + CNAMEs Proxied + TXT `_railway-verify` (roupadedomingo)
- [ ] Passo 4: o mesmo para o timedobairro
- [ ] Passo 5: API keys do Resend criadas e variáveis de e-mail e URL nos dois backends
- [ ] Passo 5: webhooks do Mercado Pago e da Printful apontando para `roupadedomingo.com.br`
- [ ] Passo 6: `sac@roupadedomingo.com.br` recebendo (Email Routing)
- [ ] Teste: cadastro / recuperação de senha chegando na caixa de entrada (não no spam) nos dois projetos
