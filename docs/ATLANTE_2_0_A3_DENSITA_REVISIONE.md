# Atlante 2.0 A3 – Revisione densità grafica (25/11/2026, approvata dopo anteprima 390 px)

## Implementato
- Catalogo: tre viste (griglia compatta predefinita, griglia grande, elenco) con preferenza in `localStorage` `tva-a3-vista` (chiave leggera, fuori da backup/sincronizzazione come `tva-a3-last`); Personaggi e Artefatti a 3 colonne, le altre categorie a 2 colonne compatte; filtri in pannello richiudibile con contatore; barra di ricerca da 36 px; schede più piccole (testo ≥ 11 px); badge «Identità» e sottotitoli ripetuti rimossi (resta «In verifica»).
- Home: hero 330 px (era 440, –25 %). Dossier: intestazione ≈ 210 px (era 330); «Ritratto privato» diventa icona a matita 36×36 con etichetta accessibile.
- Universi: emblema con **numero completo della Terra** (199999, 121698, TRN123…); per gli universi senza numerazione documentata solo gli anelli e la denominazione esistente nel titolo (nessun numero inventato).
- Dossier: campi ridondanti non mostrati quando il loro testo è contenuto in un altro campo della stessa sezione (es. «Universi: MCU» assorbito da «Universo: Earth-199999 — MCU»); **i dati originali (`atlante2/data/d/*.json`) restano intatti** (test dedicato).

## Launcher Miss Minutes – studio e scelta
Problema: la linguetta `#mmFab` (30×60 px, bordo destro, z-index massimo) copriva l'ultima colonna. Riservare 36 px di gutter su tutto il catalogo è stato escluso dall'utente.
Opzioni valutate:
| Opzione | Esito |
|---|---|
| A. Linguetta ridotta a 24 px visibili, ancorata al bordo, solo in Atlante | **adottata**: bersaglio 24×60 (WCAG 2.2 AA, 2.5.8), gutter destro solo 28 px nelle griglie/elenco; piena visibilità con focus/tocco |
| B. Nascondere durante lo scorrimento | scartata: nasconde l'accesso proprio quando serve, comportamento meno prevedibile |
| C. Parcheggio in basso a destra | scartata: coprirebbe comunque l'ultima riga a ogni scorrimento |
| D. Interruttore utente «nascondi launcher» | rimandata: richiede una modifica di Miss Minutes (congelata) |
Implementazione: solo CSS in `atlante2/a3.css` (selettore `html:has(#atlas2Toggle:checked + #atlas2 .a3) #mmFab`, `translate`), attivo solo con la Home/catalogo/dossier A3 visibili; **nessuna riga di Miss Minutes modificata, funzionamento dell'assistente invariato** (test: raggiungibile e cliccabile). Rimuovendo il blocco CSS si torna al launcher standard.

## Test
`tests/a32_test.py` (21 controlli: colonne, hero, filtri, barra, vista memorizzata dopo ricarico, universi, dossier, launcher, dati originali intatti), `a3_test` 30/30, `a31_test` 40/40.
