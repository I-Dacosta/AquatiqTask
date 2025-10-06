Prosjektnavn: PrioritiAI
🧭 Hva er det?
PrioritiAI er et smart prosjekthåndteringsverktøy for IT-konsulenter. Systemet gir:

Oversikt over forespørsler, aksepterte saker/prosjekter og pågående arbeid.

Automatisk prioritering basert på hast, verdi, risiko og kundeprofil.

Statusdeling mot Teams-kanaler og enkel UI for rask oppfølging.

En integrasjon med Clerk for sikker autentisering.

💡 Hvorfor?
Du fikk caseoppgaver som handlet om krisehåndtering og samtidig overblikk på kritiske oppgaver.

Du skal sannsynligvis balansere support, utvikling og løpende ad-hoc oppgaver.

Det mangler ofte gode verktøy for dynamisk prioritering i slike hybridroller.

Teams brukes allerede i organisasjonen – løsningen bygger på eksisterende arbeidsvaner.

⚙️ Hvordan?
MVP Arkitektur
Frontend (Next.js + Tailwind):

Login med Clerk

Dashboard:

Tab 1: "Innkommende forespørsler"

Tab 2: "Godkjente prosjekter"

Tab 3: "Pågående arbeid"

AI-prioritering vises som score + anbefaling

Mulighet for manuell overstyring

Backend (NestJS + Prisma):

REST API eller GraphQL

PostgreSQL for lagring av saker, status og AI-prioriteringsscore

Prioriteringslogikk som vurderer:

Frist (haster)

Verdi for kunde

Risiko (f.eks. "PowerPoint før møte")

Rolle i organisasjonen

Tid brukt

AI-modul (Python microservice / serverless):

FastRules + OpenAI for vekting av prioritering

Kan utvikles videre til å lære av historikk

Integrasjoner:

Tjeneste	Formål
Outlook Mail	Leser e-poster, parser forespørsler automatisk, sender varsler/status
Outlook Kalender	Booker møter, viser tilgjengelighet, kobler saker til møter
Excel (OneDrive/SharePoint)	Leser eller oppdaterer logg-, ressurs- eller rapportfiler
Teams	Sender varsler/status, kobler til kanal, kan integreres med adaptive cards og bots

🔐 Clerk: Login + brukerprofil

⏱ Scheduler/Queue: For fremtidige varsler (kan bygges senere)

👤 Bruker-caser (basert på casene du fikk):
Case 1: CFO får ikke åpnet PowerPoint
Opprettes automatisk via skjema eller manuell input

Systemet forstår at dette haster pga. møte om 45 min

Gir høy prioritet + pusher varsling til deg + Teams

Case 2: Webshop og PowerBI-ordre feiler
Vektes som høy verdi og høy risiko

Hvis det finnes en workaround, AI foreslår det

Status meldes til Teams

Case 3: CEO får ikke synkronisert dokument
Lavere prioritet enn de to andre, men viktig pga. rolle

Systemet varsler bruker med forslag: "Se på etter CFO"

Bonus Case: Kunden klikker på svindel-lenke fredag kveld
Foreslår midlertidig handling (f.eks. frakoble nett)

Logger hendelse + merkes som sikkerhetskritisk

Kan bygges inn som kategori

🛠 Neste steg
UI-skisse og komponentoversikt – Lag wireframe for dashboard.

Datamodell – Sak, status, score, eier, type.

Mock integrasjon mot Teams og Clerk

Manuell input først, AI-prioritering i neste versjon