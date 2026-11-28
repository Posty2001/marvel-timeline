# Database Expansion – Consolidamento W1–W4 e ondate W5/W6 (fumetti) – 28/11/2026, build `20261128-1100-db5`

Stato: **in attesa di approvazione. Non dichiarata completata.** TEST (`test/tva-archives`), produzione congelata, 0 €.

## Conteggi canonici (deduplicati per ID e per QID; `python3 tools/db_conteggi.py`)
- **Voci canoniche totali: 4.232** (452 storiche + **3.780 nuove**; 698 righe duplicate tra ondate scartate: lo stesso elemento può comparire in più ondate).
- Per livello: A 315 (storiche), B 351, C 3.566.
- Nuove per ondata (righe di canon, prima della deduplica tra ondate): W1 1.006 · W2 592 · W3 433 · W4 110 · **W5 1.208 · W6 431**.
- Categorie (totale canonico): identità 1.717, luoghi 395, creatori 458, interpreti 979, opere 243, organizzazioni 127, artefatti 114, eventi/saghe 43, universi 40, entità cosmiche 21, battaglie 20, pianeti 11, specie 10.
- Il runtime (`atlante2/data/db/`) contiene ora 4.134 record deduplicati (stub caricato progressivamente; ~518 KB gz in totale, schede a richiesta).

## Consolidamento W1–W4
- Titoli mancanti recuperati (tolleranza ±1 anno su etichetta esatta + titolo «Marvel's Spider-Man»): W3 28→29/29 e W4 36→40/40; Ghost Rider: Spirit of Vengeance già in W2.
- Code ambigue risolte a regole (`tools/db_code_risolvi.py`, esiti in `review/risoluzioni_code.json`): C1 collegamento al personaggio-base (36, ID esterno alternativo, nessuna fusione); C2 concetto multi-continuità (7: Groot, Invisible Woman, Green Goblin, Harry/Norman Osborn, Thaddeus Ross, Peter Parker, Wolverine → mai attribuiti a una sola incarnazione); C3 nome non corrispondente (4, rinviate ai fumetti). Nessuna decisione controversa per l'utente.
- W3/W4 ricostruite con la seconda fonte (MCU Wiki): W3 867→433 voci nuove dopo la deduplica, W4 207→110.
- **Relazioni narrative**: 1.786 (Wikidata + «parenti» delle infobox); **1.412 verificate** con seconda fonte indipendente (articolo Wikipedia, stessa frase: nome dell'altro estremo + termine del tipo di relazione; si conserva solo esito e URL) e 374 «da verificare»; 344 in staging (continuità diverse / estremi non coerenti). Co-apparizioni e collegamenti editoriali esclusi (storiche: 245 narrative, 207 verificate, 1.027 editoriali escluse).
- Livelli A/B: i B passano a 351 (la definizione di B non è stata modificata). **Livello A** (dossier con testi originali in italiano) non si genera automaticamente: richiede testi scritti, quindi resta una decisione/lavoro dedicato (v. «Aperto»).

## Progressione (decisione utente 28/11)
Le voci db verificate (canon Livello B/C) partecipano a XP, badge e completamenti con le regole A5 invariate (+2 dossier, +15 hub, +25 universo, +5, +5, +40, tetto 30/giorno); esclusi staging, alias, duplicati e segnaposto. Le ricompense già ottenute non vengono mai revocate (registro permanente). La scheda db usa lo stesso tracker del dossier (tempo, scorrimento, sezione). Test: `tests/a5_test.js` (46), `tests/a5_ui_test.py`.

## W5 / W6 – Universo dei fumetti
Fonte: Wikidata (CC0), criterio di rilevanza oggettivo = ≥3 collegamenti Wikipedia (fasce di rilevanza), universi Marvel (P1080) + presenza in opere Marvel Comics (P1441/P674); Marvel Database (Fandom, CC BY-SA 3.0, solo fatti, attribuzione) come seconda fonte per Earth-616. Nessun testo copiato.
- **W5** entità narrative: personaggi (incarnazioni Earth-616 **distinte** dalle identità MCU/Fox/Raimi: nome disambiguato «(Earth-616)», nessuna fusione), squadre, specie, luoghi, oggetti, entità cosmiche, universi. Nuovo universo `uni-earth-616`.
- **W6** opere e persone: testate, miniserie, saghe/eventi, graphic novel; creatori (autori, disegnatori, creatori di personaggi).
- Apparizioni classificate: continuità narrativa / universi alternativi / fumetti / videogiochi / LEGO-parodie-adattamenti.
- Workflow (da `gh`): `db_w5`, `db_w6`, `db_w5b` (Marvel Database), `db_w5c` (Comic Vine, richiede chiave), `db_relv` (verifica relazioni). Tutti indipendenti, riprendibili, solo branch `db-raw`.
- Test: `tests/db_w5_test.py`, `tests/db_harvest_test.py`, `tests/db_w1_test.py`, `tests/db_test.py`, `tests/db_ui_test.py`, a3/a40/a41/a5/a7.

## Comic Vine (opzionale, gratuita) – guida
La raccolta già eseguita NON richiede Comic Vine. La chiave serve per ordinare per **numero di albi** i personaggi minori e per testate/saghe/creatori: `tools/db_w5c_comicvine.py` conserva solo ID, nomi e numeri.
1. Registrati (gratis) su comicvine.gamespot.com → account → pagina **API** (comicvine.gamespot.com/api) → copia la tua *API key* (nessuna fatturazione, solo uso non commerciale).
2. Su GitHub: repository `marvel-timeline` → Settings → Secrets and variables → Actions → New repository secret → nome `COMICVINE_API_KEY`, valore = la chiave.
3. Dimmi «chiave inserita»: lancio io il workflow (`db_w5c`).

## Aperto
Livello A dei personaggi fondamentali (testi originali), personaggi secondari oltre la soglia di rilevanza (Comic Vine / categorie Marvel Database), 374 relazioni da verificare, ritratti (termini TMDB da chiarire), Comics Library (fase separata), integrazione Miss Minutes (W7), 6 dei 49 elementi in staging W5 e coda ambigua W5 (2).
