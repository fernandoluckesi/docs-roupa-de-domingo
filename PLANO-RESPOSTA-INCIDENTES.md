# Plano de resposta a incidentes de segurança

Base: LGPD, art. 48, e Resolução CD/ANPD nº 15/2024 (Regulamento de Comunicação de
Incidente de Segurança). Um incidente é qualquer evento que comprometa a
confidencialidade, a integridade ou a disponibilidade de dados pessoais. Exemplos:
vazamento de banco, credencial exposta, acesso indevido ao painel, ransomware,
e-mail enviado ao destinatário errado.

## Papéis

| Papel | Quem | Responsabilidade |
| --- | --- | --- |
| Líder do incidente | responsável técnico | coordena, decide contenção, registra a linha do tempo |
| Encarregado (DPO) | privacidade@roupadedomingo.com.br | avalia risco aos titulares, comunica ANPD e titulares |
| Jurídico | advogado da empresa | valida comunicações e obrigações contratuais |

## Prazos

- **ANPD e titulares:** em até **3 dias úteis** após saber que o incidente pode gerar risco ou dano relevante (Res. 15/2024, art. 6º), pelo formulário da ANPD.
- **Complemento:** informação que ainda falte pode ser enviada em até 20 dias úteis, com justificativa.
- **Registro:** todo incidente, mesmo sem comunicação, fica registrado por no mínimo 5 anos (art. 10).

## Passo a passo

1. **Detectar e registrar.** Abra um registro com data e hora, quem detectou, o que foi visto e os sistemas afetados.
2. **Conter (primeira hora).**
   - Credencial vazada: troque na hora.

     | Credencial | Onde trocar | Efeito |
     | --- | --- | --- |
     | `JWT_SECRET` | Railway | derruba todas as sessões |
     | `DATA_ENCRYPTION_KEY` | Railway | depois rode `npm run data:encrypt -- --rotate` |
     | `MP_ACCESS_TOKEN` | painel do Mercado Pago | — |
     | `PRINT_API_KEY` | painel da Printful | — |
     | SMTP | provedor de e-mail | — |

   - Conta comprometida: rode `UPDATE users SET "tokenVersion" = "tokenVersion" + 1 WHERE id = ...`. Isso revoga as sessões dela.
   - Acesso indevido ao admin: desative o 2FA e redefina a senha do admin. Revise `audit_logs`.
   - Exploração ativa: tire o serviço do ar no Railway (Settings → Pause) até corrigir.
3. **Avaliar o risco.**
   - Quais dados: CPF está cifrado, então veja se a chave também vazou. Inclua dados de pagamento, que não guardamos.
   - Quantos titulares foram afetados e se há menores.
   - Qual o risco de fraude ou dano.
   - Risco relevante obriga a comunicar.
4. **Comunicar**, se for o caso.

   | Destino | Conteúdo |
   | --- | --- |
   | ANPD | dados afetados, titulares, medidas tomadas, riscos, contato do encarregado |
   | Titulares | e-mail claro sobre o que houve, quais dados, o que fizemos e o que eles devem fazer (ex.: trocar a senha) |
   | Mercado Pago e Printful | se envolver dados deles |

5. **Erradicar e recuperar.**
   - Corrija a causa.
   - Restaure de backup se houve perda ou alteração (`scripts/backup/restore-test.sh` valida o arquivo antes).
6. **Pós-incidente** (até 15 dias): faça uma revisão sem culpados, com causa raiz, o que funcionou e as ações preventivas. Atualize este plano e o [ROPA](./LGPD-ROPA.md).

## Fontes para investigar

| Fonte | Onde |
| --- | --- |
| `audit_logs` | trilha completa ([AUDITORIA.md](./AUDITORIA.md)): logins e falhas, bloqueios, trocas de senha e e-mail, ações de admin, pedidos e pagamentos. Filtre por `actorId`, `action=auth.login.failed` ou `requestId` em `GET /api/admin/audit-logs` |
| Logs do Railway | requisições e erros, guardados 6 meses (Marco Civil, art. 15) |
| `consent_records`, `auth_tokens`, `users.lockedUntil` | sinais de ataque a contas |
| Painel do Mercado Pago e da Printful | movimentações fora do padrão |
