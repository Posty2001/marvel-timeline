# DATABASE EXPANSION — Chiusura definitiva (W9, build `20261128-2330-db9`, TEST)

Stato: **CONGELATA su decisione dell'utente (28/11/2026)**; build in attesa di approvazione. Nessun ulteriore ciclo di espansione. Tessera TVA 2.0 NON avviata (si attende l'approvazione). Produzione congelata, solo TEST, 0 €.
Engine, gateway, quote e verificatore di Miss Minutes e regole XP: invariati (unica modifica a `a5.js`: `eligible()` esclude le voci «fonte singola»).

## 1. Decisione D12 — deroga controllata (tre stati)
*Precisazione dell'utente (28/11, dopo l'approvazione): resta valido anche il criterio della singola fonte primaria inequivocabile per la verifica; la deroga riguarda le singole fonti secondarie attendibili.*

| Stato | Significato | Progressione/XP | Dove |
|---|---|---|---|
| **Verificata** | almeno 2 fonti indipendenti (regola D12) | sì (regole invariate) | canon |
| **Documentata da una singola fonte** | una fonte attendibile (Marvel Database) con identità base, universo e continuità documentati | **mai** XP, esplorazioni o completamenti | canon (`w9_deroga.jsonl`), etichetta visibile nella scheda e in Miss Minutes |
| **Da verificare** | casi ambigui o con documentazione insufficiente | no | solo staging |

Criteri per la promozione di una variante a «fonte singola» (tutti obbligatori): identità base verificata e di Livello A/B; nome «Base (Earth-N)» coerente con la base; la continuità Earth-N ha una pagina propria **e** pagine di almeno 5 identità distinte; l'universo è diverso da quello della base; nessun omonimo già presente; tetto prudenziale di 12 varianti per identità base. Stessa logica per gli universi: solo le continuità Earth-N citate dalle varianti promosse.
Risultato: **171 varianti** e **34 universi** documentati da fonte singola; **2.520 varianti** e **4.088 universi** restano in staging «da-verificare» (nessuna promozione indiscriminata).

## 2. Classificazione (stesse schede, ID invariati)
- Schede duplicate fuse in una sola (ID `cos-doctor-doom`, `cos-hogun`, `cos-surtur` ritirati come **lapide con redirect** verso `id-doctor-doom`, `id-hogun`, `id-surtur`; 21 relazioni riportate sulla scheda unica).
- 34 voci già classificate «entità cosmica» ora sono identità (tra cui **Mephisto**, Blackheart, Demon Bear, Sif, Typhon); Knowhere è un luogo; restano entità cosmiche solo le 22 con evidenza nei fatti (Celestials, Proemial Gods, Abraxas, Origin…).
- Il campo `categorie` consente categorie multiple (personaggio, demone, divinità, entità cosmica) sulla **stessa** scheda: nessun ID o progressione duplicati.

## 3. Conteggi canonici finali (`python3 tools/db_conteggi.py`)
Voci deduplicate: **6.793** (6.801 ID registrati nei canon, 8 duplicati per QID scartati). Per stato: verificate 6.588, documentate da fonte singola 205.
Per livello: A 449, B 469, C 5.875.

| Categoria | Totale | di cui fonte singola |
|---|---|---|
| Identità (personaggi) | 1.976 | 0 |
| Varianti | 171 | 171 |
| Universi e dimensioni | 77 | 34 |
| Entità cosmiche | 22 | 0 |
| Artefatti e armi | 392 | 0 |
| Specie e civiltà | 29 | 0 |
| Eventi e saghe | 57 | 0 |
| Organizzazioni / Luoghi | 573 / 395 | 0 |
| Pianeti / Battaglie | 11 / 20 | 0 |
| Opere / Attori / Creatori | 1.579 / 979 / 458 | 0 |
| Titoli / Hub / Mantelli | 49 / 3 / 2 | 0 |

Conteggi separati: personaggi 1.976; identità 1.976; varianti verificate 0, documentate da fonte singola 171 (+4 storiche marcate, 2.520 in staging); incarnazioni 7 (3 identità); mantelli 2; hub 3.
Relazioni narrative **documentate**: 8.372 (8.127 database + 245 storiche), di cui **verificate 993** (786 + 207), tenute separate; editoriali e co-apparizioni escluse.

## 4. Obiettivi storici — conservati come obiettivi di espansione futura
| Obiettivo | Attuale | Esito |
|---|---|---|
| 1.000+ personaggi | 1.976 | raggiunto |
| 200+ artefatti e armi | 392 | raggiunto |
| 300+ varianti | 171 documentate (0 verificate) | non raggiunto: obiettivo futuro |
| 100+ universi e dimensioni | 77 (43 verificati + 34 fonte singola) | non raggiunto: obiettivo futuro |
| 10.000+ relazioni narrative documentate | 8.372 (993 verificate) | non raggiunto: obiettivo futuro |

## 5. Ritratti
Pipeline privata mantenuta (import da file, archivio IndexedDB locale, export/import); 516 candidati conservati (solo metadati). Limite: i termini di archiviazione TMDB non sono confermati, quindi nessuna immagine viene acquisita o distribuita automaticamente.

## 6. Controlli automatici eseguiti (essenziali)
db_integrazione 24/24 (include: tre stati, nessun XP a fonte singola, Doom/Mephisto, lapidi, Miss Minutes invariata), db_test 18, db_w8 18, db_w1 30, db_w5 12, db_harvest 30, db_relverify 10, a5 46, atlas_db (Miss Minutes) 6, engine 42, db_ui, a3 32/32, a5_ui 17/17.

## 7. Sistema incrementale (mantenuto, non eseguito oltre questa chiusura)
`python3 tools/db_ricostruisci.py`; per riprendere l'espansione in futuro vedere `docs/DATABASE_EXPANSION_INCREMENTALE.md`. La deroga è riproducibile con `python3 tools/db_w9_chiusura.py [--scrivi]` (parametri `SOGLIA_UNI` e `TETTO_BASE`).

## 8. Attività residue (solo obiettivi futuri, nessuna obbligatoria)
Seconda fonte per varianti/universi in staging; verifica documentale di altre relazioni (7.341 da verificare); rilancio `db-w5c` per 305 personaggi di relazioni Comic Vine; ritratti nuove identità; collaudo reale iPhone/iPad.
