# Miss Minutes 2.0 — copertura dell'archivio TMDB (v2, rigenerato il 27/11/2026, commit `7ea1d4b`)

Verifica: `python3 tools/mm_tmdb.py --verifica` → OK 136 voci; `--copertura` (conteggi verificati nel file, non storici).

| Misura | Valore |
|---|---|
| Titoli della Timeline | 138 |
| Voci nell'archivio | **136** (film 86, serie 50) → copertura 98,6 per cento |
| Sinossi italiana | 136/136 |
| Cast | 132/136 (senza cast: N°126 Eyes of Wakanda, N°130/131/138 X-Men '97 — TMDB non lo restituisce) |
| Regia (film) | 86/86 |
| Date di uscita IT (film) | 79/86; US 86/86 |
| Voci con dati di stagione | 32 (con sinossi di stagione: 23) |
| Origine dell'associazione | mappa 124 · override verificati dall'utente 10 · automatiche 2 |

**Film senza data italiana (7):** N°027 Beyond the Spider-Verse (in produzione), N°139 Secret Wars (pianificato), N°028 The Fantastic Four (1994, mai distribuito), N°042/046/048/052 «Irripetibili Marvel» (cortometraggi senza uscita TMDB). Sono assenze reali, non errori: Miss Minutes le dichiara come «dato non disponibile».

**Titoli ancora senza voce (2) — nessuna associazione inventata**
- **N°077 Team Thor / Team Darryl shorts:** un solo candidato (TMDB 413279 «Team Thor: Parte 1»), ma il titolo copre più cortometraggi → classificato *ambiguo*. Serve la tua decisione (override in `assets/images/catalog/tmdb_overrides.json`).
- **N°125 Fantastic Four: First Steps:** la ricerca stretta (titolo+anno) non trova candidati: il titolo italiano su TMDB è diverso. L'ID non è stato verificato (nessun accesso a TMDB da questa sandbox), quindi non lo indovino: se mi indichi l'ID TMDB (o lo metti tu in `tmdb_overrides.json`) lo applico.

**Associazioni automatiche da confermare (2):** N°107 Guardiani della Galassia: Holiday Special, N°115 I Am Groot. Regola: titolo normalizzato identico + anno identico + candidato unico; per confermarle copiale in `tmdb_overrides.json`.

**Override dell'utente applicati (10):** N°036, N°073, N°074, N°086, N°096, N°114, N°119, N°122, N°128, N°137.

**Serie / stagioni / speciali:** le voci TV portano `serie{prima,ultima,n_stagioni}` e, se la Timeline indica una stagione, `stagione{n,nome,sinossi_it,data,episodi,cast}`; Miss Minutes dichiara se un dato è «della serie» o «della stagione N» e non presenta la data della serie come data della stagione.

**Spider-Man: Brand New Day (N°132):** film (regia Destin Daniel Cretton, stato Released, uscita IT/DE/ES/FR/GB 29/07/2026, US 31/07/2026); il fumetto omonimo del 2008 resta distinto dal verificatore (formato/esistenza) e dai fatti dell'archivio.
