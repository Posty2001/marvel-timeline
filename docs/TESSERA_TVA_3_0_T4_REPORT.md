# Tessera TVA 3.0 — build t4 (rifinitura) — Report

Build `20261128-1830-t4`, branch `test/tva-archives`. Origine: richiesta dell'utente (28/11, 17:56) dopo la visione delle anteprime t3. Stato: **in attesa di approvazione**; macro-fase NON conclusa; Missioni ed Evolution NON avviate.

## Modifiche per punto della richiesta
1. **Intestazione/navigazione** — riga unica compatta («‹ Guida» + titolo), nessuno spazio vuoto superfluo, cinque schede coerenti con la Centrale TVA, barra inferiore originale invariata.
2. **Qualità della carta** — rimossa l'inclinazione 3D continua (causava sfocatura da rasterizzazione ruotata); inclinazione solo durante tocco/hover, carta piana a riposo; proporzioni 1,4:1; sfondo animato sotto il contenuto (leggibilità); Personalizza e Condividi subito sotto la carta, prima della vetrina; fronte/retro, rotazione e personalizzazioni intatti.
3. **Sezioni** — iPhone: carta intera in Tessera, anteprima viva nella barra di Atelier, nessuna ripetizione in Carriera/Collezione/Identità (contenuto subito visibile). iPad: carta in colonna sinistra; eliminato lo scarto laterale a ≥1180 px (padding della sidebar e bordo/ombra rosa).
4. **Atelier** — categorie Avatar, Stile, Titoli, Cornici, Temi, Effetti, Sfondi, Copie con categoria selezionata evidente («Stai modificando…»); Stile riusa il pannello dell'editor classico (`tvaTessera3.panel`); foto personale (carica/cambia/ritaglia/rimuovi) tramite il flusso esistente `photoFlow`; nome, VAR-ID e distintivi; Copie/backup via `tvaIdentity`; Annulla/Salva con bozza; editor classico sempre apribile.
5. **Sfondi animati** — 12 scene ridisegnate e distinte; anteprima attenuata anche per i bloccati con requisito e progresso; **condizioni di sblocco invariate**; animazioni leggere, modalità statica/off.
6. **Carriera** — rango, livello, XP e progressione in evidenza; due scale separate; testi naturali nell'universo TVA; nessuna statistica inventata.
7. **Collezione** — filtri compatti (menu), emblemi/distintivi/ricompense più visibili, ottenuti vs da sbloccare distinguibili; nessun elemento rimosso (56 emblemi, 48 ricompense, 12 sfondi).
8. **Identità** — Passaporto Variante con VAR-ID, universo d'origine, universo e personaggio preferiti; privacy invariata; nessun riferimento tecnico a profili duplicati.
9. **Vincoli** — nessuna perdita di dati; XP/ranghi/soglie/ricompense invariati; Database Expansion, Friends, Missioni, Evolution non toccati; 0 €; solo TEST.

## XP e livello nelle anteprime
Le anteprime usano un profilo di prova (376 XP, livello 3, Analista Junior). Il test `t4: XP, livello e rango… = vista classica` confronta i valori della nuova vista con quelli della Tessera classica sugli stessi dati: coincidono. Le differenze rispetto agli screenshot originali dell'utente dipendono esclusivamente dai dati di prova.

## Verifiche
| Suite | Esito |
|---|---|
| `tessera_t0_test.py` | 56/56 |
| `tessera_censimento.py --verifica` | catalogo congelato rispettato |
| `tessera2_core_test.js` | 12/12 |
| `tessera2_ui_test.py` (aggiornato, +27 controlli t4) | 95/95 |
| `a5_test.js` / `a5_ui_test.py` | 46/46 · 17/17 |
| `a7_test.py` (suite in sospeso completata) | 110/110 |
| `db_integrazione_test.py` / `db_test.py` | 24/24 · 18/18 |
| `f2b_f2_tessera_test.py` | 48/48 (forza la vista classica) |

Nota: `stats_fix_test.py` fallisce solo sul controllo di un id di build storico (m342): preesistente (identico su t3), non correlato.

## Residui
- Collaudo su iPhone/iPad reali (nitidezza Retina, scorrimento, launcher Miss Minutes).
- Il flusso foto è verificato nei punti di ingresso/uscita e nella non-scrittura anticipata; il ritaglio con trascinamento va provato a mano.
- Anteprime: `docs/tessera2/anteprime/` (iPhone 4 sezioni + Atelier, iPad verticale 5, iPad orizzontale Tessera e Atelier).
