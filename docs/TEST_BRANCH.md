# Branch `test/tva-archives` — versione TEST

- **Base:** `main` = `82a73c7` (produzione, build `20261112-1905-rifinitura`, congelata). `main` non è modificato.
- **Build TEST:** `20261120-2000-episodes2` (build precedente: `20261117-1900-arcade-draft31r`).
- **Pubblicazione:** il branch NON è pubblicato né su GitHub Pages né su Netlify; il TEST si carica a mano su Netlify.

## Differenze rispetto alla produzione
| File | Differenza |
|---|---|
| `arcade/**` (nuovo, 367 file) | TVA Arcade: hub e 5 giochi (Quiz Marvel, Who Am I?, Time Crisis, Secret Wars Draft 3.1 con 120 carte e 120 ritratti di test, Multiverse Escape) |
| `index.html` | ID build; Home: carta «TVA Arcade» al posto di «Quiz Marvel»; rimossi dalla Home i due pulsanti «Atlante» e «Tessera TVA» (restano nella barra inferiore); evento additivo `tva-identity-changed`; `f3Slot()` (predisposizione Friends 3.0) |
| `quiz/index.html` | ID build; timer domanda 20 s → 30 s; ritorno a TVA Arcade se aperto con `?from=arcade` |
| `sw.js` | ID build/cache; precache Arcade (pagine, script condivisi, manifest e 120 ritratti) |
| `tools/arcade/`, `tests/arcade/`, `docs/arcade/` (nuovi) | Sorgenti del Draft, bilanciamento/simulazioni, validatore ritratti, test attuali, report e cataloghi |
| `index.html` (TVA Episodes) | Pannello «Episodi e voti» nelle schede serie; chiave `marvel-ultimate-timeline-episodes-v1` (campo `episodes` in backup/sync); media episodi in Timeline al posto del voto originale (che resta salvato). |
| `assets/episodes/`, `tools/tmdb_episodes.py`, `.github/workflows/tmdb-sync.yml` (esteso) | Catalogo episodi TMDB in JSON separati (`index.json` + `<tmdbId>.json`), generatore (token solo da ambiente) e workflow manuale che produce un artifact. |
| `tests/episodes/ep_test.py` | Test mirati TVA Episodes (`python3 tests/episodes/ep_test.py`). |
| `arcade/**/index.html`, `quiz/index.html`, `sw.js` | Solo ID build (stesso valore di `index.html`, richiesto dalla cache offline). |

Invariati: Rankings, Friends 2.0, Tessera 3.0, Atlante, Timeline, dati, Firebase, workflow TMDB.

## Note
- I ritratti del Draft sono asset stilizzati di test (`status: test_stylized`), non ritratti Marvel definitivi né diritti confermati.
- `docs/arcade/PATCH_disclaimer_DA_APPLICARE_DOPO_COLLAUDO.diff` è preparata e NON applicata.
- I test in `tests/arcade/` usano un server locale sulla cartella del progetto (porta 8790 negli script).

## TVA Episodes — dati
`assets/episodes/` contiene il catalogo reale TMDB (artifact «TMDB sync» #5): 46 schede serie con dati, 488 episodi principali + 2 speciali (WandaVision). 137 (Daredevil: Born Again S3) e 138 (X-Men '97 S3) sono «in attesa» (stagione non ancora su TMDB, nessun dato inventato). 073 The Defenders NON ha ancora dati: ID corretto 62285 in `tmdb_overrides.json`; rilanciare il workflow «TMDB sync (manuale)» con `solo_episodi` e copiare `episodes/` in `assets/episodes/`. Episodi con data futura: «In arrivo», non votabili. Attribuzione: sezione Credits + pannello episodi; il logo ufficiale va messo (non modificato) in `assets/images/tmdb-logo.svg`: finche' manca, resta il testo con link. Verifica: `python3 tests/episodes/data_test.py` e `ep_test.py`.
