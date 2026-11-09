# REPORT F-A2 + F-A3 — build 20261109-1730-fa2 (copia di lavoro; NESSUN commit/push/deploy; regole NON applicate)

## Realizzato
- Profilo personale per account (Firebase Auth, email verificata) su `users/{uid}`: `profile` (stesso JSON del motore 4.0C), `meta{schema,rev,updatedAt,device}`, `backups/{id}`.
- Sync cloud riusando il motore 4.0C/4.0E (barriera init, confronto stabile, retry, conflitto con scelta esplicita, ripristino transazionale). Mai applicazione automatica del cloud.
- Scrittura con controllo di concorrenza (rev+1): un dispositivo obsoleto non sovrascrive.
- Migrazione: attivazione manuale + conferma; dati locali mai modificati/cancellati; backup «migrazione».
- Protezione dati altrui: se il dispositivo appartiene a un altro uid, nulla viene caricato (stato «foreign»).
- Offline: modifiche conservate, riallineamento al ritorno online; stato di non-sincronizzato visibile.
- Backup cloud (ultimi 5) con SHA-256, verifica prima del ripristino, ripristino con conferma + copia di sicurezza locale e cloud.
- Sync con codice (legacy) invariata e mutuamente esclusiva. Diario TVA non condiviso. Architettura TVA Friends solo descritta (firebase/PIANO_FA2_FA3.md).

## File
index.html, sw.js (build), tools/patch_fa2.py, firebase/rules.users.proposed.json (NON applicata), firebase/PIANO_FA2_FA3.md, tests/fa2_rtdb_sim.js, fa2_rules_matrix.js, fa2_rules_test.py, fa2_mockdb_server.js, fa2_test.py; adattati fa1_test (testo sync), m32_test (build), b40c_test (controlli statici: modulo account verificato a parte), SUITES.json.

## Test
- PASS fa2_rules_test 39/39 (simulatore; 6 mutazioni delle regole rilevate)
- PASS fa2_test 53/53 (SDK MOCK + DB simulato con le regole proposte): migrazione rifiutata/confermata, isolamento A/B, B non legge/scrive/enumera A, token non verificato respinto, secondo dispositivo, stato update, CAS/conflitto, foreign, offline, backup manomesso rifiutato, ripristino, logout
- PASS fa1 64, td1 33, td2 67, c3 22, c4 12, b40c 42, m32 37
- Regressione completa 62 suite: PASS 40 | FAIL 6 | BLOCKED 6 | NOT RUN 10 — insieme identico allo storico (FAIL: b32, bl, cron3c, fx_test4, fy, ui_audit; BLOCKED: cons, cop, f3, fx_test2, nav, net). Nessun nuovo FAIL.
- BLOCKED: emulatore Firebase reale, regole sul motore reale, SDK reale, prova su iPhone (sandbox senza rete verso gstatic/Firebase).
- NOT RUN: 10 suite con dipendenze esterne storiche.

## Limite della sicurezza
Le autorizzazioni sono provate solo sul simulatore con le regole proposte. NON si dichiara la sicurezza completa finché le regole non sono provate sull'emulatore/Firebase reale.

## Per andare avanti (richiede la tua autorizzazione)
1. Test regole su emulatore Firebase (sulla tua macchina) o su progetto Firebase di TEST.
2. Pubblicare le regole `users` (aggiunte, senza toccare rooms/sync) in produzione.
3. Commit/push/GitHub Pages della build fa2.
