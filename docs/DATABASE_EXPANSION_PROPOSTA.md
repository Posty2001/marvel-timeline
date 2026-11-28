# Database Expansion — Proposta operativa (da approvare, NON avviata)

> **Correzione 28/11/2026 (utente):** l'obiettivo storico approvato per le relazioni narrative documentate NON era 500 ma **10.000+**; gli obiettivi orientativi della Database Expansion sono: 1.000+ personaggi, 300+ varianti, 200+ artefatti e armi, 100+ universi e dimensioni, 10.000+ relazioni narrative documentate. Sono traguardi orientativi: nessun contenuto va inventato per raggiungerli.

Data: 27/11/2026 · Base: build a70 congelata · Complemento di `docs/DATABASE_EXPANSION_PREPARAZIONE.md` (stato verificato, fonti, vincoli).
Obiettivo: archivio Marvel estremamente completo (MCU, universi cinematografici precedenti, serie TV, animazione, fumetti), **tutte** le categorie dell'Atlante, scalabile, documentato, automatizzabile, a costo zero, senza duplicati né dati inventati.

---

## 1. Principi non negoziabili
1. **ID immutabili.** Nessun ID esistente cambia, sparisce o cambia significato; le fusioni si fanno solo con redirect (tombstone), mai distruttive.
2. **Nessun dato inventato.** Ogni fatto ha provenienza (fonte, data di consultazione, licenza). Un fatto senza fonte non entra. Niente testi generati da modelli linguistici come «fatti».
3. **Nessuna unificazione di persone distinte** (regola A2): varianti per continuità = identità separate + hub.
4. **Co-apparizioni ≠ relazioni narrative** (regola A4); «da verificare» mai presentata come verificata.
5. **Dati personali intatti**: ritratti privati, progressione, XP, preferiti, raccolte, Tessera, Friends non vengono letti né scritti dalla pipeline.
6. **0 €**, solo servizi gratuiti, chiavi solo nei Secret, nessuna API a pagamento.
7. **Solo TEST**; produzione congelata; pubblicazione/deploy solo dall'utente.
8. **Il pubblicato è sempre verificato dai test**: nulla va nello ZIP se un controllo automatico fallisce.

## 2. Cosa copre il perimetro (matrice categorie × ambito)
| Categoria | Oggi | Dopo l'espansione (proposta) |
|---|---|---|
| Personaggi/identità | 315 | tutte le identità con almeno un'apparizione in un'opera adattata (film, TV, animazione) in ogni continuity; **Livello B** (solo fumetto) a profondità ridotta (§6) |
| Attori/interpreti | 49 | tutti gli interpreti e doppiatori delle identità incluse (fonte TMDB), con legame identità↔interprete↔opera |
| Universi/continuity | 27 | tutte le continuity cinematografiche, TV, animate e fumettistiche rilevanti (es. Terra-616, Ultimate, 2099, MC2, Marvel Zombies, ecc.) con classificazione già in uso |
| Organizzazioni | 17 | team, agenzie, gruppi criminali, governi, aziende ricorrenti |
| Artefatti | 16 | oggetti/armi/tecnologie ricorrenti |
| Luoghi / Pianeti | 9 / 7 | luoghi e mondi ricorrenti |
| Eventi / Battaglie | 3 / 4 | eventi e saghe (opere e fumetti), battaglie principali |
| **Opere** (NUOVA) | — | film, serie, stagioni, speciali, cortometraggi, serie animate, episodi (livello catalogo, **senza N°**): è il ponte con TMDB |
| **Fumetti** (NUOVA) | — | testate/volumi, saghe/archi, albi chiave (prime apparizioni, eventi), creatori |
| Creatori (opzionale) | — | autori/disegnatori collegati ai fumetti (decisione D2) |

Le categorie nuove (Opere, Fumetti, Creatori) richiedono dossier, emblema e schema: vanno approvate (D1–D2). **I 138 titoli numerati della Timeline non cambiano** (D4).

## 3. Modello dati: tre strati
```
FONTI (grezzo)  →  STAGING (normalizzato + provenienza)  →  CANONICO (verificato)  →  RUNTIME (shard generati)
 cache esterna        data/atlante/espansione/staging/        data/atlante/espansione/canon/       atlante2/data/…
```
### 3.1 Sorgente canonica (nuova)
`data/atlante/espansione/canon/<tipo>/<lettera>.jsonl` — un record per riga, ordinato per ID (diff leggibili in Git). Il registro attuale (estratto da `index.html`) resta **sorgente storica sola lettura**: le sue 452 voci sono importate una volta come «canon» *senza cambiare un ID*, poi le nuove voci vivono solo nel canonico.
Record (schema proposto, versione 1):
- `id` (immutabile), `tipo`, `nome`, `nomi_alt[]`, `universo` (ID), `stato` ∈ `proposta | verificata | da_verificare | editoriale | sospesa | respinta`
- `ext` = identificatori esterni: `tmdb`, `wikidata` (QID), `comicvine`, `gcd`, `fandom` (titolo pagina)
- `fatti[]`: `{campo, valore, fonti:[{id, url, data, licenza}], livello}` — **provenienza per campo**
- `legami[]`: `{tipo, a, b, classe(n|c|e), fonti[], verifica}` (stesso schema del Nexus)
- `versione`, `aggiornato`, `nota_editoriale`
### 3.2 Registro ID append-only
`ids_registro.json`: ogni ID mai assegnato, tipo, data, stato, `sostituito_da` (redirect). Test: nessun ID sparisce; `ids_sha256` della baseline A0 resta valido per i 452 storici.
### 3.3 Politica ID per le nuove voci
`<prefisso>-<slug-ascii>` con suffisso di continuity per omonimi (`id-<nome>-<universo>`), come nelle identità esistenti; slug deterministico, collisioni risolte con suffisso numerico mai riassegnato; ID mai derivati da fonti esterne mutabili.

## 4. Deduplicazione e risoluzione identità
1. **Chiavi forti**: ID esterni (Wikidata QID, TMDB, Comic Vine, GCD) — se due record hanno lo stesso ID forte → candidati stesso soggetto.
2. **Chiavi deboli**: nome normalizzato + continuity + interprete + prima apparizione → solo *proposte*.
3. **Nessuna fusione automatica tra persone/varianti**: ogni coppia dubbia va in **coda di revisione** con le evidenze; si fonde solo con redirect (tombstone) e dopo regola approvata (come R1–R5 del ciclo link ambigui).
4. Gli omonimi diventano **hub** (modello esistente) quando ≥2 identità effettive.
5. Test automatici: nessun nome+universo duplicato, nessun alias condiviso senza hub, nessun ID doppio, nessuna identità orfana.

## 5. Fonti e gerarchia (tutte gratuite; v. Preparazione §3)
`Ufficiale/opera stessa > TMDB (opere, cast) > GCD + Comic Vine (fumetti) > Wikidata (identificatori e date strutturate) > Wikipedia/Fandom (solo verifica incrociata, fatti non prosa) > nessun altro`.
- Un fatto è **verificato** se confermato da ≥2 fonti indipendenti o da una fonte ufficiale; con una sola fonte secondaria → **da verificare** (stessa semantica di `verifica 0/1/2` già in uso); in conflitto → coda di revisione, mai scelta silenziosa.
- **Testi italiani**: generati da modelli di frase deterministici sui campi strutturati (es. «Interpretato da X in Y»); nessuna prosa copiata (CC BY-SA); riassunti liberi solo su approvazione (D8). Nessun dato personale va a servizi AI online.
- **Attribuzioni**: sezione «Crediti/Fonti» con TMDB (logo e dicitura richiesti), Comic Vine (link), GCD e wiki CC BY-SA (attribuzione + licenza). Da implementare prima di mostrare dati di quelle fonti.
- **Immagini**: invariato — nessuna nel repository; ritratti sempre privati sul dispositivo.

## 6. Profondità per livello (per evitare un'esplosione di dati)
- **Livello A** (adattato in film/TV/animazione): dossier completo — identità, interpreti, apparizioni per opera, incarnazioni, relazioni narrative documentate, fonti.
- **Livello B** (solo fumetto): scheda ridotta — nome, continuity, prima apparizione, creatori, affiliazioni, link a testate; **no** relazioni narrative finché non verificate; condizione di ingresso da decidere (D3): es. adattamento esistente, o soglia di apparizioni/rilevanza misurata dal censimento.
- **Livello C** (minore/occasionale): indice solo-ricerca, non catalogo (opzionale).
Il censimento W0 misura quante voci cadono in ogni livello prima di fissare obiettivi: **nessuna stima numerica è inventata in questo piano**.

## 7. Scalabilità sull'iPhone/iPad
Misura attuale: 99 KB (19 KB gzip) per 452 voci (~220 B/voce). L'indice monolitico non scala a decine di migliaia di voci. Architettura proposta:
- **Indice a livelli**: `index-core.json` (solo A: id, nome, tipo, universo) + indici per tipo/lettera caricati su richiesta; ricerca per **prefisso** con indice a trie/liste ordinate in shard (nessun download completo).
- **Shard dossier** per tipo e intervallo ID (come oggi, 24/shard → blocchi dimensionati a byte, es. ≤ 64–128 KB), compressi (gzip/brotli dal server), cache SW a LRU.
- **Nexus**: grafo caricato per sottografo (vicini di 1–2 salti dell'ID aperto), non l'intero `g.json`.
- **Budget da misurare e fissare con test** (non assunti): peso indice iniziale, memoria, tempo di apertura catalogo/dossier su iPhone di riferimento; soglie regressione automatiche (estendendo `a7_test.py`).
- Importazione senza regressioni: `a3`, `a4`, `a5` leggono lo stesso formato runtime; il generatore cambia, l'interfaccia no.

## 8. Pipeline automatizzata (GitHub Actions, a blocchi riprendibili)
Stile già collaudato (`tutti_candidati`, `engine2-tutte`, `miss-minutes-archivio`): job manuali/pianificati, checkpoint, idempotenti, reportistica.
1. **Discover** — elenca entità da una sorgente (es. TMDB discover/collection + company Marvel; Comic Vine per publisher; GCD per serie).
2. **Harvest** — scarica in cache grezza (rispetto limiti: Comic Vine 200 req/risorsa/ora, una sola chiave; backoff su 429); la cache NON va nel branch di sviluppo (branch dati dedicato o artefatti).
3. **Normalize** — mappa ai campi canonici, normalizza nomi/date, estrae ID esterni.
4. **Resolve** — dedup (§4) e collegamento a ID esistenti.
5. **Enrich** — completa campi da fonti secondarie con provenienza per campo.
6. **Validate** — schema, regole (§1), integrità referenziale (relazioni su ID esistenti), nessun fatto senza fonte, conteggi attesi, nessuna scomparsa di ID.
7. **Review queue** — `coda.json`: solo casi ambigui/controversi vanno all'utente (come per i link ambigui); il resto è verificato dal ledger documentale.
8. **Promote & Build** — canonico → shard runtime (`tools/atlante_a3.py`-successore) → test completi → ZIP.
9. **Delta periodico** — aggiornamento incrementale (nuove uscite, correzioni) con diff e approvazione di riepilogo.
Ogni job produce: report, conteggi, esito, elenco delle voci nuove/modificate/respinte.

## 9. Integrità delle integrazioni (garanzie testate)
| Elemento | Garanzia | Test |
|---|---|---|
| ID storici | tutti presenti, invariati | confronto con `baseline_A0` e registro ID |
| Ritratti privati | chiave = ID identità+continuità: nessun ID cambia | test a31 + nuova verifica ID |
| `tva-atlante-v2` | nessuna lettura/scrittura dalla pipeline; ID in `esp/fav/col/hub/uni/rel` restano risolvibili (redirect) | simulazione stato utente su build nuova |
| XP/Tessera | nessuna ricompensa duplicata; tetto 30/giorno; registro permanente | `a5_test` + scenario di crescita DB |
| Badge | mai revocati quando il DB cresce | `a5_test` (non revoca) |
| Completamenti Universo/Hub | **D5**: regola proposta: le nuove voci non annullano completamenti già premiati (ledger permanente); i nuovi totali valgono per i completamenti futuri | scenario di crescita |
| Miss Minutes | congelata; `atl:<id>` continua a funzionare; integrazione dei nuovi dati = decisione futura separata | test host |
| Percorsi/Nexus | nodi via ID; relazioni solo su voci esistenti | `a40`/`a41`/`a43` |

## 10. Onde operative (ogni onda: test → report → approvazione dell'utente prima della successiva)
- **W0 — Architettura e censimento** (nessun contenuto pubblicato): schema canonico v1, registro ID, importazione dei 452 storici senza modifiche, generatore runtime a livelli (verificato identico in output sui 452), pipeline Discover+Harvest in sola lettura, **censimento** per categoria/continuity con dati pubblici, report di fattibilità e budget (peso, quote, minuti Actions).
- **W1 — MCU completo** (Livello A): tutte le opere MCU (film, serie, speciali, corti, animazione MCU), interpreti, identità, organizzazioni, artefatti, luoghi, pianeti, eventi.
- **W2 — Film Marvel pre-MCU e paralleli**: Fox (X-Men, Fantastici Quattro, Deadpool), Sony (Raimi, Webb, SSU, Venom), Blade, Hulk 2003, Punisher, Ghost Rider, Elektra, ecc.
- **W3 — Serie TV non-MCU**: Netflix/Defenders, Agents of S.H.I.E.L.D., Runaways, Cloak & Dagger, Inhumans, Legion, The Gifted, Helstrom e analoghe (come già parzialmente presenti nelle 27 continuity).
- **W4 — Animazione**: serie e film animati (anni '60–oggi), What If…?, X-Men '97, Spider-Verse, Marvel Animation Universe, Marvel Productions.
- **W5 — Fumetti, Livello A + struttura**: testate/volumi, saghe/archi, prime apparizioni delle identità già in catalogo, creatori (se D2), continuity fumettistiche.
- **W6 — Fumetti, Livello B** (secondo la soglia D3) e relazioni narrative documentate (obiettivo D9).
- **W7 — Consolidamento**: dedup globale, qualità, copertura, prestazioni, documentazione finale, delta periodico automatico.
L'ordine W1–W5 è una proposta: l'utente può riordinarlo (D6).

## 11. Qualità e controlli automatici (suite `tests/db_*`)
Schema valido · ID unici e immutabili · nessun duplicato nome+continuity · integrità link/relazioni · ogni fatto con fonte e licenza · nessuna relazione narrativa da sola co-apparizione · conteggi coerenti tra canonico/runtime/UI · nessun testo con prosa copiata (confronto con fonte per sovrapposizioni lunghe) · prestazioni entro soglia su viewport iPhone/iPad · regressioni A3–A7 · test di crescita (stato utente simulato prima/dopo).
Metriche di copertura per continuity/categoria pubblicate a ogni onda (verificate nel codice, separate dai conteggi storici).

## 12. Sostenibilità a 0 €
- Solo piani gratuiti: TMDB (già attiva), GCD (dump pubblici), Wikidata, Comic Vine (chiave gratuita, **attivazione = tua autorizzazione**).
- Rispetto dei limiti con code e riprese (blocchi), nessuna richiesta inutile; cache locale riutilizzata.
- Minuti Actions gratuiti: **da verificare** sul tuo piano in W0 prima di pianificare i volumi.
- Dimensione repo: dato normalizzato compresso nel repo; grezzo fuori (branch dati/artefatti).
- Nessun database esterno, nessun hosting nuovo: dati statici nello ZIP che pubblichi tu.

## 13. Rischi e mitigazioni
| Rischio | Mitigazione |
|---|---|
| Volumi enormi (fumetti) oltre la capacità dell'app | livelli A/B/C, censimento W0, indice a livelli |
| Duplicati/omonimi | chiavi forti, hub, coda di revisione, mai fusioni automatiche |
| Dati errati o in conflitto | gerarchia fonti, due fonti per «verificata», coda conflitti |
| Licenze CC BY-SA / non commerciale | solo fatti, attribuzioni, uso personale; revisione se mai distribuita |
| Limiti API | blocchi riprendibili, backoff, cache |
| Regressioni su dati personali | test di crescita, registro ID, nessun accesso alla pipeline ai dati utente |
| Prestazioni iPhone | budget misurati e soglie automatiche |
| Minuti Actions insufficienti | verifica in W0; fallback: esecuzione locale degli stessi script |

## 14. Decisioni richieste (con default consigliato)
| # | Decisione | Default proposto |
|---|---|---|
| D1 | Nuove categorie **Opere** e **Fumetti** nell'Atlante | sì, senza N° e senza toccare i 138 titoli |
| D2 | Categoria **Creatori** (autori/disegnatori) | sì, solo Livello A/B collegati |
| D3 | Ingresso dei personaggi **solo-fumetto** (Livello B) | dopo censimento: adattamento esistente o soglia di rilevanza misurata |
| D4 | Rapporto con i 138 titoli numerati (Tessera/Missioni/percentuali) | nessuna modifica; le nuove opere solo nell'Atlante |
| D5 | Completamenti Universo/Hub quando il DB cresce | premi già ottenuti intatti; nuovi totali per i futuri |
| D6 | Ordine delle onde W1–W5 | come proposto |
| D7 | Attivare Comic Vine (chiave gratuita personale, solo non commerciale) | sì, quando autorizzi |
| D8 | Testi italiani | modelli di frase deterministici; niente prosa copiata; nessun LLM senza tua approvazione |
| D9 | Obiettivo relazioni narrative (500 non raggiunto) | nessun obiettivo numerico; solo relazioni documentate |
| D10 | N°077 e N°125: fonte per completare l'archivio Miss Minutes | da indicare/da cercare in W1 |
| D11 | Johnny Storm N°117: discrepanza | da risolvere in W2 con fonti |
| D12 | 34 relazioni «da verificare»: criterio | promozione con 2 fonti, altrimenti scarto motivato |
| D13 | Ritratti per le nuove identità | stessa pipeline privata, richiesta separata per ondata |
| D14 | Integrazione dei nuovi dati in Miss Minutes (oggi congelata) | richiesta separata dopo W1 |

## 15. Cosa succede dopo la tua approvazione
1. Rispondi alle decisioni D1–D14 (o scrivi «default»).
2. Avvio **W0** (architettura + censimento): ZIP di test con generatore a livelli invariato nell'output, nessun contenuto nuovo pubblicato; report di fattibilità con numeri reali.
3. Approvazione dei numeri/budget → W1, e così via, un'onda per volta, ciascuna con test automatici e senza collaudi manuali intermedi (salvo tua richiesta).

*Questo documento è una proposta: nessun dato, codice di espansione o servizio è stato attivato.*
