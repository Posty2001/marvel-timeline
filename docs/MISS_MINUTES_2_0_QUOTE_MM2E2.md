# Miss Minutes 2.0 — diagnosi 429 e gestione quote (mm2e.2)

Build `20261127-1700-mm2e2` · solo TEST · produzione congelata · 0 € · A5 sospesa. **In attesa di collaudo reale; gateway da ridistribuire dall'utente.**

## 1. Quale limite è stato raggiunto
Dalla diagnostica mm6.1: codice `quota`, stadio **gateway**, HTTP 429, 502 ms, 1 tentativo. Significa che **a rifiutare è stato il gateway di Miss Minutes prima di chiamare Google** (un 429 di Google avrebbe codice `provider-quota`, stadio `gemini`, e una durata di migliaia di ms).
Quale dei sei contatori non è però ricostruibile: il gateway restituiva `scope` solo come lettera (`i`, `v`, `g`) e l'app non lo mostrava. Candidati (valori attuali): rete 6/minuto; rete 100/giorno; **dispositivo 100/giorno (UTC)**; globale 12/minuto; globale 450/giorno (Pacific); globale 12.000/mese. Il più probabile è il tetto **dispositivo 100/giorno**: nella stessa giornata sono state fatte la valutazione da 81 domande e il collaudo mm2e/mm2e.1. È un'inferenza, non un dato.

## 2. Limiti realmente disponibili sul piano gratuito Gemini — NON verificati, quindi nessun limite è stato alzato
- La documentazione ufficiale (ai.google.dev/gemini-api/docs/rate-limits) **non pubblica i valori del piano gratuito**: rimanda ad AI Studio. Indica solo: limiti per progetto (non per chiave), RPM/TPM/RPD, **RPD azzerata a mezzanotte (fuso Pacific)**.
- Nel progetto due documenti si contraddicono: `DEPLOY.md` §D riporta «10 RPM e 20 richieste/giorno» (letto da te per `gemini-3.5-flash-lite`), mentre il paragrafo sui limiti citava «15 RPM / 500 al giorno» come ipotesi mai verificata (corretto in questa versione). Anche il tuo uso reale (79 risposte online in una sessione) è incompatibile con 20/giorno: i valori del tuo progetto vanno riletti.
- **Cosa serve da te:** AI Studio → «Rate limits» (progetto della chiave, senza fatturazione) → copiare RPM, TPM e RPD del modello in uso. Con quei numeri si decide il tetto.
- Valutazione dell'aumento 100 → 200: il gateway lo consente (`DEVICE_DAILY_CAP`/`IP_DAILY_CAP` in `wrangler.toml`, massimo 1000; il globale 450 resta vincolo) ma è sensato **solo se l'RPD gratuita di Google è ≥ 200 per tutta la giornata** (e il tetto globale `DAILY_CAP` non va oltre la RPD reale, con margine). Altrimenti sarebbe Google a rifiutare (429 `provider-quota`) senza guadagno. Nessuna modifica fatta.
- Nota: i reset giornalieri non coincidono — dispositivo/rete a mezzanotte UTC (01:00 italiane), globale e Google a mezzanotte Pacific (09:00 italiane circa).

## 3. Modifiche (tutte a costo zero, nessuna protezione rimossa)
**Gateway** (`worker.ts`; copia in repo scheduler, nessun deploy):
- il 429 ora porta `scope` leggibile, `kind` (temporaneo/giornaliero/mensile), `source` (`gateway`|`gemini`), `limit`, `used`, `resetAt` (epoch), `retryAfter` e header `Retry-After`;
- per Google: tipo ricavato da `quotaId`/`retryDelay`/messaggio, ripristino = tempo indicato da Google o mezzanotte Pacific, «sconosciuto» se non classificabile (mai inventato);
- nuovo `GET /v1/quota` (token richiesto): residuo di ogni contatore, limite più stringente e orario di ripristino, **senza consumare richieste e senza chiamare Google**;
- tetti, proof-of-work, blocco IP, sessioni/ora, nessun retry: invariati.
**App**:
- messaggio esplicito: «Limite di Miss Minutes, non di Google: hai esaurito il limite giornaliero di questo dispositivo (100 richieste). Torna disponibile domani alle 01:00 (ora italiana).» / «Limite di Google, non di Miss Minutes: è esaurita la quota giornaliera gratuita…»; al minuto: «Riprova tra N secondi»;
- limite noto → **nessuna nuova richiesta** (né ricerche esterne) fino al ripristino; «Riprova» controlla prima il residuo e rimuove il blocco se ci sono richieste disponibili; i `quota` non sono mai ritentati automaticamente;
- Diagnostica: pulsante «Richieste disponibili» (residuo per ambito, limite più stringente, orari in ora italiana) e riga «Limite raggiunto» con origine/ambito/tipo;
- nota onesta nella schermata: i limiti di Google non sono leggibili dal gateway.
**Valutazione (123 domande)**: salvataggio dopo ogni risposta; a quota giornaliera/mensile/sconosciuta la serie si **sospende** (il record non completato non viene salvato come fatto); «Riprendi (salta le già completate)» non ripete le domande completate e ricostruisce il contesto dei seguiti; un limite al minuto viene atteso fino al ripristino indicato con un solo nuovo tentativo.

## 4. Verifiche
`gateway_test` 70/70 (scope, tipo, ripristino, `/v1/quota` senza consumo, parsing 429 Google), `quota_test.js` 17/17 (testi, client, sospensione e ripresa), `ui_quota_test.py` 12/12. Regressioni complete (verify 45, lookup 14, archive 18, engine 42, quota 17, gateway 70, ui_quota 12, ui_viewport 18, ui_c1 10, ui_eval 16, ui_tmdb 12, ui_stream 26, ui_scroll 11, ui_mm61 9, ui_test 67, ui_mm6 35, ui_mm2 27): tutte superate. Non verificato: comportamento con i veri 429 di Google (formato dei `details` assunto dalla documentazione), orari in Safari iOS.
