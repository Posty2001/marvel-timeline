# Miss Minutes 2.0 – Fase a (build 20261127-0010-mm2a) – IN COLLAUDO, non completata

**Autorizzazione:** architettura approvata e sviluppo per fasi autorizzato dall'utente (26/11, 16:43). Solo TEST; produzione, A5, TVA Live non toccati; nessun deploy; sonda grounding NON eseguita.

## Cosa è stato fatto
- **Causa radice di «Peter Parker interpretato da Peter Parker»:** `resolveRefs` inseriva il titolo della scheda dopo parole funzionali. Ora i marcatori `[[id]]` vengono solo rimossi (mai inserito testo); le schede citate diventano chip strutturati. Gli URL del modello restano rimossi.
- **Verificatore deterministico** `miss-minutes/verify.js` (nessuna AI, nessuna rete): controlla attore/personaggio/continuità/produzione e stato di uscita (già uscito / non ancora) frase per frase; un nome assente dall'archivio NON è falso (solo conflitti con dati documentati); la presenza di una fonte non verifica l'intera risposta.
- **Compatibile con lo streaming:** le frasi vengono controllate prima di essere mostrate (la coda incompleta è trattenuta solo se contiene parole sensibili); la frase errata non compare mai e non c'è sostituzione a posteriori. Alla violazione: stream interrotto, **al massimo UNA** ripresa (`riprendi`) dal prefisso verificato (o riscrittura guidata se il prefisso è vuoto); al secondo fallimento si mostra il prefisso + dichiarazione di incertezza.
- **Conoscenza interna pertinente:** `knowledge/fatti.json` (45 voci cast con fonte, alias titoli, indizi di continuità; `python3 tools/mm_fatti.py --scrivi|--verifica`), Timeline (titoli già usciti inclusi, data odierna reale), TVA Live. Si inviano al gateway solo fatti pertinenti alla domanda (max 8), con classe (archivio-app, confermato, provvisorio, documentato…), senza `seen`/`rating`/dati personali.
- **Gateway** (`miss-minutes/gateway/worker.ts`, copia nello scheduler repo; **da ridistribuire dall'utente**): data odierna Europe/Rome, `fatti` sanificati (dati, mai istruzioni), `riprendi`, prompt aggiornato (priorità ai fatti recenti, «non verificabile» se mancano, nessun attore = personaggio).
- **Diagnostica locale facoltativa** (default OFF): testo grezzo vs mostrato per le ultime 20 risposte, solo su questo dispositivo, disattivabile, cancellabile, copiabile.
- **Bug reale trovato dal test UI e corretto:** «Spider-Man» (N°001) si sovrapponeva a «Spider-Man: Brand New Day» disattivando il controllo di stato; ora vince il titolo più specifico.

## Verifiche
verify 24/24 · gateway 58/58 · e2e 8/8 · ui_mm2 13/13 (frase errata mai visibile, 1 sola rigenerazione, incertezza al 2° fallimento, attore=personaggio) · ui_stream 26/26 · ui_test 67/67 (4 attese aggiornate al nuovo contratto) · mm6 35/35 · mm6.1 10/10 · engine 37/37.

## Limiti / non ancora fatto
- Fase b: archivio fatti TMDB+Wikipedia/Wikidata con attribuzioni, ricerche a runtime con cache, fonti ufficiali Marvel/Sony/Disney, verifica limiti gratuiti (Cloudflare, TMDB, Wikimedia, Gemini). BND: dato di uscita (31/07/2026) da riscontrare su fonte ufficiale prima di inserirlo come «confermato».
- Fase c: ≥50 domande documentate e metriche.
- Sonda grounding: solo dopo tua conferma esplicita che la fatturazione è disattivata.
- Il verificatore intercetta errori noti (cast documentato, stato di uscita): non garantisce la verità di ogni frase. Safari iOS reale non verificabile qui.
