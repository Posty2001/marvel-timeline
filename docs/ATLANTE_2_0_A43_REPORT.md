# Build a43 (TEST) – report delle modifiche e delle verifiche
Data: 26/11/2026 · branch `test/tva-archives` · produzione (`main`) congelata · budget 0 € · A5 NON avviata.
Dati personali, ritratti privati, cronologia, preferiti, voti, XP: non toccati. Gateway Miss Minutes: **non modificato** (nessuna ridistribuzione necessaria).

## 1. Home TVA Atlas – portali compatti
- L'accesso all'Osservatorio è ora un **portale premium compatto** (~140 px, 130 px sotto i 360 px): miniatura animata della mappa a sinistra (rotazione lenta, disattivata con «riduci movimento»), titolo, breve sottotitolo e freccia a destra; **l'intera scheda è cliccabile**. Rimossi descrizione lunga e pulsanti ridondanti.
- **TVA Nexus** e **Percorsi** sono due portali compatti affiancati (≤ 90 px). Stile nero/oro/Spectral invariato. La mappa interattiva vera e propria non è stata ridotta.
## 2. Miss Minutes – velocità di visualizzazione
- Nuova preferenza **locale** «Velocità di lettura» (Impostazioni): **Lenta 25 / Normale 45 (predefinita) / Rapida 80 caratteri/s** (valori iniziali da calibrare). Non viene inviata al gateway (verificato nel payload).
- Pacer: ritmo quasi costante pari al valore scelto; se la rete consegna a raffiche l'arretrato si smaltisce con recupero dolce, **al massimo 1,25× il ritmo scelto**; nessuna pausa artificiale. Tempo massimo di smaltimento dinamico (arretrato/ritmo + 15 s).
- Misurato con raffica totale (caso peggiore): Lenta ≈ 31, Normale ≈ 56, Rapida ≈ 100 car/s; con flusso regolare il ritmo coincide col valore scelto.
- Corretti due effetti collaterali emersi con testi più lunghi: `overflow-anchor:none` sulla chat (spostamento di 12 px della bolla) e ricostruzione del contenuto in un'unica operazione. Streaming reale, interruzione, Markdown e scroll invariati.
## 3. Dati del Multiverso – Fantastici Quattro
Causa: una sola identità per personaggio (Reed, Sue, Johnny, Ben, Doom) aggregava incarnazioni di continuità diverse sotto Earth-121698, quindi Terra-828 mostrava solo Franklin e Galactus.
Correzione (schema Wolverine/Harry/Matt, **nessuna unificazione**; ID e pagine canoniche originali invariati, ritratti/preferiti salvati restano sugli ID originali, che coprono i film di Tim Story N°029-030):
- 1994 (N°028, mai distribuito): Hyde-White, Staab, Underwood, Bailey Smith, Culp.
- Tim Story (Earth-121698, ID originali): Gruffudd, Alba, Evans, Chiklis, McMahon.
- Trank 2015 (N°031, Earth-TRN123): Teller, Mara, Jordan, Bell, Kebbell.
- First Steps (N°125, Earth-828): Pedro Pascal, Vanessa Kirby, Joseph Quinn, Ebon Moss-Bachrach (+ Franklin, Galactus già presenti).
- Reed Richards Illuminati (N°102, Terra-838): John Krasinski.
Totale identità: 300 → **315** (+15). Fonti: Wikipedia (schede dei film), Marvel/MCU Wiki; interpreti da fonti consultate il 26/11/2026.
**Discrepanza segnalata (non risolta, non inventata):** Johnny Storm in *Deadpool & Wolverine* (N°117): Marvel Wiki lo colloca in Earth-121698, `mvMapData` in Fox-Verse. Resta sull'identità Story con nota; da decidere se serve.
Relazioni: quelle esistenti restano sugli ID originali (film Story). **Non** sono state aggiunte relazioni per First Steps/1994/Trank/Illuminati (nessuna verifica documentale ancora eseguita; nessuna inventata).
## 4. Parole spezzate nelle schede
`overflow-wrap` portato a `normal` nei titoli delle schede e riduzione automatica del corpo (min 9 px) quando una parola supera la larghezza (`fitTitles`, ricalcolata al resize). Verificato su Terra-828 a 390 e 430 px.
## 5. A4.3 – Percorsi e confronti
- **Percorsi**: linguette «Percorso tra identità / Confronto tra universi»; pulsante **Inverti**; ogni passo mostra identità e universo; **«Apri nel TVA Nexus»** per ogni percorso.
- **Confronto tra universi** (nuova vista `cp`, raggiungibile da Percorsi e dal pannello della mappa con «Confronto dettagliato»): titoli in comune (con N° e nome), controparti dichiarate (con livello di verifica), identità presenti solo in A / solo in B; inversione A/B; stato ripristinabile. Solo dati del registro; co-apparizioni ≠ relazioni; incarnazioni distinte restano distinte. Nessun XP/badge.
- Dati: `data/nexus/g.json` ora include `ut` (titoli per universo).
## 6. Verifiche
`tests/a43_percorsi_test.py` 33/33 (nuovo); `tests/a43_test.py` 73/73 (portali); a3 32/32, a31 40/40, a32 21/21, a33 12/12, a34 9/9, a35 5/5, a40, a41, a42 OK; Miss Minutes: `ui_stream_test` 26/26 (incl. velocità), `gateway_test` 53/53, `engine_test` 37/37, ui_test, ui_mm6, ui_mm61 10/10; catena dati `--verifica` (estrai, identità incl. nuovo controllo FF, a3, relazioni, a4) tutte OK.
**Non verificato:** Safari iOS reale (WebKit non disponibile nell'ambiente): da collaudare su iPhone (portali, velocità di scrittura, confronto).
## 7. Stato
In attesa di collaudo a43. **A5 non avviata.** Nessuna funzionalità dichiarata «completata» senza approvazione dell'utente.
