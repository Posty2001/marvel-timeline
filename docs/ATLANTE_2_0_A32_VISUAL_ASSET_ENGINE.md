# Atlante 2.0 – A3.2 Visual Asset Engine (progetto + prototipo sulle 10 identità del pilota)

Stato: **prototipo di fattibilità eseguito sulle sole 10 identità del pilota**; nessuna estensione alle 296 identità; A4 non avviata; produzione non toccata; budget 0 €.
Misure oggettive aggiornate: `data/atlante/engine/CONFRONTO.md` (generato da `tools/atlante_engine_confronto.py`).

## 1. Principi invariati (decisioni dell'utente)
- Immagini **private** sul dispositivo (IndexedDB `tva-atlante-ritratti`), mai nel repository/ZIP/deploy; nessuna chiave nel frontend; nessuna API a pagamento; nessun archetipo condiviso/ricolorato; nessuna locandina come ritratto; foto degli attori solo nelle schede interpreti.
- Il motore **propone, non decide**: ogni immagine entra solo dopo un'approvazione dell'utente (un tocco) o una scelta manuale.
- Registro asset (`data/atlante/assets.json`), verifica dei diritti, sostituzione/ritaglio/rimozione, esportazione/importazione: invariati.

## 2. Architettura (semi-automatica, tutta gratuita)
```
 [GitHub Actions, CPU gratuita]                                  [iPhone, privato]
 candidati TMDB (metadati) ──► filtri duri ──► punteggio visivo ──► ritaglio 3:4 ──► proposte.json (metadati)
                                (continuità,      (CLIP / SigLIP,     (finestre,        │
                                 titoli condivisi, margine log-odds)   formato app)      ▼
                                 risoluzione,                                      selettore: 3–5 schede 3:4 con ✓ Approva
                                 dedup)                                            → IndexedDB (copia locale) + rango registrato
```
1. **Filtri duri (deterministici)**: solo titoli verificati della continuità; i titoli condivisi tra varianti della stessa famiglia (es. N°099 per i tre Peter Parker) sono esclusi dalla proposta automatica (restano disponibili nella scelta manuale); larghezza ≥ 1280 px; nitidezza minima; deduplica con dHash.
2. **Punteggio visivo**: modelli aperti tramite `open_clip` (CLIP ViT-B/32 LAION-2B; SigLIP ViT-B/16 WebLI). Metrica = **margine log-odds** dell'etichetta dell'identità contro tutte le altre identità del pilota e contro negativi generici (paesaggio, folla, testo/logo, volto senza costume, veicolo, esplosione, scena buia). *Correzione emersa nel prototipo*: la probabilità softmax saturava a 1,0 per ogni scena (tutte provengono dal film giusto) e non ordinava nulla; il margine non satura.
3. **Ritaglio verticale suggerito**: ricerca a finestre 3:4 (3 scale × 7 posizioni) con la stessa metrica; funziona anche con maschere e caschi (Iron Man, Spider-Man, Deadpool), dove un rilevatore di volti fallirebbe. Convertito nel formato dell'app `{z,cx,cy}`.
4. **Selezione finale 3–5**: punteggio composto (60 % riconoscibilità, 25 % nitidezza, 15 % esposizione), al massimo 2 per titolo (fino a 3 se servono per arrivare a 3 proposte), scene quasi identiche scartate (similarità degli embedding).
5. **Approvazione rapida** (nuova nell'editor dei ritratti): sezione «Proposte automatiche» con anteprime 3:4 già ritagliate; **✓ Approva** salva con un tocco; toccando la scena si rivede il ritaglio. Nel record si registrano rango e punteggio (`scena.rk`, `scena.sc`) per misurare la precisione reale (rango dell'approvato) senza dati aggiuntivi.
6. **Sostituzione manuale** sempre disponibile (scelta tra tutte le scene candidate, importazione locale, ritaglio libero).

## 3. Cosa NON fa (limiti dichiarati)
- **Nessun riconoscimento facciale degli attori** (dato biometrico, non necessario, rischio privacy).
- Non attribuisce dati narrativi né decide le varianti: la continuità si decide dai metadati verificati, non dal modello.
- Non produce né copia immagini: nel repository vanno solo percorsi CDN, punteggi e ritagli. Le miniature w780 vengono scaricate **solo nel runner** e scartate a fine job; l'artifact di valutazione (miniature) ha retention di 1 giorno.
- I prompt visivi (`PROMPT` in `tools/atlante_engine.py`, es. «Iron Man in red and gold armor») sono ipotesi di lavoro del motore, non dati dell'Atlante.

## 4. Diritti e conformità (per sorgente)
| Sorgente | Uso consentito dal progetto | Verifica nel motore |
|---|---|---|
| TMDB (scene) | solo privato/locale, attribuzione mostrata, nessuna ridistribuzione | blocco `diritti` in ogni `proposte_*.json`; percorsi solo `image.tmdb.org`; TMDB non concede diritti sui contenuti Marvel/Disney |
| Importazione locale dell'utente | responsabilità dell'utente, resta sul dispositivo | `fonte: import-locale` nel record |
| Illustrazioni originali (universi, luoghi, eventi) | libere, autoprodotte | registro asset, nessun elemento protetto |
| Wikimedia Commons (futuro, eventuale) | solo CC0/PD/CC-BY con attribuzione registrata; escluse NC/ND | controllo del campo licenza per file prima di proporre |
| Modelli | CLIP/OpenCLIP (MIT), SigLIP (Apache-2.0): solo inferenza gratuita su CPU | da riverificare le licenze dei pesi prima di ogni estensione |

## 5. Tutte le categorie dell'Atlante (progetto, non implementato)
| Categoria | Immagine specifica | Come |
|---|---|---|
| Personaggi (296) | scena TMDB della variante, ritaglio 3:4 | pipeline §2, estesa solo dopo l'esito del prototipo |
| Hub multiversali | **composizione dei ritratti delle varianti** (2–4 pannelli, divisione diagonale) | renderizzata sul dispositivo dai ritratti privati già approvati (`tvaRit`), senza salvare derivati; senza ritratti resta l'emblema. Elenco varianti dal dossier dell'hub (non inventato) |
| Universi | numero completo della Terra (fatto) + composizione dei ritratti dei suoi personaggi principali quando disponibili | per gli universi senza numerazione documentata: denominazione esistente, nessun numero inventato |
| Attori | foto del profilo TMDB nelle sole schede interpreti | TMDB `profile`, privata, attribuzione |
| Luoghi, pianeti, artefatti, eventi, organizzazioni | scena TMDB più pertinente dai titoli in cui compaiono (stessa pipeline con prompt = nome + tipo) | filtri sui titoli dell'elenco apparizioni; soglia minima di margine, altrimenti **nessuna immagine** (mai iniziali o archetipi ripetuti): resta l'illustrazione originale specifica per tipo, da progettare per categoria |
| Mantelli | ritratti dei titolari (composizione come gli hub) | idem hub |

## 6. Prototipo: misure
Vedi `data/atlante/engine/CONFRONTO.md` (numeri aggiornati a ogni esecuzione). Sintesi a fine documento (§8).

### Precisione: cosa è misurabile e cosa no
- **Misurato oggettivamente** (nessun giudizio umano): riduzione dei candidati; tempo e risorse; accordo CLIP/SigLIP; confusioni tra identità (scene proposte a più identità); rispetto dei vincoli (titoli condivisi esclusi, ≥3 proposte, ritaglio 3:4 valido).
- **Non misurabile dalla sandbox**: la correttezza visiva (la scena mostra davvero il personaggio/variante giusta). La sandbox non può scaricare gli artifact con le miniature né vedere i pesi: il giudizio è tuo. **Protocollo**: per ciascuna delle 10 identità apri «Proposte automatiche» e approva; il rango dell'approvata (`scena.rk`) e gli eventuali rifiuti (scelta manuale) danno recall@k e precisione@k reali. Soglia di successo proposta: la tua scelta cade nelle prime 5 per **≥ 8 identità su 10** e nelle prime 3 per ≥ 6 su 10. Se non raggiunta: restano i soli filtri duri (riduzione ~97 % verso un elenco di 3–5 per metadati/qualità) e il motore si usa come ordinamento di aiuto.

## 7. Costo, risorse e scalabilità
- **0 €**: repository pubblico → minuti di GitHub Actions gratuiti; modelli open source; nessuna API a pagamento (la chiave TMDB gratuita resta nei Secret).
- Risorse misurate sul runner (4 CPU, ~16 GB): vedi §8. Stima per le 296 identità: lineare nel numero di candidati (≈ 3,1 s di CPU per identità nel solo punteggio, dominato dal ritaglio a finestre sulle prime 12 scene). Esecuzione a lotti da 30–50 identità per restare sotto i limiti di durata del job; nessun costo.
- Persistenza: nessuna immagine nel repository; l'unico stato è `proposte.json` (≈ poche decine di KB per 10 identità).

## 8. Esito del prototipo
Eseguito su GitHub Actions (CPU, 4 core, 0 €) sulle sole 10 identità del pilota.

| | CLIP ViT-B/32 | SigLIP ViT-B/16 |
|---|---|---|
| Candidati → proposte | 1272 → 44 (–96,5 %) | 1272 → 41 (–96,8 %) |
| Proposte per identità | 4–5 | 3–5 |
| Tempo totale | 6,3 min | 13,4 min |
| RAM di picco | 1,8 GB | 2,2 GB |
| Stadio dominante | ritaglio a finestre (77 %) | ritaglio a finestre (80 %) |
| Immagini proposte a due identità diverse | 0 | 0 |

- **Accordo CLIP/SigLIP**: sui titoli alto (per ogni identità i due modelli pescano dagli stessi 2–3 titoli, salvo Wanda e Deadpool con un titolo diverso); sulle singole immagini 41 % (molte scene sono quasi equivalenti). Le 44 proposte pubblicate al selettore sono quelle CLIP; **17 sono segnate ★ perché confermate anche da SigLIP**.
- **Esclusioni di continuità funzionanti**: per i tre Peter Parker il titolo condiviso N°099 è stato escluso dall'automatico.
- **Punto debole osservato**: Thanos, titolo N°089, margine di riconoscibilità basso (0,9–1,8 contro 6–15 delle altre identità): probabile scena senza Thanos in primo piano; da rivedere con attenzione.
- **Difetti trovati e corretti nel prototipo**: probabilità softmax saturata a 1,0 (sostituita dal margine log-odds); meno di 3 proposte con SigLIP (aggiunto il riempimento fino a 3).
- **Precisione visiva: non verificata**. Non ho potuto vedere le miniature (gli artifact non sono scaricabili dalla sandbox). Va misurata con le tue approvazioni (§6): non dichiaro il prototipo riuscito finché non lo approvi.
- **Fattibilità sulle 296 identità (stima, non eseguita)**: tempo lineare nel numero di candidati; ≈ 38 s/identità con CLIP e ≈ 80 s/identità con SigLIP sul runner (stima da 10 identità), cioè circa 3–7 ore a lotti. Costo 0 € (minuti gratuiti per repository pubblico), nessun archivio di immagini. **Non avviato: serve la tua approvazione dopo il collaudo.**
