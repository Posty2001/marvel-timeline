# A3.2 - confronto CLIP / SigLIP (misure oggettive)

- **clip**: candidati 1272 -> proposte 44 (riduzione 96.5%); tempo totale 379 s (6.3 min) su 4 CPU, RAM di picco 1824 MB; stadi {'carica_modello': 6.6, 'download': 18.0, 'punteggio_immagine': 55.9, 'ritaglio': 291.1}; immagini proposte a più identità: 0
- **siglip**: candidati 1272 -> proposte 41 (riduzione 96.8%); tempo totale 801 s (13.4 min) su 4 CPU, RAM di picco 2234 MB; stadi {'carica_modello': 9.9, 'download': 26.2, 'punteggio_immagine': 118.5, 'ritaglio': 637.7}; immagini proposte a più identità: 0

| identità | proposte CLIP | proposte SigLIP | in comune (immagini) | in comune (titoli) |
|---|---|---|---|---|
| id-iron-man | 5 | 5 | 1 | 3/3 |
| id-thor | 4 | 4 | 2 | 2/2 |
| id-loki | 5 | 5 | 4 | 3/3 |
| id-peter-parker-mcu | 4 | 4 | 1 | 2/2 |
| id-peter-parker-raimi | 5 | 3 | 0 | 2/3 |
| id-peter-parker-garfield | 4 | 4 | 1 | 2/2 |
| id-wolverine | 5 | 5 | 2 | 3/3 |
| id-wade-wilson-deadpool | 4 | 4 | 3 | 2/3 |
| id-wanda-maximoff | 4 | 3 | 1 | 1/2 |
| id-thanos | 4 | 4 | 2 | 2/2 |

Accordo medio sulle immagini: 41% (immagini in comune / proposte minime).
