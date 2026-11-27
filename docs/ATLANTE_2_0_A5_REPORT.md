# Atlante 2.0 / TVA Atlas — A5 (Preferiti, raccolte, progressione)

Data: 27/11/2026 · branch `test/tva-archives` · produzione congelata · 0 € · build `20261127-1900-a50`. **In attesa di collaudo su iPhone: non dichiarata completata.** A5 ripresa su richiesta dell'utente (27/11, 19:05) dopo la chiusura di Miss Minutes 2.0.

## Cosa è stato implementato (modulo lazy `atlante2/a5.js` + `a5.css`)
- **Registro `tva-atlante-v2`**: chiave nuova e additiva (nessuna chiave esistente viene riscritta; test di non regressione). Copia di sicurezza giornaliera `tva-atlante-v2-bak`. Stato corrotto → ignorato senza eccezioni. Ricompense in un libro mastro **senza il limite di 200**, una chiave per ricompensa.
- **Preferiti** (☆/★ in ogni dossier, anche hub/mantelli) e **raccolte** (creare, rinominare, eliminare con conferma in due tocchi, aggiungere/togliere dal dossier). Vista «Preferiti e raccolte» (portale in Home).
- **Dossier «esplorato»** (regola approvata): nella **stessa apertura** ≥ 10 s di tempo visibile attivo, scorrimento ≥ 60 %, ≥ 2 sezioni consultate (sezione = visibile per ≥ 50 % o ≥ 35 % dell'altezza dell'area); una sola volta per id canonico; non contano copie, hub, mantelli, voci ignote; uscire prima dei 10 s azzera.
- **Progressione** (vista «Progressione»): XP di oggi su 30, coda, dossier esplorati per tipologia sul totale reale, 8 badge con stato reale («Ottenuto», «n / N», «Non ancora ottenibile: motivo»).
- **XP**: tetto **30/giorno**, eccedenza **programmata sui giorni successivi** (nulla si perde); i badge valgono 40 XP e non sono mai revocati.
- **Tessera TVA**: **una sola riga additiva** (`leggiXpAtlante()`, sola lettura) nel calcolo XP; somma gli accrediti con data ≤ oggi (max 30/giorno), 0 se la chiave manca o è corrotta. Nessun XP nelle classifiche dei contenuti né nei punteggi dell'Arcade.

## Specifiche NON presenti nei documenti (non inventate: da decidere)
1. **XP per singolo dossier esplorato**: non specificato → impostato a **0** (`XP_DOSSIER` in `a5.js`); oggi gli XP vengono solo dai badge (40 ciascuno).
2. **Cartografo, Cacciatore di varianti, Maestro del Nexus**: servono definizioni di «universo completato», «hub completato», «relazione narrativa distinta» (e la chiave personaggio→universo): restano **«Non ancora ottenibili»** con il motivo.
3. **Custode degli artefatti / Storico del Multiverso**: interpretati come «25 artefatti / 25 eventi **esplorati**»; ottenibili solo se il registro ne contiene almeno 25 (oggi artefatti 16, eventi 3: non ottenibili).
4. **Dossier con meno di 2 sezioni**: il requisito diventa «tutte le sezioni» (altrimenti irraggiungibile); con 0 sezioni il dossier non è esplorabile.
5. **Importazione del «profilo vecchio identico»**: non esistono dati A5 precedenti da importare; le chiavi esistenti non vengono toccate (verificato).
6. Cosa conta come «alias/segnaposto/duplicato»: oggi escluse le copie (`k='c'`), hub e mantelli; gli alias sono risolti dal registro dei redirect.

## Verifiche
`tests/a5_test.js` (nucleo, 31 controlli: soglie, una volta sola, tetto e coda, badge, preferiti/raccolte, stato corrotto), `tests/a5_ui_test.py` (14 controlli a 390 px: portali, preferito e raccolta persistenti, esplorazione reale a 10 s con scroll graduale, aperture brevi, vista progressione senza overflow, Tessera +60 XP con accrediti passati e 0 per i futuri, chiave corrotta). Regressioni Atlante/Tessera: vedi roadmap. Non verificato: collaudo su Safari iPhone reale.
