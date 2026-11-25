# Atlante 2.0 — Regole proposte per XP e badge (PROPOSTA, da approvare prima di implementare)

> Nessun codice. Valori proposti: modificabili da te. **Nessuna regola è attiva.**

## 1. Come funziona oggi (verificato nel codice, 25/11/2026)
- Gli **XP totali sono calcolati** (non salvati) dalla Tessera: tag dei titoli visti, animazioni (8 XP), voti (5), note (10), **preferiti (3 XP ciascuno)**, **badge sbloccati × 40**, più la **banca XP delle missioni** (`marvel-ultimate-timeline-missioni-xp-bonus`: `totale` + elenco `ricompensate`, ricompensa assegnata una sola volta per chiave tramite `provaRicompensaMissione`).
- Rischio preesistente, **non toccato**: l'elenco `ricompensate` viene troncato agli ultimi 200 elementi; oltre quella soglia una chiave molto vecchia potrebbe essere riassegnata. Per Atlante non lo uso.

## 2. Principi (vincoli tuoi)
1. **Integrato** nel sistema esistente; nessun azzeramento, nessun progresso duplicato.
2. **Una ricompensa = una chiave univoca e permanente** (`dossier:<id-canonico>`): ripetere la stessa azione (riaprire, togliere/rimettere un preferito, ricreare una collezione) **non dà altri XP**.
3. Chiave sull'**identità canonica**, non sulla pagina: aprire un alias o una pagina poi unificata **non** ricompensa due volte; le identità già premiate restano premiate dopo le unificazioni.
4. **Segnaposto, hub e voci «da verificare» non danno XP**; l'hub dà solo il bonus di completamento.
5. **I preferiti già valgono 3 XP**: Atlante **non** li ricompensa di nuovo (nessuna duplicazione).
6. **Tetto giornaliero** di 30 XP da esplorazione (anti-farming) e nessuna ricompensa per azioni automatiche (nessun XP da link di Miss Minutes aperti da script/ricarica).
7. **Solo cumulativo**: nessuna regola sottrae XP.

## 3. Regole di assegnazione proposte
| Azione | XP | Condizione | Frequenza |
|---|---|---|---|
| Leggere un dossier | **+2** | scheda aperta con ≥ 50% di scorrimento o ≥ 8 s | 1 volta per identità canonica |
| Completare un hub | **+15** | viste tutte le identità membre | 1 volta per hub |
| Completare un universo | **+25** | viste tutte le schede dell'universo (non segnaposto) | 1 volta per universo |
| Primo confronto | **+5** | un confronto completato | 1 volta in assoluto |
| Prima collezione | **+5** | creata e con ≥ 3 schede | 1 volta in assoluto |
| Seguire una relazione nel Nexus | **+1** | apertura della scheda collegata | 1 volta per coppia, max 10/giorno |
| Badge | **+40** | già previsto dal sistema (badge × 40) | per badge |

## 4. Badge proposti (si agganciano al meccanismo badge esistente)
| Badge | Requisito |
|---|---|
| Esploratore | 25 dossier |
| Archivista | 100 dossier |
| Cartografo del Multiverso | 10 universi visitati |
| Cacciatore di varianti | 3 hub completati |
| Custode dei mantelli | tutti i mantelli esplorati |
| Tessitore del Nexus | 50 relazioni narrative seguite |
| Collezionista | 3 collezioni |
| Cosmico | prime schede di specie/entità (quando esisteranno) |

## 5. Dati e protezione
- Registro in `tva-atlante-v2` (chiave nuova, additiva) con **proprio elenco di ricompensate senza limite di 200**; incluso nell'esportazione/backup profilo in modo **additivo** (un profilo vecchio si importa identico).
- Il bonus Atlante si aggiunge al totale con **una sola riga additiva** nel calcolo della Tessera → **richiede la tua autorizzazione** perché tocca il calcolo XP esistente.
- Classifiche (Rankings): **decisione richiesta** se gli XP di esplorazione devono entrare nelle classifiche o restare fuori.
- Test obbligatori prima del rilascio: nessuna doppia assegnazione (azione ripetuta, ricarica, due dispositivi), profilo esistente invariato, totale XP invariato prima/dopo l'aggiornamento.

## 6. Decisioni che ti chiedo
(a) valori XP e tetto giornaliero; (b) elenco badge; (c) autorizzazione alla riga additiva nel calcolo XP; (d) XP di esplorazione nelle Classifiche sì/no.
