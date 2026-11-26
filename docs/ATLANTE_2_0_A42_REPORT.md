# Build a42 (TEST) – report delle modifiche e delle verifiche
Data: 26/11/2026 · branch `test/tva-archives` · produzione (`main`) congelata · budget 0 € · A5 NON avviata.
Build id: `20261126-1334-a42` (index.html, sw.js, arcade/index.html, quiz/index.html). Dati personali, ritratti privati, cronologia, preferiti, voti, XP: non toccati (nessuna modifica a storage, chiavi, dati dei ritratti).

## 1. Miss Minutes – streaming (causa effettiva)
**Misura sul gateway distribuito** (sonda `Miss Minutes - sonda streaming`, 1 sola richiesta reale, tempi/dimensioni dei chunk, nessun segreto):
- Cloudflare **invia davvero lo stream**: 25 chunk (`transfer-encoding: chunked`, `text/event-stream`, nessuna compressione).
- Gemini consegna il testo **a raffiche**: intestazioni dopo ~5,9 s (latenza del primo token), poi 5 chunk in 0,4 s, **pausa di 3,8 s**, poi 20 chunk (~1.650 caratteri) in meno di 1 s. Per l'occhio la risposta compare «tutta insieme» anche se la rete è progressiva.
- Il service worker non intercetta `*.workers.dev` (verificato nel codice); il parsing SSE e il rendering erano corretti nei test, ma mostravano i chunk così come arrivavano.
- **Non verificato direttamente su Safari iOS** (nell'ambiente non ci sono WebKit né iPhone). Ipotesi nota: WebKit/CFNetwork può accumulare i primi byte prima di consegnarli a `fetch`; mitigata (vedi sotto), da confermare al collaudo.

**Correzioni**
- App: *pacer* di visualizzazione (`miss-minutes/app.js`): il testo ricevuto va in coda e compare a ritmo regolare (≥70 caratteri/s, e comunque smaltendo l'arretrato in ~2,4 s di costante di tempo), senza salti, anche con raffiche. A fine stream la coda viene mostrata fino in fondo. Nessuno scroll automatico; la bolla resta ferma dove l'utente sta leggendo. **Interrompi** conserva solo il testo già mostrato; errori/connessione interrotta conservano il testo ricevuto. Nessun nuovo tentativo dopo testo parziale.
- Gateway (`worker.ts`, solo risposta in streaming): prologo SSE di ~2 KB (commento ignorato dal client), `Cache-Control: no-store, no-transform`, `X-Content-Type-Options: nosniff`; annullamento della richiesta a monte anche al raggiungimento del tetto di 4000 caratteri. Invariati: segreti, autenticazione, limiter, modello, quote, `wrangler.toml`, TVA Live.
- Limite residuo (non risolvibile senza cambiare il modello): l'attesa iniziale di ~6 s e la pausa intermedia sono la latenza di Gemini.
**Verifiche**: `ui_stream_test` 21/21 (include raffica a 1 evento: ≥15 stadi in >2 s, nessun salto >25%, posizione stabile, Interrompi nello smaltimento); `gateway_test` 53/53; ui_test 67, mm6 35, mm61 10, engine 37, e2e_gateway 8.
**Gateway**: aggiornamento da ridistribuire (workflow `Miss Minutes - gateway`): commit `b41b01a` su `tva-live-scheduler`; backup `backup/gateway-streaming-v1-9bc2ed5` (versione streaming precedente) e `backup/gateway-pre-streaming-20261126` (prima dello streaming).

## 2. Osservatorio del Multiverso (mappa) in primo piano
La mappa era raggiungibile (modulo lazy `a4.js`) ma solo da una sezione a metà Home. Ora: pulsante primario **«Osservatorio del Multiverso»** nella hero (visibile senza scorrere) + scheda dedicata subito sotto la hero con anteprima della mappa (stesse orbite e colori) e le azioni Apri la mappa / TVA Nexus / Percorso; testo che distingue mappa e catalogo. Il catalogo Universi mostra un invito a usare la mappa. Titolo della vista: «Osservatorio del Multiverso». Hero ancora ≤ 335 px (limite approvato); «Atlante classico» spostato in fondo alla Home.

## 3. Catalogo universi
- Numeri Terra non più tagliati (emblema in `meet`, corpo adattato al numero di cifre).
- Titolo = denominazione completa (es. «Terra-199999 · MCU»); classificazione in pillola separata.
- Colori ed emblemi per universo: tinta propria (stessa funzione `uniHue` della mappa → stessa tinta nel catalogo e nel nodo) + simbolo per natura documentata (raggi/ramo/satellite/esagono) con i colori delle orbite.
- «Hub multiversali» → **«Hub di identità»** (Home, catalogo, dossier, ricerca); Groot resta hub di continuità.

## 4. TVA Nexus
Etichette dei nodi brevi (alias/nome breve; nome completo nel titolo, nell'elenco e nel dossier), senza parole spezzate; identità con lo stesso alias distinte (nome civile + qualificatore: universo/produzione); **relazioni multiple**: un nodo mostra tutte le relazioni documentate della classe migliore (es. Iron Man–Steve Rogers: amicizia + rivalità) con tratti paralleli e una riga per relazione, ciascuna con il proprio stato di verifica; nulla è presentato come «solo rivali».

## 5. A4.2 (da `ATLANTE_2_0_A4_PROPOSTA.md`, fase Nexus)
Percorso esplorato toccabile (trail), filtri per tipo di relazione con conteggi, relazioni multiple, etichette. «Apri nel Nexus» dai dossier (identità e organizzazioni) già presente da A4.1. Co-apparizioni ≠ relazioni (invariato); nessun XP/badge (A5).

## 6. Barra categorie del catalogo
Causa: ogni cambio categoria ricostruiva tutta la schermata e la barra ripartiva da 0. Ora la posizione orizzontale fa parte dello stato (`cx`, salvata allo scroll), viene ripristinata a ogni rendering e al ritorno dal dossier insieme a categoria, filtri e testo; la categoria scelta viene centrata dolcemente solo se non interamente visibile (istantaneo con «riduci animazioni»). Il cambio vista non ricostruisce la barra. Provato a 390 e 430 px che **senza la correzione il test fallisce** (barra a 0) e con la correzione passa.

## Verifiche (tutte eseguite in Chromium con emulazione iPhone 390/430 px)
a43 71/71 (nuovo: Home, catalogo, barra, Nexus) · a3 32/32 · a31 40/40 · a32 21/21 · a32e 7/7 · a33 12/12 · a34 9/9 · a35 5/5 · a40 · a41 (UI e correzioni) · ui_audit 0 falliti · c3 (PWA/offline) · c4 (CSP/accessibilità) · catena dati `--verifica` (estrai, identità, a3, relazioni, a4) rc=0 · Miss Minutes: gateway 53, ui 67, mm6 35, mm61 10, stream 21, engine 37, e2e 8.
**Non verificabile qui**: Safari iOS reale (WebKit non installabile: rete non consentita). Sono state usate solo API standard (scrollTo/scrollLeft, `overscroll-behavior`, `-webkit-line-clamp`); da confermare al collaudo su iPhone, in particolare streaming (primo testo/ritmo) e barra categorie.
