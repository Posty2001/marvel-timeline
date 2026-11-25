# Atlante 2.0 — Regole XP e badge (valori e condizioni APPROVATI dall'utente; implementazione non avviata)

## Principi
Ricompense uniche e permanenti · nessun XP perso oltre il tetto (accredito differito) · nessun farming con apri/chiudi · nessuna revoca di traguardi quando il registro cresce · alias, segnaposto e duplicati non danno ricompense · gli hub danno solo la ricompensa di completamento prevista · nessuna modifica alle ricompense già ottenute · XP di esplorazione nelle classifiche XP esistenti, **mai** nelle classifiche dei contenuti personali né nei punteggi dell'Arcade.

## Tetto giornaliero
**30 XP/giorno** per l'esplorazione. L'eccedenza resta **in coda** e viene accreditata nei giorni successivi (nessuna perdita).

## Dossier «esplorato» (criterio concreto)
Nella **stessa apertura**: ≥ 10 s di tempo visibile attivo **e** scorrimento ≥ 60 % **e** ≥ 2 sezioni consultate. Non cumulabile tra aperture diverse; una sola volta per id canonico; solo schede reali (non alias/segnaposto/duplicati).

## Registro permanente
Libro mastro `tva-atlante-v2` separato e additivo, **senza il limite di 200** della banca missioni; una chiave per ricompensa. **Unica modifica a Tessera TVA**: una riga additiva nel calcolo XP, autorizzata, da applicare solo dopo verifica anti-duplicazione/regressione (confronto XP prima/dopo su dati reali, test su utenti con molte ricompense).

## Badge (8 × 40 XP) e disponibilità reale oggi
| Badge | Requisito | Oggi |
|---|---|---|
| Esploratore | 25 dossier esplorati | ottenibile |
| Archivista | 100 dossier esplorati | ottenibile (304 schede) |
| Cartografo | 10 universi completati | **non ancora ottenibile**: manca la chiave personaggio→universo |
| Cacciatore di varianti | 3 hub completati | **non ancora ottenibile**: 1 hub confermato (Peter); Fisk in verifica |
| Custode degli artefatti | 25 artefatti | **non ancora ottenibile**: 16 schede |
| Storico del Multiverso | 25 eventi | **non ancora ottenibile**: 3 eventi (+11 saghe, 4 battaglie) |
| Maestro del Nexus | 100 relazioni narrative distinte | **non ancora ottenibile**: relazioni tipizzate verificate ancora poche |
| Custode del Multiverso | 500 dossier esplorati | **non ancora ottenibile**: 304 schede |

L'interfaccia mostra «Non ancora ottenibile» con il motivo; i conteggi si calcolano dai dati.
