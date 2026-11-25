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

- **Accordo CLIP/SigLIP**: sui titoli alto (per ogni identità i due modelli pescano in gran parte dagli stessi 2–3 titoli; titolo diverso in parte per Wanda, Deadpool e Raimi); sulle singole immagini 41 % (molte scene sono quasi equivalenti). Le 44 proposte pubblicate al selettore sono quelle CLIP; **17 sono segnate ★ perché confermate anche da SigLIP**.
- **Esclusioni di continuità funzionanti**: per i tre Peter Parker il titolo condiviso N°099 è stato escluso dall'automatico.
- **Punto debole osservato**: Thanos, titolo N°089, margine di riconoscibilità basso (0,9–1,8 contro 6–15 delle altre identità): probabile scena senza Thanos in primo piano; da rivedere con attenzione.
- **Difetti trovati e corretti nel prototipo**: probabilità softmax saturata a 1,0 (sostituita dal margine log-odds); meno di 3 proposte con SigLIP (aggiunto il riempimento fino a 3).
- **Precisione visiva: non verificata**. Non ho potuto vedere le miniature (gli artifact non sono scaricabili dalla sandbox). Va misurata con le tue approvazioni (§6): non dichiaro il prototipo riuscito finché non lo approvi.
- **Fattibilità sulle 296 identità (stima, non eseguita)**: tempo lineare nel numero di candidati; ≈ 38 s/identità con CLIP e ≈ 80 s/identità con SigLIP sul runner (stima da 10 identità), cioè circa 3–7 ore a lotti. Costo 0 € (minuti gratuiti per repository pubblico), nessun archivio di immagini. **Non avviato: serve la tua approvazione dopo il collaudo.**

## 8. Motore 2.0 – ondata 1 (40 identità) — 25/11/2026

**Cosa cambia rispetto al prototipo.** Il punteggio principale è quello del *ritaglio 3:4* (ciò che il ritratto mostrerà davvero), non della scena intera: finestre a due scale con ricerca della posizione migliore, altezza minima del ritaglio 700 px sull'originale. Ensemble CLIP (ritagli) + SigLIP (scena intera; `ck`=★ se entrambi sopra soglia). Contrasto con tutte le identità dell'ondata e con 10 negativi (gruppo di eroi, folla, testo/logo, volto senza costume, veicoli, esplosioni, scene buie…): premia personaggio isolato e costume iconico. Qualità: nitidezza, esposizione, risoluzione del ritaglio. Varianti e continuità: solo titoli verificati della continuità dell'identità; titoli ambigui tra varianti della stessa famiglia (es. N°099 per i tre Peter Parker) esclusi dall'automatico; una scena non viene mai proposta a due identità (assegnata a quella con margine maggiore). Diversità: massimo 2 ritagli per titolo (poi 3–4 se mancano), niente quasi-duplicati (hash e coseno > 0,94).

**Confidenza.** Se almeno 3 ritagli superano la soglia: confidenza *alta*, 3–5 proposte; altrimenti *bassa*, fino a 10 proposte (segnalata nell'app).

**Risultati dell'ondata (metadati in `data/atlante/engine/metriche2_w1.json`).** 40 identità, 5606 scene candidate → 2003 immagini uniche → 1980 nitide; 202 proposte; confidenza alta 32, bassa 8 (Bucky, Nebula, Drax, Rhodey, Magneto, Reed, Ben Grimm, Harry Osborn). Tempo totale 20,5 min su 4 CPU del runner gratuito (download 3,2 min, CLIP 1,7 min, SigLIP 6,2 min, resto ritagli), RAM di picco 3,1 GB. Costo 0 €. Nessun riconoscimento facciale; immagini scartate a fine job.

**Precisione: non misurabile dalla sandbox.** Va misurata con le tue approvazioni: ogni ritratto salvato da proposta registra `scena.rk` (posizione) e `scena.sc`. Da *Ritratti privati* → «Esporta valutazioni (solo metadati)» ottieni recall: proposta n.1, entro la 3ª, 5ª, 10ª e quante scelte manuali. Soglia suggerita per estendere alle 296: ≥ 70 % entro la 3ª proposta sulle identità con confidenza alta e < 25 % di scelte manuali. **Non si estende senza la tua approvazione.**

**Revisione rapida consecutiva.** *Ritratti privati* → «Revisione rapida…»: coda delle sole identità senza ritratto; per ciascuna anteprima 3:4, ✓ Approva (un tocco), Altra proposta, Salta, Editor manuale; contatore e riepilogo finale. Controlli al momento della scrittura: un ritratto già salvato non viene **mai** sovrascritto (neppure se compare mentre approvi); una scena già usata da un'altra identità non viene salvata (passa alla proposta successiva). Test: `tests/a33_test.py` (12/12).

**Altre categorie.** Universi, hub, mantelli, artefatti, organizzazioni, luoghi, pianeti ed eventi hanno emblemi procedurali originali e deterministici (nessuna iniziale come soluzione finale; nessuna immagine protetta). Gli hub potranno comporre i ritratti delle varianti (solo progetto, non implementato).

## 9. Estensione a tutte le 296 identità — 25/11/2026 (dopo il collaudo approvato)

**Esito del collaudo (dati dell'utente).** 38 valutazioni: 34 da proposta (89,5 %), 4 scene scelte a mano, 30 entro la 3ª proposta (78,9 %), 26/31 sulle identità ad alta confidenza (83,9 %): soglie (≥ 70 % e < 25 % manuali) superate; estensione autorizzata.

**38 invece di 39.** L'esportazione v1 elencava solo i ritratti con una *scena TMDB* registrata (`r.scena`). I ritratti creati con «Importa da foto o file» non hanno scena e venivano omessi: è la spiegazione più probabile del 39° (34 da proposta + 4 scene manuali = 38 + 1 da file locale). Non è una perdita di dati: il ritratto è nell'archivio. L'esportazione v2 elenca **tutti** i ritratti con `origine` (`proposta` / `scena-manuale` / `file-locale`) e i conteggi `totale`, `file_locali`, `scene_manuali`: riesportando dovresti leggere 39.

**Harry Osborn.** Il pool conteneva titoli di altre continuità (N°005 Garfield e N°120 serie animata) mescolati ai Raimi. Ora ogni identità usa solo i titoli della *continuità del suo universo principale* (Parte/saga dell'universo dal registro: 1A, 1B, …, Canone). Per Harry: solo N°001–003 (Raimi-Verse), ricerca ampliata (fino a 120 scene per titolo, 349 candidate), 3 prompt (Goblin con aliante, Harry in giacca, New Goblin), immagini taggate con l'interprete se presenti. Esito: 5 proposte, confidenza alta. **Nota di dati (non applicata):** l'identità unica «Harry Osborn/Green Goblin» elenca anche N°005 (Garfield, interprete diverso) e N°120; separarla in due identità è una decisione di identità che spetta a te. Altre identità con titoli esclusi dal filtro: elenco in `waveall.json` (`esclusi_continuita`). Se per un'identità nessun titolo appartiene alla continuità principale non si filtra (segnalato nei dati).

**Pipeline a blocchi riprendibili.** `tools/atlante_w.py --meta-all` (296 identità, 250 elaborabili con titoli TMDB verificati, 13 senza titoli) → candidati TMDB (solo metadati, riprendibile, saltando i file già presenti) → `engine2-tutte`: 9 blocchi da 30; ogni blocco è salvato a parte (`data/atlante/engine/blocchi/b*.json`) e i blocchi già presenti vengono saltati al rilancio; limite di tempo del job (95 min) con arresto ordinato. Una scena non è mai proposta a due identità neppure tra blocchi. Le immagini scaricate nel runner sono cancellate a fine blocco.

**Prompt e confidenza.** 174 identità hanno un prompt descrittivo (costume/tratto iconico; ipotesi di lavoro, non dati Atlante); 82 hanno solo il nome e usano una soglia più prudente (2,5 invece di 5,0), **non ancora calibrata**: la misureremo con le tue approvazioni, separando le classi (`gen` nei metadati). Confidenza alta: 3–5 proposte (90 identità); bassa: fino a 10 (189 identità, quasi tutte a 10); 17 identità senza proposte (13 senza titoli TMDB e 4 senza scene idonee): restano all'emblema/import manuale.

**Risorse (0 €).** 9 blocchi, circa 93 min di CPU totali su runner gratuito, RAM di picco ≈ 3 GB, 16.898 scene candidate → 10.617 immagini uniche analizzate, 2.072 proposte. Nessun riconoscimento facciale; nessuna immagine nel repository, nello ZIP o sul sito (solo percorsi CDN TMDB).

**App.** Contatore «completati / mancanti» in Ritratti privati, nella revisione rapida e nel catalogo Personaggi; filtro «Solo senza ritratto» (catalogo e gestione); revisione rapida su tutte le identità senza ritratto (mai sovrascrive); composizione degli hub e dei mantelli con i ritratti salvati delle varianti/titolari (fino a 4; se non ce ne sono resta l'emblema originale). Test: `tests/a34_test.py` (9/9).

**Misura della precisione.** Da *Ritratti privati* → «Esporta valutazioni (solo metadati)»: recall per posizione (prima, entro 3ª/5ª/10ª) e quota di scelte manuali; con la classe di confidenza (`conf`, `gen`) potrò tarare le soglie.
