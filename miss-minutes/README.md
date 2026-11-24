# Miss Minutes 1.0 (TEST)

Assistente della TVA integrato in TVA Archives. Pagina in iframe a stessa origine (`miss-minutes/index.html`), aperta dal pulsante rapido ⏱ presente in tutte le sezioni dell'app.

| File | Ruolo |
|---|---|
| `engine.js` | motore locale offline: indice (Knowledge Core + personaggi/relazioni/poteri/universi/titoli dell'app), intenti (scheda, confronto, relazioni, consigli, progressi, voti, Live), spoiler, contesto per il gateway |
| `knowledge/core.json` | Knowledge Core: 62 schede curate (id, nome, alias, categoria, universo, testo, fonte, `spoiler`, `verification`). Si estende aggiungendo record: nessun altro file da toccare |
| `store.js` | cronologia locale (max 40 chat × 120 messaggi), preferenze |
| `gateway-client.js` | sessione per dispositivo (proof-of-work), chiamata al gateway, messaggi d'errore espliciti |
| `app.js`, `index.html`, `mm.css` | interfaccia, mascotte animata, voce (dettatura e lettura dove supportate), consenso AI |
| `gateway/` | Worker Cloudflare + Durable Object, `DEPLOY.md` |
| `tests/` | `engine_test.js`, `gateway_test.mjs`, `e2e_gateway_test.mjs`, `ui_test.py` |

Contratto con l'app (`window.tvaMissMinutesHost`, in `index.html`, blocco `mm-host`): oggetto congelato, sola lettura — `titles()`, `live()`, `blob(nome)` (solo 6 JSON statici in whitelist), `open(link)`, `close()`. Link: `item:089`, `char:char-loki`, `uni:…`, `arc:cat:id`, `tab:timeline|atlante|tessera|friends|home|missioni`, `cen:live|missioni|…`, `page:arcade|quiz|rankings`.
Predisposto per Dossier, Quiz e Arena: basta leggere `knowledge/core.json` (stesso schema) e aggiungere nuove sorgenti all'adattatore.

## Protezione spoiler: cosa fa e cosa no
Le schede con `spoiler: true` sono nascoste finché l'utente non preme «Mostra comunque». Le schede spoiler non vengono mai inviate all'AI online. L'app non conosce i contenuti narrativi dei titoli e l'AI online può rivelare dettagli: la protezione è un aiuto **non garantito** e l'interfaccia lo dice.
