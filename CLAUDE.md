# Istruzioni di progetto – TVA Archives

**Prima di qualsiasi sviluppo leggi `docs/MASTER_ROADMAP.md`** (riferimento ufficiale del progetto) e rispettane le «Regole inderogabili», gli stati di avanzamento e le «Funzionalità cancellate» (non reinserirle senza richiesta esplicita dell'utente).

**Dopo ogni intervento aggiorna** il «Registro di avanzamento» e lo «Storico aggiornamenti» della roadmap (stato, versione, commit, ZIP, problemi aperti, approvazione), senza eliminare requisiti futuri.

Vincoli permanenti: sviluppo solo sul branch `test/tva-archives`; `main` (produzione) congelato; costo 0 €; nessuna perdita di dati personali; nessuna pubblicazione, deploy o attivazione di servizi esterni senza autorizzazione esplicita; niente dati personali inviati all'AI online.

Decisioni dell'utente da rispettare (v. «DECISIONI DELL'UTENTE» nella roadmap): Friends solo per due persone (niente Squadre TVA, gruppi 2–6, TVA Group; TVA Live Room conservata); nome **Tessera TVA 3.0**; Firebase = Realtime Database + Auth esistenti (niente Firestore né servizi a pagamento senza autorizzazione); Multiverse Arena 2.0 cancellata, ma tutti i giochi, i progressi e le funzionalità di TVA Arcade vanno preservati.

Rendicontazione: tieni separati i conteggi storici (da documenti) e quelli verificati nel codice (sezione «Conteggi»); non dichiarare «completata» una funzionalità solo perché implementata o con test superati: serve l'approvazione esplicita dell'utente; non inventare specifiche mancanti, segnalale.

**Miss Minutes 1.0 è COMPLETATA, APPROVATA e CONGELATA** (versione definitiva mm6, riferimento Git stabile `release/miss-minutes-1.0-mm6` (commit `8330576`), ZIP `MISS_MINUTES_1.0_APPROVATA_mm6.zip`). Non modificarla né avviare mm7 senza richiesta esplicita dell'utente. Atlante 2.0: prima di scrivere codice serve l'approvazione del progetto da parte dell'utente.

Hotfix **mm6.1** (solo scorrimento chat, richiesto dall'utente il 25/11/2026): in attesa di collaudo/approvazione; dopo l'approvazione Miss Minutes torna congelata. Nessun altro intervento su Miss Minutes senza richiesta esplicita.

Atlante 2.0: Revisione 2 grafica APPROVATA (riferimento definitivo, `docs/atlante2/revisione2/`). Fasi A0–A1 eseguite (registro dati `data/atlante/`, estrattore `tools/atlante_estrai.py`, verifica con `--verifica`); runtime invariato (strangler). Vietato inventare dati; Bishop e Janet sospese; Miss Minutes protetta.
Atlante 2.0 A2 (identità) eseguita a livello registro: `data/atlante/identita.json`, verifica `python3 tools/atlante_identita.py --verifica`. Nessuna unificazione di persone distinte; hub e mantelli non contano come personaggi; co-apparizioni ≠ relazioni narrative; A3 non avviare senza approvazione.
Atlante 2.0 A3 (Dossier e navigazione) eseguita come anteprima additiva: modulo `atlante2/` (lazy), dati generati da `python3 tools/atlante_a3.py --scrivi` (verifica `--verifica`), test `python3 tests/a3_test.py`; Atlante classico invariato come fallback (preferenza `tva-atlante-ui=v2` per la nuova Home). In attesa del collaudo iPhone: **non avviare A4** senza approvazione. Link ambigui: `docs/ATLANTE_2_0_A3_LINK_AMBIGUI.md` (decisioni dell'utente da applicare). Nessun XP/badge in A3 (A5).
Atlante 2.0 A3.1 pilota ritratti (10 identità) predisposto: immagini PRIVATE (IndexedDB `tva-atlante-ritratti`, mai nel repository/ZIP/deploy), chiave TMDB solo nei Secret (job `atlante-pilot` in `tmdb-sync.yml`), registro `data/atlante/assets.json`, test `python3 tests/a31_test.py`. In attesa del collaudo iPhone: **non estendere alle 295 identità né avviare A4** senza approvazione. Niente archetipi condivisi/ricolorati, niente locandine come ritratti, foto attori solo nelle schede interpreti, nessuna API a pagamento.
