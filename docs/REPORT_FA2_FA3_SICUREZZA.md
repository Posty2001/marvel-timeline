# F-A2/F-A3 — Verifica finale di sicurezza (build 20261109-1730-fa2, invariata)

## Stato: sicurezza NON dichiarata verificata
L'emulatore ufficiale Firebase NON e' eseguibile in questo ambiente (firebase-tools/npm non raggiungibili: BLOCKED). Nessun servizio Firebase reale e' stato usato. Le prove sono su simulatore delle regole + SDK/DB simulati. Per chiudere la verifica serve eseguire `firebase/emulator` sul tuo PC (README incluso, nessun account, nessun dato reale) oppure autorizzare un progetto Firebase TEST.

## Vulnerabilita' trovata e corretta (regole)
- Con profilo invariato, la regola CAS accettava QUALSIASI valore di `meta/rev` (rewind o salto). Un client difettoso/malevolo del proprietario poteva falsare la revisione e disarmare la protezione tra dispositivi (non cross-account).
- Correzione: `.validate` richiede (profilo invariato E rev invariata) OPPURE rev = precedente+1 (1 alla creazione). Mutazione sulla vecchia regola: 2 test falliscono → i test sono sensibili.
- Il client non e' cambiato (scrive gia' rev+1).

## Risultati (simulatore regole, 54 casi) + e2e (69 controlli) — tutti PASS
| # | Verifica | Esito |
|---|---|---|
| 1 | A non legge/modifica/cancella dati di B (e viceversa), nessuna enumerazione di `users` | PASS (simulatore) / BLOCKED (emulatore) |
| 2 | Non autenticato: nessuna lettura/scrittura; email non verificata negata | PASS / BLOCKED |
| 3 | UID non falsificabile: scrittura in altro uid negata, campi uid/owner rifiutati | PASS / BLOCKED |
| 4 | Rev obsoleta, saltata, rewind rifiutate dal DATABASE | PASS / BLOCKED |
| 5 | Due dispositivi dalla stessa base: vince uno solo (DB); client mostra conflitto/update, mai sovrascrittura silenziosa | PASS / BLOCKED |
| 6 | Modifiche offline non perse in conflitto: restano sul dispositivo, cloud intatto, copia di sicurezza locale prima del ripristino | PASS (e2e mock) |
| 7 | Backup verificati (SHA-256, dimensione, formato) prima del ripristino | PASS (e2e mock) |
| 8 | Backup alterato rifiutato, dati locali invariati; backup create-only nelle regole | PASS |
| 9 | Regole users non alterano rooms/sync (differenziale: 12 operazioni con/senza `users`, merge additivo) | PASS su regole SEGNAPOSTO; regole di produzione reali NON viste → da confermare con `npm run merge` (si ferma se altera rooms/sync) |
| 10 | Logout: nessuna connessione/richiesta DB, elenco backup non visibile; cambio account: D non si connette col flag di C, nessun upload, stato «foreign», nessun contenuto di C nei backup di D | PASS (e2e mock) |
| Atomicita' | CAS valutato dal database in scrittura atomica multi-percorso; update con un percorso non valido non scrive nulla | PASS (simulatore) / BLOCKED (emulatore: il simulatore replica la semantica, non e' Firebase) |

## Limiti noti
- Il logout NON cancella i dati locali (scelta non distruttiva): su dispositivo condiviso restano visibili in locale a chi usa il browser; non vengono mai caricati in un altro account.
- Il simulatore e' scritto da me: puo' divergere dal motore reale (es. valutazione di `.validate` sugli antenati). Per questo l'esito e' PARZIALE finche' non gira l'emulatore.
- Regole di produzione attuali non disponibili: caso 9 provato solo in forma differenziale.

## Produzione: nessuna modifica
Nessuna scrittura su Firebase (reale o test), regole non pubblicate, nessun commit/push/deploy, nessun dato personale caricato, repo a 4d73feb.

## Piano di rilascio (da eseguire SOLO dopo la tua autorizzazione)
0. Prerequisito: `firebase/emulator` PASS sul tuo PC con le regole attuali esportate.
1. Backup: esporta le regole attuali (file datato) e il profilo locale (Esporta profilo).
2. Regole: aggiungi SOLO il nodo `users` (merge generato, diff = solo `users`) in Console > Regole > Pubblica. Subito dopo smoke test: rooms/sync funzionano come prima. ROLLBACK regole: ripubblica il file delle regole attuali (secondi; nessun dato toccato).
3. Frontend: commit unico fa2, tag `pre-fa2` su 4d73feb, push main → GitHub Pages. Il frontend senza regole `users` e' innocuo (la sync account resta spenta, il pulsante dara' errore di autorizzazione senza toccare dati). Ordine: regole PRIMA, frontend DOPO.
4. Verifica online: build id da sw.js, un account di prova (non il tuo) con dati fittizi: attiva sync, secondo dispositivo, conflitto, backup.
5. ROLLBACK frontend: `git revert` del commit fa2 (o ripristino tag pre-fa2) → TD2 invariato; i dati nel cloud `users/*` restano ma inerti. ROLLBACK completo: rimuovi il nodo `users` dalle regole (i dati cloud diventano inaccessibili, non cancellati).
6. Migrazione dei tuoi dati reali: solo manuale, con tua conferma, dopo i passi 1–4.
