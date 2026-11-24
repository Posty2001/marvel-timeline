# Gateway Miss Minutes — attivazione (una volta sola)

## Perché Cloudflare mostrava «No Durable Object found»
Una classe Durable Object esiste solo dopo un deploy che contiene la **migrazione** (`new_sqlite_classes = ["Limiter"]`).
Il Worker `miss-minutes-api` era stato caricato dal solo editor del dashboard, che non può dichiarare migrazioni: per questo il menu
del binding `LIMITER` era vuoto. Il file `wrangler.toml` di questa cartella contiene classe, binding e migrazione: basta un deploy con Wrangler.
Sul piano **Workers Free** i Durable Object sono disponibili solo con storage SQLite (è già così in questa configurazione).

## Procedura da iPhone, senza terminale (GitHub Actions)
Il deploy è un workflow manuale nel repository **Posty2001/tva-live-scheduler** (`Miss Minutes - gateway`). Aggiorna il Worker esistente `miss-minutes-api`, applica la migrazione SQLite della classe `Limiter` e il binding `LIMITER`, e imposta `APP_ORIGINS = https://tva-archives-test-1110.netlify.app`. Non tocca `marvel-timeline` né nessun `main` dell'app. Il sorgente in quel repository è una copia di `miss-minutes/gateway/` (stesso `worker.ts`).

### A. Token Cloudflare con permessi minimi (Safari, se serve «Sito desktop»)
1. dash.cloudflare.com → icona profilo in alto → **My Profile** → **API Tokens** → **Create Token** → **Create Custom Token → Get started**.
2. Nome: `github-miss-minutes-deploy`.
3. **Permissions** (due righe): `Account` · `Workers Scripts` · `Edit`, poi **Add more**: `Account` · `Account Settings` · `Read`.
4. **Account Resources**: `Include` · `Specific account` · scegli il tuo account. Nessuna risorsa di zona/dominio.
5. **Client IP Address Filtering**: lascia vuoto (gli indirizzi di GitHub cambiano). **TTL**: consigliata una scadenza (es. tra 30 giorni).
6. **Continue to summary → Create Token**. Copia il token (si vede una volta sola).
7. Copia anche l'**Account ID**: Workers & Pages → colonna a destra «Account ID».
Se il workflow fallisse con un errore di permesso, il log indica quale: aggiungi solo quello.

### B. Segreti su GitHub
Repository tva-live-scheduler → **Settings → Secrets and variables → Actions → New repository secret**:
- `CLOUDFLARE_API_TOKEN` = il token del passo A
- `CLOUDFLARE_ACCOUNT_ID` = l'Account ID
(`GEMINI_KEY` si aggiunge più avanti, solo quando attivi l'AI. `SESSION_SECRET` lo genera il workflow e lo salva direttamente su Cloudflare, senza che nessuno lo veda.)

### C. Esecuzione
1. **Actions → Miss Minutes - gateway → Run workflow**: prima `action = check` (solo controlli, nessun contatto con Cloudflare), poi `action = deploy` lasciando **AI spenta**.
2. A fine esecuzione il riepilogo del run mostra l'**indirizzo del gateway** (`https://miss-minutes-api.….workers.dev`). Incollalo in **Miss Minutes → ⚙ Impostazioni → Indirizzo del gateway → Salva**: l'app verifica che risponda (deve dire «AI ancora spenta»).

### D. Attivazione dell'AI (solo dopo la verifica del piano gratuito)
1. Google AI Studio: la chiave deve appartenere a un progetto **senza account di fatturazione** e il modello (`GEMINI_MODEL`, default `gemini-3.5-flash-lite`, verificato da te con 10 RPM e 20 richieste/giorno) deve avere in «Rate limits» un limite gratuito > 0.
2. GitHub: aggiungi il secret `GEMINI_KEY`.
3. Run workflow con `action = deploy`, `enable_gemini` e `free_tier_checked` entrambi acceso. Il workflow carica la chiave su Cloudflare e imposta `FREE_TIER_VERIFIED=yes`. Per spegnere di nuovo: nuovo deploy con `enable_gemini` spento.

## Come funzionano sicurezza e costi
- **Nessuna chiave nell'app.** Ogni dispositivo ottiene un token firmato (24 h) dopo una piccola proof-of-work (qualche decimo di secondo) e un limite di 8 sessioni/ora per IP. Nessun token condiviso nel codice pubblico.
- **Limiti persistenti** (Durable Object, contati prima di chiamare Google, tarati sul piano gratuito 10 RPM / 20 al giorno): globale 8 al minuto, 18 al giorno (giorno Pacific, come le quote Google) e 500 al mese; per IP 10/giorno e 6/minuto; per dispositivo 10/giorno. Dopo 20 richieste non valide in un'ora l'IP viene bloccato. Modificabili in `wrangler.toml`.
- **Nessun costo automatico:** Cloudflare Workers resta sul piano Free (non attivare «Workers Paid»); la chiave Gemini è in un progetto senza fatturazione, quindi superata la quota le richieste falliscono e l'app usa il motore locale. Nessun retry automatico.
- **Limite onesto:** senza CAPTCHA, un automatismo ostinato potrebbe consumare la quota giornaliera (denial of service sul solo servizio AI, mai costi). L'app continua a funzionare in locale.
- **Privacy:** al gateway arrivano domanda, fino a 4 schede pubbliche e gli ultimi messaggi; mai visti, voti, note, amici. Nel piano gratuito Google può usare i contenuti inviati per migliorare i propri prodotti (l'app lo dice nel consenso).
- Il gateway non salva testi né domande: il Durable Object contiene solo contatori con scadenza, e l'IP solo come hash firmato.

## Cosa NON ho potuto verificare dalla mia sandbox
`wrangler`/`workerd` non sono installabili qui (rete npm bloccata), Cloudflare e Gemini non sono raggiungibili. La logica del Worker e del Durable Object è testata in Node con un Durable Object simulato su SQLite (`tests/gateway_test.mjs`, `tests/e2e_gateway_test.mjs`); la sintassi del workflow è validata, ma il primo `check` su GitHub (che compila il Worker con Wrangler) e il primo `deploy` sono la verifica reale.
