# Draft 3.1 — integrazione 120 ritratti di test (report sintetico)

Build `20261117-1900-arcade-draft31r`. Statistiche, offerte, ruoli, scenari e difficoltà **invariati** (nessuna modifica a `core.js`/roster). Nessuna pubblicazione; Firebase, produzione e altri giochi non toccati.

## Cosa è stato fatto
- 120 WebP (600×800, 4,5 MB) copiati in `arcade/assets/draft_portraits/` e associati alle carte tramite il manifest (`<id>.webp`, id = id della carta; varianti Phoenix, Zarathos, Rune King Thor incluse). Il pacchetto aveva ID e file coincidenti col roster al 100%.
- Manifest del gioco: nuovo stato **`test_stylized`** (file + sha256 + licenza; `rights_confirmed` resta false). **Non è un'approvazione dei diritti**: sono illustrazioni originali stilizzate di test, non ritratti Marvel definitivi e non un completamento artistico. Lo stato `approved` mantiene le regole rigide.
- Motore: carica un ritratto solo per voci valide; per ogni errore (manifest assente, voce non valida, file mancante o corrotto) resta il segnaposto SVG originale. Sostituire un'immagine = cambiare file/voce nel manifest, nessuna modifica al motore.
- Le immagini hanno una didascalia incisa («Thor / STANDARD») che duplicava il nome del gioco: nascosta via CSS (ritaglio inferiore), le immagini non sono state modificate.
- Offline: manifest e 120 immagini nel precache del service worker (`sw.js`, solo elenco file e ID build).
- Validatore ritratti esteso a `test_stylized` (test negativo: file alterato → errore). `REGISTRO_ASSET.csv`: 120 righe con file, dimensioni, sha256, origine, stato.

## Verifiche Chromium (tutte superate)
- `ritratti.py` **25/25**: 120/120 carte con il ritratto corretto in miniatura e carta selezionata; squadre (5+5), battaglia e risultato nei 4 scenari; fallback per file mancante, corrotto, manifest assente e voci non valide; precache di 121 file e **partita completa offline** con ritratti da cache.
- `draft3.py` **97/97** (layout 320/390/430, cinque ruoli e pulsanti accessibili, dock sopra la home indicator, scroll, safe area simulata, nomi non tagliati, seed, salvataggi, Skip, reduced motion). Regressioni: `ux` 20/20 · `offline` 10/10 (test O2 aggiornato per accettare ritratti o SVG) · `hub` 13/13 · `int1` 12/12.

## Limiti
- Safari su iPhone reale **non verificato** (safe area solo simulata).
- Le immagini sono sagome generiche che cambiano per colore/accessori: i personaggi non sono distinguibili dall'immagine, solo dal nome sulla carta. Verificato l'abbinamento file↔carta, non la somiglianza.
- Peso della prima installazione offline aumentato di ~4,6 MB.
- Patch disclaimer non applicata; pubblicazione su TEST in attesa di autorizzazione.
