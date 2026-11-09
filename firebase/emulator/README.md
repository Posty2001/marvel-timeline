# Test regole su emulatore ufficiale (da eseguire sul TUO PC — non tocca produzione)
Requisiti: Node 20+, Java 11+. Nessun account Firebase necessario (progetto fittizio `demo-tva-test`).
1. Console Firebase > Realtime Database > Regole: copia le regole ATTUALI in `current.rules.json` (solo lettura, non modificare nulla online).
2. `npm install`
3. `npm run merge`  (crea database.rules.merged.json; si ferma se `users` esiste o se altera rooms/sync)
4. `npm test`       (avvia l'emulatore RTDB locale ed esegue i test)
Esito atteso: tutti i test PASS. Inviami l'output.
