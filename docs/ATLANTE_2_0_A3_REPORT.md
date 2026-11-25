# Atlante 2.0 — A3 Dossier e navigazione: report

Stato: **implementata, in attesa di collaudo su iPhone** (nessuna approvazione; A4 non avviata). Build `20261125-1200-a3`. Solo TEST, produzione congelata, costo 0 €.

## 1. Funzionalità completate
- **Home immersiva** (hero con Ken Burns e anelli, ricerca, «Riprendi da dove eri», dossier in evidenza a rotazione, rail illustrata delle 10 categorie con conteggi reali, hub).
- **Catalogo illustrato**: griglia a 2 colonne e modalità elenco; filtri per tipologia, universo e continuità; filtro testuale; rendering progressivo (36 voci, poi IntersectionObserver); `content-visibility` sulle schede.
- **Ricerca globale** con risultati suddivisi per categoria (indice normalizzato, ricerca per prefisso di parola, debounce 100 ms).
- **Dossier dinamici**: sezioni previste — Identità e biografia, Origini, Storia narrativa, Poteri e capacità, Debolezze, Trasformazioni, Equipaggiamento, Apparizioni, Relazioni, Varianti e incarnazioni, Fonti e riferimenti. **Una sezione compare solo se esiste contenuto**: oggi Debolezze, Trasformazioni ed Equipaggiamento non hanno dati nel registro e non vengono mostrate (nessun testo inventato).
- **Hub multiversali** (Peter Parker 6 voci con 1 segnaposto non cliccabile, Wilson Fisk) e **mantelli** (titolari distinti, nessuna unificazione); navigazione tra identità, varianti, incarnazioni (con distinzione «cambio di interprete ≠ variante») e mantelli.
- **Apparizioni** → «Scheda» (Dossier Opera esistente) e «Timeline» (scheda del titolo nella Timeline); Indietro riporta al dossier.
- **Indietro/X** coerenti con lo stack esistente; **scorrimento e numero di voci caricate ripristinati** tornando al catalogo; Miss Minutes (pulsante globale) resta raggiungibile in ogni schermata.

## 2. Architettura (scalabilità)
- Modulo additivo e lazy: `atlante2/a3.js` + `a3.css` si scaricano solo al primo ingresso; nessun dato A3 prima. Dati generati da `tools/atlante_a3.py` dal registro A1/A2: `atlante2/data/index.json` (431 voci, 94 KB) + 18 shard `d/NNN.json` (~30 KB) caricati **uno alla volta** all'apertura del dossier. Immagini lazy.
- Pensato per migliaia di voci e >10.000 relazioni: indice per righe compatte, ricerca O(N) su stringhe normalizzate, rendering a blocchi; oltre ~10.000 voci l'indice si suddivide per tipo/iniziale senza cambiare la UI. Il Nexus (A4) non è in A3.
- Nessun HTML dai dati (solo `textContent`); i campi del registro sono convertiti in token testo/collegamento; link esterni solo `https` con `rel="noopener noreferrer"`.
- Integrazione in `index.html` limitata a: hook `EXT.over` in `draw()`, stato `a3` in `getState/setState`, blocco `tva-a3-boot` (banner + caricamento lazy). Preferenza `tva-atlante-ui=v2` per avviare dalla nuova Home (default: Home classica con banner). Atlante classico, blob, Tessera, XP, preferiti, Miss Minutes: **non modificati**.
- `sw.js`: build `20261125-1200-a3` in tutti i punti coerenti (index, sw, quiz, arcade) e precache di modulo + indice.

## 3. Collegamenti verso schede suddivise (76)
Dettaglio in `docs/ATLANTE_2_0_A3_LINK_AMBIGUI.md`.
- 44 classificazioni automatiche verificate (criterio: stesso universo o apparizioni in comune): **42 confermate**, 2 non confermate (Kate Bishop → Fisk: Bishop è sospesa) passate agli ambigui.
- **34 collegamenti ambigui** (32 + 2): tabella numerata con origine, destinazione, continuità, identità possibili e soluzione consigliata (hub dove la variante non è dimostrata; per Groot, che non ha hub, resta la scheda storica). Collegamenti originali conservati nel registro e nell'Atlante classico; la nuova UI usa l'hub **senza attribuire relazioni narrative**.

## 4. File
Nuovi: `atlante2/` (a3.js, a3.css, data/, img/), `tools/atlante_a3.py`, `tests/a3_test.py`, `docs/ATLANTE_2_0_A3_LINK_AMBIGUI.md`, questo report. Modificati: `index.html` (3 hook), `sw.js`, build id in `quiz/` e `arcade/`, roadmap, `CLAUDE.md`.

## 5. Verifiche
`tests/a3_test.py` 30/30; `atlante_estrai.py --verifica` OK (baseline A0 invariata); `atlante_identita.py --verifica` OK; `atlante_a3.py --verifica` OK. Regressione: 66 suite esistenti rieseguite; l'esito (FAIL/BLOCKED/NOT RUN) coincide con quello del commit precedente `8b6e667` rieseguito in un worktree pulito (cop, f3, fx_test2, cons, b32, td2, b40c, m32 identici); nessun controllo indebolito. `fa2_test` mostra 2 FAIL identici anche sul commit precedente (instabile sotto carico) ed è stato documentato in `tests/KNOWN_FAILS.json`. ZIP: `NETLIFY_TEST_a3.zip`, SHA-256 5979f41a7c055206e9907e509f677d47d33b589d55ad325339a233e13bb3fc7c.

## 6. Aperti / limiti dichiarati
- Nessun ritratto specifico disponibile e legittimo: emblemi con iniziali (non sono ritratti).
- Debolezze/Trasformazioni/Equipaggiamento: struttura pronta, nessun dato → sezioni assenti.
- Relazioni mostrate = collegamenti «Correlati» della guida (co-apparizioni, non relazioni narrative) + relazioni tipizzate del registro (5 narrative, 2 non narrative). Il Nexus è in A4.
- Fonti ancora secondarie (completamento con fonti primarie in A7); Bishop e Janet sospese.
- Mappa del Multiverso, confronto affiancato, collezioni e progressione non sono in A3 (fasi successive).
