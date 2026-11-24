# Gateway Miss Minutes — attivazione (una volta sola)

## Perché Cloudflare mostrava «No Durable Object found»
Una classe Durable Object esiste solo dopo un deploy che contiene la **migrazione** (`new_sqlite_classes = ["Limiter"]`).
Il Worker `miss-minutes-api` era stato caricato dal solo editor del dashboard, che non può dichiarare migrazioni: per questo il menu
del binding `LIMITER` era vuoto. Il file `wrangler.toml` di questa cartella contiene classe, binding e migrazione: basta un deploy con Wrangler.
Sul piano **Workers Free** i Durable Object sono disponibili solo con storage SQLite (è già così in questa configurazione).

## Procedura (Windows, ~10 minuti)
1. Installa Node.js LTS (nodejs.org). Apri PowerShell nella cartella `miss-minutes\gateway` dello ZIP.
2. `npx wrangler login` → si apre il browser, accedi a Cloudflare e autorizza.
3. Apri `wrangler.toml` e imposta **solo** `APP_ORIGINS` con l'indirizzo esatto del tuo sito TEST (https, senza `/` finale), per esempio
   `APP_ORIGINS = "https://nome-del-tuo-sito.netlify.app"`. Più origini: separate da virgola. Lascia `FREE_TIER_VERIFIED = "no"` per ora.
4. `npx wrangler deploy` → crea/aggiorna il Worker `miss-minutes-api`, la classe `Limiter` e il binding `LIMITER`. Annota l'indirizzo `https://miss-minutes-api.<tuo-sottodominio>.workers.dev`.
5. Segreti (si digitano nel terminale, mai in chat, mai in file del progetto):
   - `npx wrangler secret put GEMINI_KEY` → incolla la chiave di Google AI Studio.
   - Genera una stringa casuale: `node -e "console.log(require('crypto').randomBytes(32).toString('base64url'))"`, poi `npx wrangler secret put SESSION_SECRET` e incollala. È la sola chiave con cui il gateway firma le sessioni dei dispositivi; non va mai messa nell'app.
   (In alternativa: dashboard Cloudflare → Workers → miss-minutes-api → Settings → Variables and Secrets → tipo «Secret».)
6. **Verifica il piano gratuito** (obbligatoria, la fai tu): in Google AI Studio → la chiave deve appartenere a un progetto **senza account di fatturazione**; apri «Rate limits» e controlla che il modello in `GEMINI_MODEL` abbia un limite gratuito diverso da 0. Se il nome del modello è diverso da `gemini-3.5-flash-lite`, correggi `GEMINI_MODEL` in `wrangler.toml`. Se il modello non risulta gratuito, non attivare.
7. Quando sei sicuro: `FREE_TIER_VERIFIED = "yes"` in `wrangler.toml` e di nuovo `npx wrangler deploy`.
8. Nell'app: in `miss-minutes/config.js` imposta `endpoint: 'https://miss-minutes-api.<tuo-sottodominio>.workers.dev'`, ricrea lo ZIP TEST e caricalo su Netlify TEST come sempre.
9. Prova: dalla pagina Miss Minutes → ⚙ → «AI online» → consenso. Controllo diretto del gateway (PowerShell):
   `curl.exe -H "Origin: https://nome-del-tuo-sito.netlify.app" https://miss-minutes-api.<sottodominio>.workers.dev/v1/health` → `{"ok":true,"enabled":true}`.

## Come funzionano sicurezza e costi
- **Nessuna chiave nell'app.** Ogni dispositivo ottiene un token firmato (24 h) dopo una piccola proof-of-work (qualche decimo di secondo) e un limite di 8 sessioni/ora per IP. Nessun token condiviso nel codice pubblico.
- **Limiti persistenti** (Durable Object, contati prima di chiamare Google): globale 150/giorno e 3000/mese (UTC), per IP 40/giorno e 6/minuto, per dispositivo 30/giorno. Dopo 20 richieste non valide in un'ora l'IP viene bloccato. Modificabili in `wrangler.toml`; tienili sotto il limite gratuito di Google.
- **Nessun costo automatico:** Cloudflare Workers resta sul piano Free (non attivare «Workers Paid»); la chiave Gemini è in un progetto senza fatturazione, quindi superata la quota le richieste falliscono e l'app usa il motore locale. Nessun retry automatico.
- **Limite onesto:** senza CAPTCHA, un automatismo ostinato potrebbe consumare la quota giornaliera (denial of service sul solo servizio AI, mai costi). L'app continua a funzionare in locale.
- **Privacy:** al gateway arrivano domanda, fino a 4 schede pubbliche e gli ultimi messaggi; mai visti, voti, note, amici. Nel piano gratuito Google può usare i contenuti inviati per migliorare i propri prodotti (l'app lo dice nel consenso).
- Il gateway non salva testi né domande: il Durable Object contiene solo contatori con scadenza, e l'IP solo come hash firmato.

## Cosa NON ho potuto verificare dalla mia sandbox
`wrangler`/`workerd` non sono installabili qui (rete npm bloccata), Cloudflare e Gemini non sono raggiungibili. La logica del Worker e del Durable Object è testata in Node con un Durable Object simulato su SQLite (`tests/gateway_test.mjs`, `tests/e2e_gateway_test.mjs`); il deploy reale, il binding e la chiamata a Gemini restano da verificare con i passi 4–9.
