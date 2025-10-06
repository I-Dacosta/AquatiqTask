# PrioritiAI

PrioritiAI er et MVP-oppsett for å samle inn forespørsler fra Outlook og Teams, prioritere dem med en AI-mikrotjeneste og presentere dem i et Next.js-dashboard. Repositoriet inneholder Docker-stack, databaseoppsett, n8n-workflows, AI-kode og frontend.

## Arkitektur

```
Microsoft 365 (Outlook/Teams) ─┐
                               ├─▶ n8n (workflow-automatisering)
                               │      ├─ Henter meldinger
                               │      ├─ Kaller AI (FastAPI)
                               │      ├─ Skriver til PostgreSQL
                               │      └─ Sender Teams-varsler
                               ▼
                         PostgreSQL (prioai_task)
                               ▼
                        Next.js frontend (faner: Innkommende, Godkjente, Pågående)
```

## Innhold

| Mappe / fil                | Beskrivelse |
|----------------------------|-------------|
| `docker-compose.yml`       | Starter Postgres, n8n, AI-tjeneste og frontend |
| `infra/db/init.sql`        | Databaseskjemaet (`prioai_task`) |
| `ai/`                      | FastAPI-tjeneste med heuristikker + valgfri OpenAI-støtte |
| `frontend/`                | Next.js-app med faner og API-endepunkt mot Postgres |
| `n8n/workflows.md`         | Beskrivelse av n8n-workflows og Teams Adaptive Card |
| `.env.example`             | Miljøvariabler som må fylles ut |

## Kom i gang

1. **Klon repo og kopier miljøvariabler**
   ```bash
   cp .env.example .env
   ```
   Fyll inn `OPENAI_API_KEY` (valgfritt for LLM-forklaring) og `TEAMS_WEBHOOK_URL` (Incoming Webhook i ønsket kanal).

2. **Start stacken**
   ```bash
   docker compose up --build
   ```
   - n8n: http://localhost:5678 (første gang vil du bli bedt om å lage brukerkonto)
   - Frontend: http://localhost:3000
   - AI-tjeneste: http://localhost:8080/docs (Swagger)
   - Postgres: `postgres://prioai:superSikker!@localhost:5432/prioai_db`

3. **Importer eller bygg n8n-workflows**
   Følg oppskriften i [`n8n/workflows.md`](n8n/workflows.md) for å sette opp:
   - Outlook → Oppgave
   - Teams → Oppgave (valgfri)
   - Webhook for manuell opprettelse
   - Webhook for statusoppdatering

4. **Frontend-utvikling (valgfritt)**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Next.js-appen vil koble til Postgres via `DATABASE_URL`. Bruk `npm run lint` og `npm run build` for kvalitetssjekker.

## Entra ID-oppsett

1. **App-registrering**
   - Gå til Azure Portal → Entra ID → App registrations → *New registration*.
   - Navn: `PrioritiAI-n8n`
   - Kontotilganger: *Accounts in this organizational directory only*.
   - Redirect URI (Web): `https://<din-n8n-host>/rest/oauth2-credential/callback`

2. **Legg til delegert tilgang**
   - API Permissions → Microsoft Graph → Delegated → legg til `Mail.Read`, `User.Read` og `offline_access`.
   - Gi admin consent for organisasjonen.

3. **Generer klienthemmelighet**
   - Certificates & secrets → *New client secret*. Noter verdi (brukes i n8n-creds).

4. **Konfigurer n8n**
   - Opprett en ny `Microsoft OAuth2 API` credential i n8n.
   - Sett `clientId`, `clientSecret`, `tenant` og redirect-URL (samme som over).
   - Autoriser brukeren (admin/service-konto) som skal lytte på mailboksen.

5. **Teams webhook**
   - I ønsket kanal: *Connectors* → *Incoming Webhook* → Navngi og kopier URL.
   - Legg inn i `.env` som `TEAMS_WEBHOOK_URL` og referer i n8n HTTP-node.

## Databaseskjema

Tabellen `prioai_task` inneholder alle felter som heuristikken fyller ut: delskår (0–10), totalt AI-score (0–100), status (`incoming`, `approved`, `in_progress`, `done`) og mulighet for manuell overstyring (`override_priority`, `override_locked`). Indeksene på `status` og `due_at` gir rask filtrering i UI og rapporter.

## AI-tjenesten

`ai/service.py` kombinerer håndlagde regler (FastRules) med valgfri OpenAI-forklaring. Endepunktet `/classify` tar inn emne, brødtekst, avsender, rolle-hint, estimering og fristtekst. Heuristikken produserer delskår og en samlet `ai_score`, og LLM-en (om tilgjengelig) kan gi en kort forklaring på norsk.

## Frontend

Next.js-appen leser data direkte fra Postgres via API-ruter:
- `GET /api/tasks?status=incoming` → liste
- `PATCH /api/tasks/:id` → oppdatere status eller overstyring

Fanene **Innkommende**, **Godkjente** og **Pågående** speiler statusene i databasen. UI lar deg godkjenne, starte eller avslutte oppgaver, samt sette manuell prioritet (0–100) og låse den mot AI-oppdateringer.

## Kvalitet

- `npm run lint` i frontend validerer React/TypeScript.
- `python3 -m compileall ai/service.py` sjekker syntaks for AI-tjenesten.
- Docker Compose sørger for isolert og reproduserbar kjøring av hele stacken.

## Videre arbeid

- Sett opp Graph change notifications for sanntids-push fra Outlook/Teams.
- Legg til autentisering i frontend (Azure Entra ID / NextAuth).
- Lag flere rapporter (f.eks. tidslinje, SLA) og integrasjon mot tidsregistrering.
- Utvid heuristikken med flere regler og historikklæring.
