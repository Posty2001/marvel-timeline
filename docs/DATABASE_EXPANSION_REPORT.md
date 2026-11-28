> **Correzione 28/11/2026 (utente):** l'obiettivo storico approvato per le relazioni narrative documentate NON era 500 ma **10.000+**; gli obiettivi orientativi della Database Expansion sono: 1.000+ personaggi, 300+ varianti, 200+ artefatti e armi, 100+ universi e dimensioni, 10.000+ relazioni narrative documentate. Sono traguardi orientativi: nessun contenuto va inventato per raggiungerli.

# Database Expansion — Report (db6) (build `20261128-1500-db6`, TEST)

Stato: **consegnata per collaudo; NON dichiarata «completata»** (serve l'approvazione esplicita dell'utente). Solo branch `test/tva-archives`, `main` congelato, 0 €, Tessera TVA 2.0 non avviata, motore/gateway/quote di Miss Minutes non modificati (solo dati letti dal caricatore).

## Conteggi canonici deduplicati (`python3 tools/db_conteggi.py`)
Totale canon **6.255** = 452 storiche + **5.803 nuove** (698 duplicati d'ID scartati, 0 duplicati Wikidata).
| Categoria | Voci | | Categoria | Voci |
|---|---|---|---|---|
| Personaggi/identità | 1.958 | | Interpreti | 979 |
| Organizzazioni | 573 | | Opere/testate | 1.579 |
| Autori/creatori | 458 | | Luoghi | 395 |
| Artefatti | 114 | | Eventi/saghe | 43 |
| Universi | 40 | | Titoli (storici) | 49 |
| Specie | 10 | | Pianeti | 11 |
| Battaglie | 20 | | Entità cosmiche | 21 |
| Hub/mantelli | 5 | | | |
Livelli: A 315 · B 351 · C 5.589. Per ondata (nuove): W1 1.006 · W2 592 · W3 433 · W4 110 · W5 1.208 · W6 431 · **W5c (Comic Vine) 2.023** (241 personaggi secondari, 446 team/organizzazioni, 1.336 testate). Archivio per Miss Minutes: 5.803 schede verificate.

## Cosa è stato fatto in questo blocco
- **Comic Vine** (chiave gratuita nei Secret, ≤1 req/s): raccolti solo ID/nome/conteggi di 3.607 personaggi, 1.133 team, 1.050 saghe, 1.969 testate Marvel (filtro editore lato client). 591 abbinamenti esatti a voci Earth-616 esistenti (`cv_match.json`); nuove voci solo con **seconda fonte indipendente** (pagina omonima su Marvel Database, titolo esatto, non disambigua; D12). Nessun testo copiato.
- **Staging**: 2.467 candidati CV senza seconda fonte restano in `staging/w5_cv_staging.jsonl` (saghe incluse: nessuna pagina omonima verificabile); promozione dello staging Wikidata W5/W6 via CV: 0 corrispondenze esatte. Il resto dello staging W1–W6 resta documentato nelle code (`review/`).
- **Relazioni narrative**: verifica semantica v2 (costrutti relazionali direzionali; la sola co-presenza di due nomi non verifica) applicata: **783 verificate** (da 78), 1.003 da verificare/staging su 1.786. Storiche: 207 verificate su 245.
- **Dossier originali in italiano** (solo da fatti verificati): 298 (da 222).
- **Miss Minutes**: archivio `atlas_db.json` 5.803 schede (testate come «Nome (testata)» per non alterare le risposte sui personaggi); `engine.js`, gateway e quote invariati; test di non regressione Loki ok.
- **Progressione A5**: voci db verificate (B/C) idonee con regole e valori invariati; ricompense mai revocate.
- **Ritratti**: condizioni TMDB non leggibili in modo ufficiale da qui (pagina bloccata); il supporto TMDB indica che la cache è consentita con attribuzione, ma i termini formali non sono confermati → **nessuna immagine nuova acquisita**; resta la pipeline privata (IndexedDB, mai nel repository/ZIP). Nessun ritratto per le nuove voci: decisione aperta.

## Confronto con gli obiettivi storici
| Obiettivo storico | Esito |
|---|---|
| 452 voci storiche invariate, ID immutabili | rispettato (test `db_test`) |
| 10.000+ relazioni narrative documentate (corretto: non 500) | 990 verificate (207 storiche + 783 db) su 2.031 narrative censite: obiettivo lontano, vedi report W8 |
| Copertura MCU, pre-MCU, TV, animazione, fumetti, creatori | W1–W6 eseguite; Comics Library futura resta distinta |
| Livello A | 315 (invariato: solo voci storiche; nuove voci non promosse ad A senza dossier editoriale) |
| Miss Minutes (D14) | integrato come dati (W7 minimo); nessuna riprogettazione |

## Limiti e aperti
Relazioni «da verificare» 1.003; 2.467 candidati CV in staging; saghe CV non abbinabili; ritratti nuove voci; Livello A per le nuove voci; Safari iOS/iPad reali da collaudare. Test automatici essenziali superati: db_test 18, db_w5 12, db_harvest 30, db_relverify 10, db_w1 30, a5 46, atlas_db 6, engine 42, UI db/a3 32/a5 17/a41/a7 110, a40.
