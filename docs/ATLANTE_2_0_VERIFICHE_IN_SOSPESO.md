# TVA Atlas (Atlante 2.0) — verifiche in sospeso (NON bloccanti)

Decisione dell'utente del 27/11/2026 (20:33): A7 approvata, sviluppo dell'Atlante 2.0 **concluso alla build a70** e congelato. Nessun'altra sessione di collaudo manuale. Le verifiche sotto non sono state eseguite su dispositivi Apple reali; **non bloccano** la chiusura. Eventuali problemi verranno corretti durante il normale utilizzo.

## Non verificato su dispositivi Apple reali
1. Comportamento in Safari iOS/iPadOS reale: viewport dinamico, barra degli indirizzi, tastiera virtuale, scorrimento con momentum.
2. iPad reale: verticale/orizzontale, rotazione, Split View, Slide Over, Stage Manager, ridimensionamento finestra (testati solo viewport Chromium 820×1180, 1180×820, 1024×1366, 507×1180).
3. Safe area (notch, Dynamic Island, home indicator) su iPhone e iPad (usate `env(safe-area-inset-*)`, non verificate dal vivo).
4. Prestazioni e fluidità delle animazioni su hardware iPhone/iPad reale (misurati solo tempi in Chromium e assenza di long task > 700 ms).
5. PWA installata (schermo intero, service worker, aggiornamento della cache dopo il cambio build).
6. Mappe Osservatorio/Nexus con gesti touch reali (pinch, pan a due dita) su iPad.
7. Miss Minutes su tablet: solo adattamento grafico verificato in Chromium; viewport/tastiera iOS reali non provati.
8. Quota/429 reali del gateway Gemini e ridistribuzione del gateway (a carico dell'utente).

## Rimandato per scelta
- Ottimizzazioni grafiche profonde di Quiz, Arcade, Rankings e Impostazioni (oggi adattati solo in larghezza): fasi future di ciascuna sezione.
- Problema preesistente `tests/cons_test.py` «Back 2: posizione di scorrimento» (scarto di 8 px, presente anche prima di A7).

## Stato
Build a70 = riferimento congelato (tag Git `release/atlante-2.0-a70`, ZIP `ATLANTE_2_0_APPROVATA_a70.zip`). Modifiche future solo su richiesta esplicita dell'utente.
