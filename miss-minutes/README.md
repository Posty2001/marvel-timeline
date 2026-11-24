# Miss Minutes 1.0 (TEST) — build mm6.1 (hotfix scorrimento)

Assistente della TVA integrato in TVA Archives. Pagina in iframe a stessa origine (`miss-minutes/index.html`), aperta dal pulsante rapido ⏱ presente in tutte le sezioni dell'app.

| File | Ruolo |
|---|---|
| `engine.js` | motore locale offline: indice (Knowledge Core + personaggi/relazioni/poteri/universi/titoli dell'app), intenti (scheda, confronto, relazioni, consigli, progressi, voti, Live), spoiler, contesto per il gateway |
| `knowledge/core.json` | Knowledge Core: 62 schede curate (id, nome, alias, categoria, universo, testo, fonte, `spoiler`, `verification`). Si estende aggiungendo record: nessun altro file da toccare |
| `store.js` | cronologia locale (max 40 chat × 120 messaggi), preferenze |
| `gateway-client.js` | sessione per dispositivo (proof-of-work), chiamata al gateway, messaggi d'errore espliciti |
| `app.js`, `index.html`, `mm.css` | interfaccia, mascotte animata, voce (dettatura e lettura dove supportate), consenso AI |
| `gateway/` | Worker Cloudflare + Durable Object; deploy via GitHub Actions (`DEPLOY.md`) |
| `tests/` | `engine_test.js`, `gateway_test.mjs`, `e2e_gateway_test.mjs`, `ui_test.py` |

Contratto con l'app (`window.tvaMissMinutesHost`, in `index.html`, blocco `mm-host`): oggetto congelato, sola lettura — `titles()`, `live()`, `blob(nome)` (solo 6 JSON statici in whitelist), `open(link)`, `close()`. Link: `item:089`, `char:char-loki`, `uni:…`, `arc:cat:id`, `tab:timeline|atlante|tessera|friends|home|missioni`, `cen:live|missioni|…`, `page:arcade|quiz|rankings`.
Predisposto per Dossier, Quiz e Arena: basta leggere `knowledge/core.json` (stesso schema) e aggiungere nuove sorgenti all'adattatore.

## Protezione spoiler: cosa fa e cosa no
Le schede con `spoiler: true` sono nascoste finché l'utente non preme «Mostra comunque». Le schede spoiler non vengono mai inviate all'AI online. L'app non conosce i contenuti narrativi dei titoli e l'AI online può rivelare dettagli: la protezione è un aiuto **non garantito** e l'interfaccia lo dice.


## mm6.1 — hotfix scorrimento (25/11/2026)
Solo comportamento di scorrimento della chat: all'arrivo di una risposta la vista parte dall'**inizio** del nuovo messaggio (nessuno scorrimento automatico fino in fondo); all'invio restano visibili domanda e indicatore di attesa; una freccia verso il basso (`#mmDown`) compare solo quando la fine della conversazione è fuori vista; la persistenza dello scorrimento di mm6 è invariata. Nessuna modifica a grafica, gateway, prompt o altre funzioni. Test: `miss-minutes/tests/ui_mm61_test.py` (10 controlli).

## mm6 — componente globale, persistenza, instradamento
- **Componente globale** (`mm-host` in `index.html`): pulsante e overlay sono figli di `<html>`, non di `<body>`, quindi non sono raggiungibili dalle regole dell'app che nascondono i fratelli di `#homeHubExited` (era la causa della scomparsa in Home, Tessera, Friends, Classifiche). Nessuna sezione deve registrarlo: le sezioni future lo ereditano. Il pulsante è trascinabile in verticale (posizione salvata in `tva-mm-fab-y`) per evitare i controlli di una sezione. Quiz e Arcade sono documenti separati e **non** lo includono (decisione da prendere: i giochi hanno timer in tempo reale).
- **Chiusura vs indietro**: la X (sempre visibile in tutte le schermate) chiude l'assistente e ripristina sezione e scorrimento di provenienza (`tva-mm-host-v1`); la freccia torna alla schermata precedente dell'assistente.
- **Persistenza**: l'host salva apertura/provenienza e la pagina salva schermata, bozza e scorrimento (`marvel-ultimate-timeline-miss-minutes-ui-v1`, chiave separata dalla cronologia, nessuna migrazione) su `visibilitychange`, `pagehide`, `blur`, `freeze` e a ogni scorrimento/digitazione (debounce 250 ms). Alla ripartenza (ricarica della pagina o del solo iframe) l'assistente si riapre sulla stessa schermata se l'ultimo uso è di meno di 45 minuti. Una richiesta AI interrotta lascia solo il messaggio utente già salvato: compare «Domanda in attesa» con Riprova manuale, mai un invio automatico. Una nuova chat nasce solo da «Nuova conversazione».
- **Diagnostica**: avvii della pagina, tipo di avvio (`reload`/`navigate`/`back_forward`), ripristino e ultimi eventi del ciclo di vita (senza testi delle conversazioni).
- **Instradamento**: con AI online attiva l'archivio locale risponde solo a richieste semplici (scheda, dato puntuale, dati dell'app); domande teoriche, comparative, ipotetiche, sul futuro o contestuali vanno a Gemini con l'archivio come contesto. Il prompt distingue confermato / ipotesi / indiscrezioni.
