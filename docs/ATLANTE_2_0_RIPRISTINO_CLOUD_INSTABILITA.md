# Instabilità dei test di ripristino cloud (b40c_test) – nota di rischio

Stato: **aperto, causa radice non determinata** (25/11/2026). Non modificato il codice di sincronizzazione.

## Fatti verificati
- `tests/b40c_test` fallisce anche eseguito da solo; l'insieme dei controlli falliti cambia tra le esecuzioni (33–38 PASS).
- Sei fallimenti su sette includono il controllo «dati locali invariati» (`snapL(pg)==before`): in quelle esecuzioni lo stato locale dopo un ripristino/conflitto risultava diverso da prima.
- Non è stato possibile individuare la chiave divergente: lo script diagnostico `/tmp/b40c_dbg2.py` non è riuscito (dipendenza da un percorso inesistente, `snapL` non definito) e non è nel repository.
- Non provocato dal lavoro A3/A3.1 (atlante2/ è lazy e non tocca il sync); non dimostrato che sia anteriore: serve un bisect.

## Rischio
Se la divergenza è reale e non un artefatto del test (timing/ordine di scritture, chiavi con timestamp), un ripristino da cloud potrebbe alterare dati locali. **Non declassare a «rumore» finché non è chiarito.**

## Protezione raccomandata finora
1. Prima di ogni ripristino cloud: esportare un backup locale.
2. La copia di auto-backup al ripristino esiste (T8a): verificarla prima di fidarsi.
3. I ritratti privati (IndexedDB `tva-atlante-ritratti`) sono fuori da backup/sync: non sono toccati dal ripristino, ma neppure protetti; usare Esporta ritratti.

## Attività proposta (separata, da autorizzare)
Task di causa radice: (a) loggare le chiavi differenti nel confronto `snapL`; (b) bisect sui commit; (c) ripetere N=20 esecuzioni per stimare la frequenza; (d) correggere o riclassificare con prova.
