# Database Expansion – W1 «Espansione MCU» (27–28/11/2026) — REPORT

Stato: **pipeline, integrazione e prima raccolta reale consegnate: 286 nuove voci verificate (Livello C) + 153 arricchimenti (risolutore a regole W1.b)**. Non dichiarata completata. Build TEST `20261128-0100-db1`. 0 €, produzione congelata.

## 1. Correzioni al censimento (richieste dell'utente)
| Problema | Causa | Correzione |
|---|---|---|
| Q1235940 = Kilmogue Portal Tomb | QID scritto a mano e mai verificato | nessun QID a mano: si risolvono per **etichetta esatta** (`Marvel Cinematic Universe`) e il censimento stampa i candidati per la verifica umana |
| Query Wikidata: solo 9 elementi / 5 personaggi | QID universo errato (Q931597) e classe troppo stretta | elenco **di tutti gli universi con «Marvel» nell'etichetta** con conteggio P1080; personaggi per P1080 e per editore (P123); MCU per classe P31; sottoclassi incluse |
| `titoli_timeline` = 49 | contava le voci d'indice di tipo «titolo» (titoli con scheda Atlas) | ora `titoli_timeline_numerata` = **138** (da `altTimelineData`, la Timeline numerata) e `titoli_con_voce_atlas` = 49, separati |
| Relazioni mescolate | 1.277 = somma di classi diverse | `relazioni_per_classe`: **narrativa 245, editoriale 1.027, controparte 5, co-apparizione 0** (per regola mai nel registro); narrative per verifica: 207 verificate, 34 da verificare, 4 guida |
Dati dell'esecuzione dell'utente (19 s): 104 film e 39 serie Marvel Studios, 20 serie Marvel Animation (TMDB), 1.197 elementi MCU (Wikidata) — usati solo come ordine di grandezza; nessun metadato TMDB archiviato.

## 2. Pipeline W1 (tutto in repository, riproducibile)
1. **Raccolta** `tools/db_w1_harvest.py` (modalità `db_w1` di «TMDB sync (manuale)», ref `test/tva-archives`): SPARQL leggero per i QID di 4 gruppi (universo MCU P1080; opere MCU via franchise/parte-di; interpreti = cast delle opere MCU; creatori = regia/sceneggiatura/creatori dei personaggi MCU) → `wbgetentities` a blocchi (etichette/alias/descrizioni en+it, sitelink, dichiarazioni). Solo **Wikidata CC0**, User-Agent dichiarato, pause. Scrive **solo sul branch dati `db-raw`** (mai `main`, mai il branch TEST). Nessun Secret.
2. **Costruzione offline** `tools/db_w1_build.py`: classifica per classe P31 → risolve contro le 452 voci storiche → valida (D12) → `canon/w1_mcu.jsonl` (Livello C, verificate), `canon/w1_arricchimenti.jsonl`, `staging/w1_staging.jsonl`, `review/w1_coda.json`, registro ID append-only aggiornato, indice runtime a shard `atlante2/data/db/`.
3. **Regole anti-duplicazione e anti-invenzione**: nome/alias esatto → *arricchimento* della voce storica (ID invariato, aggiunge alias/interpreti, mai riscrittura); corrispondenza parziale/multipla → **coda di revisione e voce trattenuta** (mai importata); omonimi con QID diversi **mai fusi** (ID con suffisso QID); nuova voce → **verificata solo con dichiarazione Wikidata + articolo Wikipedia indipendente** (D12), altrimenti staging; episodi e classi non riconosciute fuori dal runtime; nessun testo narrativo (descrizione breve Wikidata CC0 + campi strutturati); mai co-apparizioni come relazioni.
4. **Categorie coperte**: personaggi, entità cosmiche, organizzazioni, artefatti/armi, luoghi, pianeti, universi/dimensioni, specie, civiltà, eventi, battaglie, **opere** (film/serie MCU), **interpreti**, **creatori**.

## 3. Integrazione con TVA Atlas
- **Ricerca globale**: nuovo modulo lazy `atlante2/db.js` (non caricato né scaricato finché non si cerca); ricerca per alias, nome italiano e originale, nomi parziali/infissi, accenti/maiuscole, interpreti. Gruppo «Archivio esteso» sotto i risultati storici; un alias di una voce storica apre la **scheda storica esistente**.
- **Scheda essenziale (Livello C)** `v:'dbx'`: tipo, nome, nome italiano, descrizione breve, alias, interpreti, continuità (link all'hub/universo esistente), fonti con licenza; dichiara che il dossier approfondito arriverà dopo.
- **Invariati**: ID storici, continuità, ritratti privati, XP, badge, preferiti, raccolte, Multiverso, Nexus (nessuna relazione nuova senza verifica D12: le relazioni narrative restano a W6), Miss Minutes (D14: integrazione dei nuovi dati nell'archivio consultabile rimandata a W7, motore/gateway/interfaccia/quote intoccati). Banner/ID di build: solo `20261128-0100-db1`.
- Scala: indice runtime = trigrammi a 16 shard + chunk da 500 record (prototipo W0: 1,14 MB gz a 50.000 record).

## 4. Verifiche automatiche
`tests/db_w1_test.py` 13/13 (idempotenza ID, nessuna collisione con gli ID storici, omonimi non fusi, solo Livello C verificato, staging/coda corretti, ricerca JS); `tests/db_ui_test.py` 10/10 (lazy, omonimi, scheda, link sicuri, alias→scheda esistente, ricerca storica invariata, nessun overflow, nessun errore JS); `tests/db_test.py` (W0 + W1); regressioni Atlas v. roadmap. Le fixture sono **sintetiche e non finiscono nel runtime**.

## 5. Contenuti aggiunti (raccolta reale eseguita il 27/11 alle 23:55: 1.532 entità Wikidata, 2.319 etichette di riferimento)
Raccolta: universo MCU 1.197 · opere 92 · interpreti 187 · creatori 59 (esito `w1_manifest.json`, tutti i gruppi ok).
| Esito | Quantità |
|---|---|
| **Nuove voci verificate in archivio (Livello C)** | **284**: 162 interpreti, 53 creatori, 39 opere, 23 personaggi, 2 artefatti, 2 battaglie, 2 universi/dimensioni, 1 organizzazione |
| **Arricchimenti di voci storiche** (ID invariati: alias, nomi italiani, interpreti, QID Wikidata) | **109** |
| **Coda di revisione – possibili duplicati** (non importati) | **59** (es. «Tony Stark»↔`id-iron-man`, «Peter Parker» ↔ 4 identità, «Tesseract»/«Eye of Agamotto» ↔ schede italiane) |
| **Coda – classi non riconosciute** (non importate) | **89** (es. «fictional occurrence» 34: fasi/eventi editoriali da valutare) |
| **Staging – una sola fonte (D12)** | **970**: 352 luoghi, 341 personaggi, 146 artefatti, 36 organizzazioni, 21 battaglie, 18 opere, 14 pianeti, 9 specie, 8 universi, 4 entità cosmiche, 11 persone |
| Staging – senza etichetta inglese / episodi | 28 / 3 |
Indice runtime `atlante2/data/db/`: 394 record (284 nuovi + 109 arricchimenti + 1), **33 KB compressi**, 156 KB su disco; ricerca reale ≤ 5 ms (es. «hemsworth»→Thor, «zoe saldana»→Gamora e scheda attrice, «Batista»→Dave Bautista, «guardians», «quantum»).
**Lettura onesta del risultato:** la quota di **personaggi** nuovi verificati è bassa (23) perché la gran parte dei personaggi minori MCU in Wikidata non ha un articolo Wikipedia: per la regola D12 (due fonti indipendenti) resta in staging (341 personaggi, 352 luoghi, 146 artefatti). Non è un limite del sistema ma di fonti: **non ho abbassato la soglia** per gonfiare i numeri. Per promuoverli serve una **seconda fonte indipendente** compatibile con le licenze (proposta W1.b: wiki MCU su Fandom, CC BY-SA 3.0, solo fatti e mai prosa; oppure TMDB solo dopo chiarimento dei termini): decisione tua.
Le 59 possibili duplicazioni sono volutamente non risolte automaticamente (continuità diverse, es. Peter Parker; Hive ≠ Grant Ward): vanno decise caso per caso, non inventate.

## 6. Prossimi passi
1. (Opzionale, tua decisione) **W1.b**: seconda fonte per promuovere lo staging (Fandom MCU, solo fatti, o TMDB dopo verifica dei termini).
2. Revisione della coda (59 duplicati, 89 non classificati): posso proporre decisioni a regole come per i link ambigui di A3.
3. W2 (pre-MCU e paralleli) solo dopo la tua approvazione.
Rigenerazione: il raw (`data/atlante/espansione/raw/`, ignorato da git) si scarica da `db-raw`; `python3 tools/db_w1_build.py <raw> --scrivi` è idempotente (ID stabili).


## Aggiornamento 28/11 – W1.b/W2 (strumenti pronti, raccolta da eseguire)

- **Correzione**: i «49 titoli con voce Atlas» erano in realtà 49 attori (tipo `t`); i titoli numerati della Timeline sono 138 (`altTimelineData.json`).
- **Code risolte a regole** (verifica identità/continuità/alias/ID esterni/interpreti, omonimi mai fusi): possibili duplicati 59 → 3 realmente ambigui (Groot originale/successore; Blade MCU/Blade-verse; Grant Ward/Hive); classi non classificate 89 → 35 (fuori ambito o classe non riconosciuta).
- **Numeri verificati nel codice**: canon 286 (163 attori, 53 creatori, 39 opere, 23 identità, 4 artefatti, 2 universi, 1 battaglia, 1 organizzazione), arricchimenti 153, staging 1.093 (987 a fonte singola), runtime 439 record; registro 1.038 ID, 0 errori.
- **W1.b** (`tools/db_w1b_harvest.py`, `db_wiki_parse.py`): MCU Wiki e Marvel Database via API MediaWiki Fandom (testo CC BY-SA 3.0; solo fatti strutturati con attribuzione e URL, mai prosa; 1,2 s tra richieste; User-Agent dichiarato). marvel.com non usato (termini Disney vietano l'accesso automatico). Livelli B: poteri/abilità/equipaggiamento/debolezze/trasformazioni (nomi). Testato solo su mock/fixture: **contenuti reali = DA RACCOGLIERE**.
- **W2** (`tools/db_w2_harvest.py`, `--onda w2`): Fox X-Men/Deadpool/New Mutants, Raimi, Webb, SSU, Blade, Daredevil/Elektra, Ghost Rider, Hulk 2003, Fantastici Quattro. Test su fixture; contenuti reali da raccogliere.
- **Raccolta**: Actions → «TMDB sync (manuale)» → ref `test/tva-archives` → spunte `db_w1b` e `db_w2` (job `db-w1b` e `db-w2`, scrive solo sul branch `db-raw`).
- **Non fatto / bloccato**: integrazione nei cataloghi nativi di Atlas/Multiverso/Nexus (oggi: ricerca e catalogo «Archivio esteso»); relazioni narrative da Wikidata (P22/P25/P26/P40/P3373/P463 non ancora raccolte); ritratti privati per le nuove identità (la pipeline usa metadati TMDB: termini di archiviazione non chiariti); Comic Vine rimandato; tag `release/atlante-2.0-a70` non pushabile dal proxy.


## Aggiornamento 28/11 04:00 – W1.b e W2 su dati reali

| Voce | Contenuti |
|---|---|
| W1 + W1.b acquisiti e verificati | **1.006** (828 Livello C + **178 Livello B**): 223 personaggi, 363 luoghi, 85 artefatti, 163 interpreti, 53 creatori, 39 opere, 30 organizzazioni, 20 battaglie, 11 pianeti, 10 universi, 8 specie |
| Arricchimenti di voci storiche | 154 |
| W2 pre-MCU/paralleli acquisiti | **592** (457 interpreti, 59 creatori, 45 personaggi, 20 opere, 5 organizzazioni, 4 entità cosmiche, 2 altri) + 103 arricchimenti; 35/36 film |
| Ancora in staging | W1 372 (seconda fonte non coerente/assente), W2 113; coda ambigua: W1 2, W2 16 (personaggi con più continuità: Peter Parker, Sue Storm, Harry Osborn, Lizard…) |
| Registro / runtime | 2.337 ID (0 errori); indice runtime 1.855 record, ~180 KB gz |

Fonti: Wikidata CC0; MCU Wiki e Marvel Database (Fandom, CC BY-SA 3.0) solo parametri brevi di infobox con attribuzione e URL; nessun testo di prosa; marvel.com non usato; nessun nuovo metadato TMDB. Il campo «Apparizioni» riporta i titoli elencati dalla fonte (include media non canonici come LEGO/giochi, indicati dalla fonte).
Limiti noti: le relazioni narrative Wikidata, i ritratti privati delle nuove identità e l'integrazione nei cataloghi nativi (Atlas/Multiverso/Nexus) NON sono ancora fatti; Ghost Rider: Spirit of Vengeance (2011) non risolto su Wikidata.

## Aggiornamento 28/11 08:40 – integrazione nativa, W3/W4, relazioni

| Voce | Contenuti |
|---|---|
| Canon | W1 1.006, W2 605, W3 585, W4 153 (+322 arricchimenti di voci storiche) |
| Staging / code | W3 428 / 8 ambigui; W4 165 / 26 ambigui; W2 114 / 16 ambigui |
| Integrazione | voci native in cataloghi, ricerca, Multiverso (universi db = «luogo narrativo», orbita 3) e Nexus; nessun archivio separato; XP/badge esclusi per le voci db |
| Relazioni narrative | 142 (16 verificate, 126 da verificare), 44 in staging; solo narrative, mai co-apparizioni |
| Registro / runtime | 2.891 ID; 2.671 record, ~289 KB gz |

Non fatto: risoluzione delle code ambigue W2–W4, promozione Livelli A/B, ritratti (termini TMDB da chiarire), W5+.
