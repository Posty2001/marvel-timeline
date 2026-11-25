# Instabilità dei test di ripristino cloud (b40c_test) – causa individuata

Stato: **causa radice trovata, nel TEST (25/11/2026)**; nessuna modifica al codice di sincronizzazione. Indagine fatta esclusivamente con dati sintetici e browser isolati (mock di Firebase, nessun ripristino su dati reali).

## Causa
1. **Race di inizializzazione (6 su 7 fallimenti storici, controllo `snapL(pg)==before`)**: il modulo TVA Live crea in modo asincrono la chiave `marvel-ultimate-timeline-live-state-v1` dopo il caricamento. L'unica chiave che differiva tra «prima» e «dopo» era questa (verificato con un confronto chiave per chiave su 4 esecuzioni: 36–37 PASS, solo quella chiave in differenza). Nessuna chiave del profilo (titoli visti, preferenze, ecc.) è mai cambiata per effetto di conflitto/ripristino/annullamento.
2. **Controllo T7 («nessuna copia»)**: l'app salva una copia di sicurezza automatica generale 5 s dopo il caricamento, indipendentemente dal ripristino; a seconda dei tempi poteva già esistere al momento del controllo. Ora il test verifica la proprietà che conta: dopo l'annullamento, la copia (se presente) contiene il profilo locale (12 titoli) e mai quello del cloud (1).

## Correzione (solo test)
`tests/b40c_test.py`: attesa dell'inizializzazione Live prima dello snapshot; T7 verifica il contenuto della copia. Esito: **4 esecuzioni consecutive 42/42 PASS** (prima 33–38). `b40c_test` rimosso da `tests/KNOWN_FAILS.json`.

## Cosa NON dimostra
- Che il ripristino cloud sia privo di difetti in condizioni reali (rete, dispositivi multipli): i test coprono il comportamento con mock. Resta valida la prassi prudente: esportare un backup locale prima di un ripristino cloud; l'auto-backup di sicurezza esiste.
- Non è stato eseguito alcun ripristino sui dati reali di Franco.
