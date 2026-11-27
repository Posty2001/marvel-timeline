# Database Expansion – W0 «Architettura e censimento» (27/11/2026) — REPORT

Stato: **W0 eseguita (parte eseguibile in sandbox); NON dichiarata completata** (serve l'approvazione dell'utente). Branch `test/tva-archives`, produzione congelata, 0 €. Runtime a70 / Miss Minutes **non modificati** (verificato da `tests/db_test.py`).

## 1. Consegnato
| Elemento | File | Verifica |
|---|---|---|
| Registro ID append-only (751 ID: 452 voci + pagine storiche + redirect; lapidi con redirect, mai riuso) | `data/atlante/espansione/ids_registro.json`, `tools/db_ids.py --scrivi/--verifica` | 0 errori |
| Schema canonico v1 (tipi, livelli A/B/C, stato verifica D12, ID esterni forti, fonti con licenza) | `data/atlante/espansione/schema/record_canonico.schema.json` | usato dal validatore |
| Import sottile dei 452 record storici (nessun dato nuovo, ID invariati) | `data/atlante/espansione/canon/storico.jsonl`, `tools/db_canon.py` | 452/452, 0 errori |
| Prototipo indice a shard + ricerca globale (alias, nomi it/originali, infix, accenti) – **fuori dal runtime** | `tools/db_proto/` | v. §3 |
| Censimento (interno subito; esterno solo con rete) | `tools/db_censimento.py`, `.github/workflows/db-censimento.yml` (solo `workflow_dispatch`, sola lettura) | interno eseguito |
| Test automatici | `tests/db_test.py` | 14/14 + verificatori Atlas invariati |

## 2. Conteggi reali (interni, verificati nel codice)
452 voci d'indice: 315 identità, 27 universi, 49 titoli, 17 organizzazioni, 16 artefatti, 9 luoghi, 7 pianeti, 7 eventi, 3 hub, 2 mantelli. 42 identità con alias, 38 con interpreti; 1.277 voci nel registro relazioni (non confrontabili con l'obiettivo 10.000 «documentate»: molte sono in verifica). **Distanza dagli obiettivi storici** (orientativi, D9): personaggi 315/1.000+, artefatti 16/200+, universi 27/100+, relazioni narrative documentate ≈246 (206 verificate)/10.000+. Varianti: da censire in W2.
**Conteggi esterni: NON ottenibili dalla sandbox** (nessuna rete verso Wikidata/TMDB/Comic Vine). Ordini di grandezza pubblici (non verificati): wiki MCU ≈43.000 articoli; Marvel ≈7.000 personaggi dichiarati nel 2017. Vanno misurati con il workflow `DB Expansion - censimento` (azione richiesta, v. §6).

## 3. Scalabilità (prototipo, dati sintetici deterministici)
| N record | indice gz totale | byte scaricati in 10 query | latenza max | RSS Node |
|---|---|---|---|---|
| 20.000 | 0,48 MB | 300 KB | 59 ms | 63 MB |
| 50.000 | 1,14 MB | 716 KB | 107 ms | 80 MB |
Design: nomi in chunk da 1.000, posting dei trigrammi in 64 shard (delta-encoding), indice prefissi per query <3 caratteri; si scaricano solo gli shard necessari (lazy, cacheabili dal service worker). Ricerca corretta su alias, infix, maiuscole, accenti, frasi multi-parola. **Limiti noti**: ranking semplice (esatto>prefisso>parola>infix); nessuna tolleranza a errori di battitura; sinonimi italiano/originale dipendono dagli alias raccolti in W1+. Verdetto: architettura sostenibile fino ad almeno 50.000 record senza backend. Da rimisurare su iPhone reale nell'ondata che la integra (non in W0).

## 4. Licenze, attribuzioni, limiti (verificati con fonti ufficiali dove leggibili)
- **GitHub Actions**: runner standard gratuiti e senza limite di minuti per repository **pubblici** (il repo è pubblico). Nessun costo; se il repo diventasse privato i limiti cambierebbero → da non fare.
- **Wikidata**: dati strutturati CC0, uso consentito con User-Agent dichiarato e rispetto della policy sui robot. **Fonte principale di ID forti, alias multilingua, etichette italiane.**
- **TMDB**: gratuito non commerciale con attribuzione; le condizioni di **archiviazione/ridistribuzione NON sono state verificate** (pagina dei termini API non leggibile dagli strumenti: robots). Fino a verifica dell'utente: uso già in essere (titoli/cast), nessuna estensione a nuovi dati redistribuiti.
- **Comic Vine (D7)**: ToS non commerciali, 200 richieste/risorsa/ora, link obbligatorio, vietato «editare, manipolare o riprodurre su altro medium», no CORS (solo lato server), chiave unica per sito. **Raccomandazione: usare Comic Vine SOLO come fonte di consultazione/ID per il censimento e per guidare i link, senza copiarne il testo nel nostro archivio**; i dossier restano originali (D8). Decisione finale all'utente (v. §6).
- **Grand Comics Database**: CC BY-SA 4.0 (attribuzione + condivisione allo stesso modo), dump previo account gratuito: adatto ai metadati editoriali (testate, numeri, crediti) in W5–W6 con attribuzione.
- **Wiki Fandom/Marvel Database**: testo CC BY-SA 3.0 → si usano solo fatti, mai prosa copiata (D8, D12).
- **Immagini**: invariato (private, IndexedDB, mai nel repo; D13).

## 5. Piano operativo delle ondate (sintesi; nessuna avviata)
| Ondata | Contenuto | Fonti | Uscita verificabile |
|---|---|---|---|
| W1 MCU | personaggi, artefatti, luoghi, organizzazioni, specie, eventi MCU + attori/creatori collegati | Wikidata, TMDB, dati interni | canon MCU, delta ID, test dedup |
| W2 Pre-MCU e paralleli | film Fox/Sony/Raimi/… varianti | Wikidata, TMDB | varianti ≠ identità distinte |
| W3 TV non MCU | Netflix/ABC/Hulu/Freeform | idem | continuità separate |
| W4 Animazione | serie/film animati | idem | idem |
| W5 Fumetti A + struttura | testate, personaggi fondamentali (D3), universi/Terre | Wikidata, GCD, Comic Vine (consultazione) | Livello A fondamentali |
| W6 Fumetti B + relazioni | secondari/minori, relazioni narrative | + verifica D12 | relazioni verificate |
| W7 Consolidamento | indice di produzione, ricerca globale, ritratti, archivio Miss Minutes (D14) | — | build candidata |
Regola comune: Discover→Harvest→Normalize→Resolve→Enrich→Validate→Review queue→Promote&Build; nessuna fusione automatica di persone distinte; non risolto → staging (D12). Ogni ondata chiude con report a blocchi e conteggi reali; **le quantità storiche sono traguardi indicativi** (D9).

## 6. Azioni richieste all'utente (solo se vuole procedere)
1. **Avviare una volta** il workflow GitHub «DB Expansion - censimento» (Actions → Run workflow, branch `test/tva-archives`): produce l'artifact `db-censimento` con i conteggi esterni reali (Wikidata, TMDB; Comic Vine se la chiave c'è). Poi inviarmi il JSON.
2. **Comic Vine**: registrarsi gratuitamente su comicvine.gamespot.com (API key personale) e inserirla come Secret `COMICVINE_API_KEY` nel repo (Settings → Secrets and variables → Actions → New repository secret). **Non incollarla in chat.** Ti guiderò passo passo quando vuoi. Prima: confermare la modalità «consultazione/ID, nessuna copia del testo» (§4).
3. **TMDB**: leggere i termini API sulla conservazione dei dati e dirmi se la storicizzazione dei metadati nel nostro archivio è consentita.
4. **Tag `release/atlante-2.0-a70`**: il push resta bloccato dal proxy dell'ambiente (due tentativi + via REST: 403), non forzato. Il tag esiste solo in locale; per pubblicarlo: `git push origin release/atlante-2.0-a70` da una macchina con accesso diretto.

## 7. Problemi aperti / limiti
Conteggi esterni non ottenuti (rete assente); termini TMDB non verificati; GCD richiede account; N°077 e N°125 (D10) e Johnny Storm N°117 (D11) vanno trattati in W1/W2; il prototipo di ricerca non è integrato nell'app per scelta (W7).
