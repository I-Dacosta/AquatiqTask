# n8n-workflows for PrioritiAI

Alle flyter er dokumentert for n8n 1.x og forventer at `docker-compose.yml` kjører tjenestene `postgres`, `ai` og `frontend`. Miljøvariabler (`OPENAI_API_KEY`, `TEAMS_WEBHOOK_URL`) må være satt for at HTTP-kall skal fungere.

## Import av workflows

Tre ferdige workflow-filer er tilgjengelige for direkte import:

1. **PrioritiAI - Outlook til Oppgave.json** - Henter e-poster fra Outlook og oppretter oppgaver
2. **PrioritiAI - Manuell oppgave (Webhook).json** - Webhook for manuell opprettelse av oppgaver
3. **PrioritiAI - Oppdater status (Webhook).json** - Webhook for statusoppdateringer

### Importere workflows til n8n:

1. Åpne n8n i nettleseren: `http://localhost:5678`
2. Naviger til **Workflows** i venstre meny
3. Klikk på **Import from File** eller **Add workflow → Import from File**
4. Velg en av JSON-filene fra `n8n/`-mappen
5. Klikk **Import**
6. Gjenta for de andre workflow-filene

### Etter import:

- **Konfigurer credentials:** 
  - Microsoft 365 OAuth for Outlook-triggeren (krever Entra ID-app)
  - PostgreSQL-tilkobling til PrioAI-databasen
- **Aktiver workflows:** Klikk på toggle-bryteren øverst til høyre for å aktivere hver workflow
- **Test workflows:** Bruk "Test Workflow" eller "Execute Workflow" for å verifisere at alt fungerer

### Webhook-URLer:

Etter import vil webhook-workflows få automatisk genererte URLer:
- **Manuell oppgave:** `http://localhost:5678/webhook/prioai/tasks` (POST)
- **Oppdater status:** `http://localhost:5678/webhook/prioai/tasks/:id` (PATCH)

Disse URLene kan brukes fra frontend eller eksterne systemer for å opprette/oppdatere oppgaver.

## 1. Outlook → Oppgave

1. **Microsoft Outlook Trigger**
   - *Resource:* Message
   - *Operation:* On New
   - *Polling interval:* 60s (kan endres)
   - *Folder ID:* Inbox (eller annen mappe-ID)
   - *Credentials:* Microsoft 365 OAuth via Entra ID med `Mail.Read`.

2. **IF (Filter)**
   - Eksempelregel: `{{$json["subject"].toLowerCase().includes('#oppgave')}}`
   - Alternativ: Send alle videre og la AI velge.

3. **HTTP Request → AI**
   - *Method:* POST
   - *URL:* `http://ai:8080/classify`
   - *Body:* JSON, `Send Body` = `Yes`
   - *Body Parameters:*
     ```json
     {
       "subject": "={{$json["subject"]}}",
       "body": "={{$json["bodyPreview"] || $json["body"]["content"]}}",
       "sender": "={{$json["from"]["emailAddress"]["name"] || $json["from"]["emailAddress"]["address"]}}",
       "due_text": "={{$json["body"]["content"].match(/(i dag kl [0-9:]+)/i)?.[0]}}"
     }
     ```

4. **Postgres → Insert**
   - *Resource:* Database
   - *Operation:* Insert
   - *Table:* `prioai_task`
   - *Columns:*
     - `title` = `={{$json["title"]}}`
     - `description` = `={{$json["description"]}}`
     - `source` = `outlook`
     - `source_ref` = `={{$json["id"]}}`
     - `requester` = `={{$json["from"]["emailAddress"]["address"]}}`
     - `role_hint` = `={{$json["role_hint"]}}`
     - `due_at` = `={{$json["due_at"]}}`
     - `est_minutes` = `={{$json["est_minutes"]}}`
     - `value_score`, `risk_score`, `role_score`, `haste_score`, `ai_score`, `ai_reason`
     - `status` = `incoming`

5. **HTTP Request → Teams webhook**
   - *Method:* POST
   - *URL:* `={{$env.TEAMS_WEBHOOK_URL}}`
   - *Headers:* `Content-Type: application/json`
   - *Body:* Adaptive Card (se JSON under).

6. **Respond / Set** (valgfri)
   - Skriv `task_id` eller status til logg.

### Adaptive Card-eksempel

```json
{
  "type": "message",
  "attachments": [
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": [
          { "type": "TextBlock", "size": "Large", "weight": "Bolder", "text": "Ny oppgave i PrioritiAI" },
          { "type": "TextBlock", "text": "={{$json["title"]}}", "wrap": true },
          { "type": "FactSet", "facts": [
            { "title": "Score:", "value": "={{$json["ai_score"]}}" },
            { "title": "Frist:", "value": "={{$json["due_at"] || '-'}}" },
            { "title": "Kilde:", "value": "Outlook" }
          ]},
          { "type": "TextBlock", "text": "={{$json["ai_reason"]}}", "wrap": true, "isSubtle": true }
        ],
        "actions": [
          { "type": "Action.OpenUrl", "title": "Åpne i dashboard", "url": "https://prioai.local/task/={{$json["id"]}}" }
        ]
      }
    }
  ]
}
```

## 2. Teams → Oppgave (valgfri)

1. **Microsoft Teams Trigger**
   - *Resource:* Message
   - *Operation:* On Updated (polling)
   - *Team/Channel:* Dedikert kanal «Innkommet forespørsel»

2. **HTTP Request → AI** (som over)
   - Body bruker `={{$json["text"]}}` og `sender = {{$json["from"]["user"]["displayName"]}}`.

3. **Postgres → Insert**
   - Felt `source` = `teams`
   - `source_ref` = `={{$json["id"]}}`

4. **HTTP Request → Teams webhook**
   - Juster `Kilde`-feltet til `Teams`.

## 3. Manuell opprettelse

1. **Webhook**
   - *Path:* `/webhook/prioai/tasks`
   - *HTTP Method:* POST
   - *Response:* 202 Accepted

2. **Function**
   - Valider inngang (`title`, `description`, `est_minutes` osv.) og sett `source = 'manual'`.

3. **Postgres → Insert**
   - Som i Outlook-flyten.

4. **HTTP Request → Teams webhook**
   - Gi klar tekst: «Manuell oppgave registrert».

## 4. Statusendring

1. **Webhook**
   - *Path:* `/webhook/prioai/tasks/:id`
   - *HTTP Method:* PATCH

2. **Function**
   - Parse `status`, `override_priority`, `override_locked`.

3. **Postgres → Update**
   - `UPDATE prioai_task SET ... WHERE id = {{$json["params"]["id"]}}`

4. **HTTP Request → Teams webhook**
   - Kort melding: «Oppgave oppdatert til {{$json["status"]}}».

## Tilganger og OAuth

- Opprett en Entra ID-appregistrering med delegert tilgang: `Mail.Read`, `User.Read`, `offline_access`.
- N8N trenger redirect URL `https://<n8n-host>/rest/oauth2-credential/callback`.
- For Teams webhook: Opprett «Incoming Webhook» i valgt kanal og lagre URL i `.env`.

## Feilhåndtering

- Legg til `Error Workflow` i n8n for logging til Teams eller e-post.
- Aktiver `Retry On Fail` på HTTP Request-noder med eksponentiell backoff.
- Vurder `Set`-node etter AI-respons for default-verdier ved tomme felt.
