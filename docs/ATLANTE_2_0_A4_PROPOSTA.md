# Atlante 2.0 – A4 «Multiverso e Nexus» – PROPOSTA (nessun codice di produzione scritto)

Stato: **proposta in attesa di approvazione** (richiesta del 25/11/2026). Anteprima interattiva: `docs/atlante2/a4/anteprima_A4_multiverso_nexus.html` (390 px, token della Revisione 2, dati reali del registro). Vincoli: 0 €, solo TEST, produzione congelata, strangler additivo (Atlante classico invariato come fallback), Miss Minutes intoccata, nessun dato inventato.

## 1. Principio
Multiverso e Nexus non sono due cataloghi: sono **due modi di muoversi** nello stesso spazio. Si parte da una mappa, si scende per zoom (Multiverso → Universo → Personaggio/Dossier) e si cambia direzione col Nexus (da qualunque Dossier: «Apri nel Nexus»). Ogni nodo è una porta verso il Dossier A3; ogni Dossier ha il suo Nexus. Il ritorno è sempre a un livello (breadcrumb + «Indietro»).

## 2. Multiverso (mappa a orbite)
- **Centro**: continuità principale (MCU). **Orbite** dal campo reale `NATURA`: diramazioni (anello interno), universi autonomi, raggruppamenti editoriali (anello esterno). La **TVA** è fuori dal multiverso (nodo tratteggiato, non universo) – coerente con la guida.
- Dati reali: 27 voci (1 principale, 17 autonomi, 5 diramazioni, 3 raggruppamenti, 1 luogo). Raggio del nodo = numero di identità (oggi 296 assegnate a un universo su 297).
- Interazione: tocco = scheda inferiore (natura, n. identità, più presenti, «Entra nell'universo», «Apri il Nexus»); chip = livelli on/off; pizzico/doppio tocco = zoom; tastiera/VoiceOver: nodi `role=button` con etichetta.
- **Livello Universo**: stessa orbita, ma i nodi sono le identità (ritratti A3.2 dove presenti, emblema originale altrimenti), raggruppate per saga; link «Confronta con» dal campo `COMPARE IN`.
- Confronto tra universi: due universi affiancati (identità condivise, controparti dichiarate).
- Nessuna distanza «calcolata» tra universi: la posizione è editoriale (per natura), non una misura. Lo si dichiara in legenda.

## 3. Nexus (rete)
- **Ego-network** di un'identità: centro + fino a 10 vicini; spessore = titoli in comune. Tocco su un vicino = ricentra, **trail** dei passaggi cliccabile.
- Due tipi di arco, mai mescolati: **co-apparizione** (tratteggio grigio, calcolata dai numeri di apparizione reali, soglia ≥ 3 titoli) e **relazione narrativa** (linea piena, solo le 9 dichiarate nel registro con fonte e stato di verifica). Co-apparizione ≠ relazione narrativa (regola A2).
- Filtri: Tutte / Co-apparizioni / Relazioni narrative; poi per universo, per franchise, per periodo.
- **Percorso**: scegli due identità → catena più breve (BFS) con titoli in comune per passo; se non c'è, lo dice. Nell'app definitiva i titoli saranno nominati (non solo contati).
- Relazioni tipizzate esistenti: controparte altra continuità, copia di, discendente di, erede del mantello, ispirato a, stessa scheda Atlante (+ segnaposto). Nuove relazioni solo con fonte; quelle senza fonte restano «da verificare» e visivamente distinte.

## 4. Scalabilità e prestazioni (iPhone)
- Nessuna libreria esterna: SVG/Canvas 2D, layout **deterministico** pre-calcolato (niente simulazione fisica sul telefono). Limite 60 nodi / 120 archi visibili; oltre, aggregazione per universo.
- Dati a shard lazy (come A3): `atlante2/data/nexus/` generato da `tools/atlante_a4.py --scrivi` con `--verifica`; modulo `atlante2/a4.js` lazy, non tocca l'avvio dell'app.
- Animazioni solo `transform/opacity`, rispetto di `prefers-reduced-motion`, bersagli ≥ 44 px, contrasto ≥ 4.5:1 (verificato da ui_audit).
- Co-apparizioni: indice invertito titolo→identità (≈ O(n·k)), cache in memoria; archi tra le 297 identità stimati < 10.000 con soglia ≥ 2.

## 5. Dati e lacune (da decidere, non da inventare)
1. **Peter (franchise Deadpool)** non è assegnato a nessun universo → compare fuori mappa finché non indichi l'universo.
2. N°120 (YFNSM animato) resta sotto l'identità Raimi di Harry Osborn in attesa di tua decisione.
3. 34 link ambigui (`ATLANTE_2_0_A3_LINK_AMBIGUI.md`) non entrano nel Nexus finché non decisi.
4. «Distanze» tra universi, rami What If…? e linee temporali: solo se la guida le documenta.

## 6. XP/badge
Nessuno in A4 (resta A5, vedi `ATLANTE_2_0_REGOLE_XP_BADGE.md`); in A4 solo predisposizione neutra degli eventi «universo visitato / percorso trovato», senza premi.

## 7. Fasi proposte (ognuna con collaudo iPhone tuo, nessun passaggio senza approvazione)
- **A4.0** dati: `atlante_a4.py` (grafo, shard, verifica), test sui conteggi e sulla separazione co-apparizione/relazione.
- **A4.1** Multiverso: mappa a orbite + scheda universo + livello Universo.
- **A4.2** Nexus: ego-network, trail, filtri, «Apri nel Nexus» dai Dossier.
- **A4.3** Percorso e confronto universi.
- **A4.4** rifinitura grafica, accessibilità, prestazioni; fallback classico verificato.
Test: Playwright 390/430 px, nessun errore JS, a2/a3/a31–a34/ui_audit invariati, dati non modificati (`--verifica`).

## 8. Cosa mi serve da te
Approvazione (o modifiche) a: orbite per natura + TVA separata; due tipi di arco; soglia ≥ 3; fasi A4.0–A4.4; decisioni su Peter-Deadpool, N°120 e link ambigui.
