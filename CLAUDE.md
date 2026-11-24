# Istruzioni di progetto – TVA Archives

**Prima di qualsiasi sviluppo leggi `docs/MASTER_ROADMAP.md`** (riferimento ufficiale del progetto) e rispettane le «Regole inderogabili», gli stati di avanzamento e le «Funzionalità cancellate» (non reinserirle senza richiesta esplicita dell'utente).

**Dopo ogni intervento aggiorna** il «Registro di avanzamento» e lo «Storico aggiornamenti» della roadmap (stato, versione, commit, ZIP, problemi aperti, approvazione), senza eliminare requisiti futuri.

Vincoli permanenti: sviluppo solo sul branch `test/tva-archives`; `main` (produzione) congelato; costo 0 €; nessuna perdita di dati personali; nessuna pubblicazione, deploy o attivazione di servizi esterni senza autorizzazione esplicita; niente dati personali inviati all'AI online.

Decisioni dell'utente da rispettare (v. «DECISIONI DELL'UTENTE» nella roadmap): Friends solo per due persone (niente Squadre TVA, gruppi 2–6, TVA Group; TVA Live Room conservata); nome **Tessera TVA 3.0**; Firebase = Realtime Database + Auth esistenti (niente Firestore né servizi a pagamento senza autorizzazione); Multiverse Arena 2.0 cancellata, ma tutti i giochi, i progressi e le funzionalità di TVA Arcade vanno preservati.

Rendicontazione: tieni separati i conteggi storici (da documenti) e quelli verificati nel codice (sezione «Conteggi»); non dichiarare «completata» una funzionalità solo perché implementata o con test superati: serve l'approvazione esplicita dell'utente; non inventare specifiche mancanti, segnalale.
