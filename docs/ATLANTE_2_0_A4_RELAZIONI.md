# Atlante 2.0 – A4.0 – Registro delle relazioni tipizzate

Stato: **A4.0 (solo architettura dei dati e analisi)**, autorizzata il 25/11/2026. Nessun codice di interfaccia. Strumento: `python3 tools/atlante_relazioni.py --scrivi|--verifica`; dati: `data/atlante/relazioni.json`.

## 1. Modello
- Nodi = **ID univoci** (`id-*` identità, `org-*` organizzazioni, `seg-*` segnaposto), **mai nomi**. Nessuna corrispondenza testuale: se una scheda cita un nome senza link/ID (es. Laufey) la voce va in coda.
- Quattro famiglie di collegamenti, **tenute separate**:
  1. **narrativa** – famiglia (genitore/fratelli/coniugi/discendente), partner, alleanza, amicizia, rivalità, mentorato, appartenenza (membro/leader), successione di mantello, copia;
  2. **controparte** multiversale (non unifica identità);
  3. **editoriale** – «Correlati» della scheda, ispirato a, stessa scheda, segnaposto;
  4. **co-apparizione** – calcolata a runtime dalle apparizioni: **non è nel registro e non conta come relazione** (`co_apparizioni_nel_registro = 0`).
- Direzione: i tipi non simmetrici hanno `da`→`a` definito (es. `famiglia_genitore`: da = genitore, a = figlio/a, con `qualifica` padre/madre/adottivo/biologico).
- Verifica: `verificata` (fonte esterna), `guida` (documentata nelle schede dell'Atlante classico, non verificata altrove), `da verificare`. Il Nexus non mostra mai «da verificare» come verificata (tratteggio + etichetta).
- Ogni record: `id` (hash di tipo+nodi), `fonte[]`, `verifica`, `origine`, `conferme[]` (quante fonti interne concordano), `nota`.

## 2. Recupero dall'Atlante classico (cosa è stato importato)
Fonti analizzate: campo **RELAZIONI** delle schede (etichetta = ruolo del bersaglio rispetto alla scheda, bersaglio da ID del link), grafo `relationshipGraphData` (appartenenza a organizzazioni), campo **CORRELATI**, e le relazioni già presenti in A2.
Scoperta importante: nel grafo classico i versi di una relazione di parentela riusano **la stessa etichetta** («Padre» sia da Tony verso Howard sia da Howard verso Tony), quindi **la direzione non si legge dal grafo**: è stata ricavata solo dalle schede, dove l'etichetta è univoca.

| Dato | Valore |
|---|---|
| Relazioni nel registro | 940 |
| – narrative | 66 (famiglia: genitore 9, fratelli 4, coniugi 1, discendente 1; partner 1; appartenenza 48; successione 1; copia 1) |
| – controparti multiversali | 2 |
| – associazioni editoriali | 872 (di cui «Correlati» 866) |
| Stato di verifica | {'da verificare': 6, 'guida': 930, 'verificata': 4} |
| **In coda (NON importate)** | **93** |

Le 9 relazioni di A2 e le 66 narrative sono ancora poche: il registro è il **punto di partenza**, non il traguardo (§4).

## 3. Coda: ambigue o errate (non importate, decisione tua)
- **Howard Stark / Tony Stark**: presente solo nel grafo, etichetta «Padre» identica nei due versi → direzione non desumibile dai dati. *(Ipotesi da confermare con fonte: Howard è il padre di Tony.)*
- **«Varianti: Jane Foster/Mighty Thor»** sulle schede di Loki e Thor: probabile errore (Jane non è una variante né una controparte documentata di Loki/Thor). Eventuale `successione` del mantello di Thor solo con fonte.
- **Laufey** (padre biologico di Loki): nome solo testuale, nessuna scheda/identità → non si risolve per nome.
- **89 voci verso pagine che coprono più identità** (es. char-wolverine (5), char-groot (4), char-harry-osborn-green-goblin (4), char-peter-parker (4), char-wilson-fisk-kingpin (4)): il bersaglio non è univoco finché non si sceglie la continuità; vanno risolte con la stessa logica dei 34 link ambigui.

## 4. Processo scalabile verso migliaia di relazioni
1. **Intake a file**: `data/atlante/relazioni_proposte/*.jsonl` (esempio in `_esempio.jsonl.txt`): `tipo`, `da`, `a` (ID), `qualifica`, `fonte[]` (URL https), `nota`. `--scrivi` valida (ID esistenti, tipo ammesso, niente auto-relazioni, niente duplicati) e scarta gli errori elencandoli in `errori_intake`.
2. **Stato automatico**: ogni proposta è `da verificare`. Diventa `verificata` solo con ≥ 1 fonte https **e** `"verifica_umana": true` (tua approvazione per lotto).
3. **Lotti per universo/franchise** (es. un universo alla volta, 50–150 relazioni per lotto): preparazione da fonti pubbliche e dalle schede, revisione a campione sul 20 %, collaudo, poi promozione. Nessun dato personale va a servizi online.
4. **Candidati assistiti** (solo proposte): dalle voci testuali ancora senza ID (LEADER/MEMBRI delle organizzazioni, nomi in «Correlati» senza link) si generano liste di *candidati da risolvere per ID a mano o con tua scelta*; non entrano mai nel registro per nome.
5. **Qualità**: `--verifica` blocca ID inesistenti, classi incoerenti, co-apparizioni nel registro, `verificata` senza fonte, derive tra registro e fonti.
6. **Metriche** a ogni lotto: relazioni per tipo/classe/verifica, % verificate, coda residua. Le co-apparizioni **non** contribuiscono mai ai conteggi narrativi.
7. **Prestazioni**: indicizzazione per nodo (adiacenza a shard lazy `atlante2/data/nexus/`) in A4.1+, non in A4.0.

## 5. Identità corrette in A4.0
- Harry Osborn diviso in tre identità autonome: Raimi (N°001–003), Webb (N°005), YFNSM (N°120); ID `id-harry-osborn-green-goblin` invariato; relazioni «stessa scheda» tra le tre; ritratti e preferiti invariati.
- Peter (franchise Deadpool) assegnato a **Earth-10005 (Fox-Verse)**, coerente con Wade Wilson (stesse apparizioni N°024 e N°117), dopo verifica delle fonti (Marvel Movies Wiki, Marvel Cinematic Universe Wiki, GamesRadar, SlashFilm). Nota: alcune fonti lo identificano con Pete Wisdom, l'attore lo ha smentito → nessuna identificazione applicata.
