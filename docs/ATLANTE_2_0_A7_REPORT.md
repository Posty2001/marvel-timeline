# TVA Atlas (Atlante 2.0) — A7: rifinitura finale e ottimizzazione iPad (build a70, TEST)

> **Correzione 28/11/2026 (utente):** l'obiettivo storico approvato per le relazioni narrative documentate NON era 500 ma **10.000+**; gli obiettivi orientativi della Database Expansion sono: 1.000+ personaggi, 300+ varianti, 200+ artefatti e armi, 100+ universi e dimensioni, 10.000+ relazioni narrative documentate. Sono traguardi orientativi: nessun contenuto va inventato per raggiungerli.

Autorizzata dall'utente il 27/11/2026 (19:55). Una sola build consolidata, nessun collaudo manuale intermedio. Produzione invariata, 0 €, dati personali preservati, Miss Minutes congelata (solo adattamento grafico per tablet).

## Decisioni applicate
- **+1 XP per relazione narrativa distinta esplorata nel Nexus CONFERMATO** (max 10/giorno dentro il tetto di 30; una sola volta per relazione; nessun XP per co-apparizioni, collegamenti editoriali, relazioni «da verificare» o duplicati inversi). Già coerente col codice (`relKey` in `a5.js`: classe narrativa, verifica ≥ guida, chiave univoca inversa-normalizzata).
- A5 e A6 approvate a livello implementativo.

## Ottimizzazione iPad (nuova)
Approccio additivo: `assets/tablet.css` (collegato nella head), attivo SOLO con `min-width:768px` **e** `min-height:600px` (iPad verticale/orizzontale, Split View ampia, finestre ridimensionate). iPhone (anche orizzontale: altezza < 600) e Split View stretta restano identici; il ridimensionamento passa da un layout all'altro senza ricaricare.
- Home: colonna ampia a due colonne (prossimo titolo / missione).
- Timeline: schede dei titoli in griglia dinamica (`auto-fill`, ≥2 colonne).
- Centrale TVA: pannelli affiancati.
- Friends e Tessera: contenuto centrato a larghezza utile; pannelli Friends su due colonne.
- TVA Atlas: griglie con colonne dinamiche, hero più alta, liste a due colonne; **Dossier con ritratto/azioni/indice a sinistra (sticky) e informazioni a destra** (nuovi contenitori `a3-side`/`a3-main`, trasparenti su telefono con `display: contents`).
- Osservatorio e Nexus: mappa immersiva a sinistra con pannello laterale (360/400 px); schermo intero della mappa invariato. Percorsi centrati (max 820 px).
- iPad orizzontale (≥1180 px): la barra laterale della guida non copre più TVA Atlas (bug reale trovato nell'audit).
- Quiz: colonna più ampia (760 px) su tablet. Arcade e Rankings già adattivi (nessuna modifica).
- Miss Minutes: SOLO grafica (`mm.css`): colonna 900 px, argomenti su due colonne, testo leggermente più grande. Motore, intelligenza, gateway, quote e blob invariati.

## Rifinitura e coerenza
- Rimossi riferimenti tecnici/di sviluppo visibili: «pilota A3.1», «Anteprima A3 in collaudo», «NUOVO · ANTEPRIMA A3», «Atlante 2.0» nelle etichette di caricamento/errore (ora «TVA Atlas»), «chiave separata» nella Progressione, riferimento obsoleto a «40 identità» nei ritratti.
- Progressione: spiegazione che i dossier contano solo se effettivi e documentati (315 personaggi nel catalogo ≠ 310 esplorabili: esclusi segnaposto/alias/voci in verifica).
- Verificatori dati: `atlante_a3.py`, `atlante_identita.py`, `atlante_relazioni.py`, `atlante_a4.py` (--verifica) tutti OK.
- Conteggi verificati nel codice (27/11): 452 voci (315 identità, 49 attori, 27 universi, 17 organizzazioni, 16 artefatti, 9 luoghi, 7 pianeti, 7 eventi, 3 hub, 2 mantelli); relazioni 1276 record = 245 narrative (207 con fonte, 4 guida, 34 da verificare), 1026 editoriali, 5 controparti.

## Verifiche automatiche (essenziali)
`tests/a7_test.py` 110/110 (iPhone, iPhone orizzontale, Split View stretta, iPad verticale/orizzontale/Pro, ridimensionamento, nessun overflow, layout dossier/Nexus/Timeline/Home, prestazioni catalogo, nessun testo tecnico); `a5_test.js` 42/42; `a5_ui_test.py` 17/17; a3 32/32; a31 40/40; a32 21/21; a35 5/5; a40, a41, a42 OK; a43 73/0; percorsi 33/0; Tessera 48/0; `verify_test` 45/45; MM `ui_viewport` 18/18, `ui_scroll` 11/0.
Nota: `tests/cons_test.py` «Back 2: posizione di scorrimento» fallisce (8 px) anche sul commit precedente: problema preesistente, non introdotto da A7.

## Limiti dichiarati
- Nessuna prova su iPad/Safari reali (solo Chromium con viewport iPad): tastiera virtuale e Split View reali non verificabili qui; le safe area usano `env(safe-area-inset-*)`.
- Quiz/Arcade/Rankings/Impostazioni: adattati per larghezza, non ridisegnati schermata per schermata.
- Ritratti privati: compilazione resta aperta (decisione dell'utente); nessun ritratto è nel repository/ZIP.
- Obiettivo 500 relazioni non raggiunto (non è prerequisito).
- A7 NON dichiarata «completata»: serve l'approvazione esplicita dell'utente.
