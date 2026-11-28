# Tessera TVA 3.0 — Report T1–T7 (28/11/2026, build `20261128-1730-t3`)

**Stato: implementata in TEST, in attesa della tua approvazione finale. Non dichiarata «completata».** Produzione congelata, budget 0 €, Database Expansion db9 non toccata, Missioni/Evolution NON avviate.

## Cosa è stato realizzato (lazy, additivo)
- Modulo `tessera2/` (`core.js` nucleo puro testabile, `sfondi.js` 12 scene SVG originali, `tessera2.js` UI, `tessera2.css`, `data/regole.json`), caricato solo alla prima apertura della Tessera (loader inline in `index.html`). Se un file manca resta la vista classica.
- Nuova chiave additiva `marvel-ultimate-timeline-tessera-v2` (vetrina, sfondo scelto, modalità animazione, titolo personale, origine/preferiti, privacy, sblocchi). Senza la chiave o con la chiave corrotta il modulo parte coi default; nessuna chiave esistente rinominata o riscritta aprendo le sezioni.
- **Cinque sezioni**: Tessera (carta 3D fronte/retro, vetrina 6 slot riordinabili/vuoti ammessi, condividi), Carriera (passaporto: rango e livello separati, progressione, statistiche reali, riconoscimenti), Atelier (anteprima dal vivo, bozza con Salva/Annulla: avatar, stile e preset, titoli, cornici, temi, effetti, sfondi animati; «Editor completo» apre l'editor classico), Collezione (56 emblemi, 48 ricompense con filtri, distintivi, sfondi; aggiunta alla vetrina), Identità (VAR-ID, nome, motto, universo di origine/preferito e personaggio preferito scelti da TVA Atlas, privacy, interruttore vista classica).
- **Sfondi animati**: 4 liberi (Sacra Linea Temporale, Terminale TVA, Multiverso, Archivio Dorato) + 8 con le condizioni da te approvate: Yggdrasil liv. 10 · Dimensione Specchio 50 dossier verificati · Dimensione Oscura liv. 15 · Regno Quantico 25% Timeline · Bifrost 10 universi verificati · Il Vuoto 50% · Spider-Verse 10 identità verificate legate a Spider-Man (42 nel registro `regole.json`) · Infinito 100%. Requisito e progresso mostrati; sblocco retroattivo e permanente (mai richiuso); nessun XP; modalità automatica/statica/nessuno, stop in background e con «riduci movimento».
- Dossier/universi «verificati» usano la stessa regola `eligible()` di Atlas (a5.js): parità testata.
- Titolo personale ≤ 40 caratteri (solo testo, caratteri di controllo/direzione rimossi), distinto dal rango ufficiale.
- Predisposizioni (nessuna rete, nessun dato inviato): `tvaT2.publicIdentity()` (identità condivisa v1, solo categorie marcate condivisibili, legame Nexus «nessuno»), `tvaTrophies.list()` vuoto; nessuno slot vuoto in UI.
- Foto: resta locale, fuori da sync/backup (invariato; mai scritta in tessera-v2).
- Layout: iPhone a colonna (carta ridotta fuori da «Tessera», anteprima fissa in Atelier); iPad due colonne (carta+vetrina a sinistra, contenuto a destra) in verticale/orizzontale, Split View compatto a colonna singola.
- **Launcher Miss Minutes**: stessa soluzione di Atlas (fascia libera + lieve spostamento, ripristino a focus/tap), attiva solo mentre «La mia Tessera» è aperta; Miss Minutes non modificata.

## Discrepanza «Titoli completati» Home vs Centrale TVA — causa
Home usava `stats.checked` = ID salvati escluse le varianti (`VARIANT_IDS`, es. N°133 specchio di N°089) e inclusi ID non più presenti nella pagina; la Centrale/Tessera conta le caselle realmente spuntate (`.watch-check:checked`) sul totale 138. Se una variante è spuntata, Home mostrava 1 in meno (es. 3 vs 4). **Correzione**: la riga Home mostra ora le caselle spuntate (stessa fonte della Centrale). Nessun dato personale modificato; percentuale, rango e XP calcolati come prima. Nota: non ho potuto riprodurre il tuo caso esatto sul tuo profilo; la causa indicata è confermata nel codice e riprodotta con una variante spuntata.

## Verifiche (tutte superate)
- Guardie T0: censimento «catalogo congelato rispettato»; `tessera_t0_test.py` 56/56.
- `tests/tessera2_core_test.js` 12/12 · `tests/tessera2_ui_test.py` 68/68 (iPhone 320/390/430, iPad verticale/orizzontale/Split View: nessun overflow, bersagli ≥36 px, salva/annulla, vetrina, sblocco retroattivo/permanente, XP invariati, chiavi personali invariate, XSS titolo, vista classica, launcher, riduzione movimento, Home=Centrale).
- Regressioni: `a5_test.js` 46/46, `db_integrazione_test.py` 24/24, a7_test (v. registro).
- Anteprime reali (screenshot dell'app): `docs/tessera2/anteprime/` — iPhone (5 sezioni), iPad verticale (5), iPad orizzontale (Tessera, Atelier).

## Attività residue / limiti
- Verifica su Safari iOS/iPadOS reali (prestazioni animazioni, 3D, Split View): non eseguibile qui.
- Preset di stile applicati nella scheda «Stile»; modifica foto e backup restano nell'editor classico (apribile da «Editor completo»).
- Friends 3.0, Missioni, Evolution, Legame Nexus, trofei Arcade/Quiz/Rankings: solo contratti dati (macro-fasi successive).
- Il tuo caso specifico 3 vs 4 va riconfermato su iPhone dopo l'aggiornamento.
