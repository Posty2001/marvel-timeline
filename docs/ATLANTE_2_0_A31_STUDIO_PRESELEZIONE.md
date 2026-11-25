# A3.1 – Studio: preselezione intelligente delle scene (solo studio, nessuna implementazione)

Obiettivo: ridurre da centinaia a ~8 le scene da esaminare per identità, **senza** che l'automatismo scelga al posto tuo. Costo 0 €, nessuna chiave nel frontend, pilota non esteso.

## Limite di partenza
TMDB `tagged_images` restituisce solo locandine: non esiste un dato «questa scena contiene il personaggio X». L'attribuzione scena→identità non è ricavabile dai metadati; va stimata visivamente e **confermata da te**.

## Pipeline proposta (GitHub Actions, gratuito, solo metadati in uscita)
1. **Filtri duri sui metadati (deterministici, senza ML)**
   - il titolo deve appartenere alla continuità dell'identità (da registro A2 + `appearances`);
   - esclusi dall'auto-selezione i titoli condivisi tra varianti (es. *No Way Home*): vanno solo in revisione manuale esplicita;
   - risoluzione ≥ 1280 px; deduplica con hash percettivo.
2. **Punteggio visivo con modelli aperti gratuiti** (CLIP zero-shot, rilevatore di persone/volti *solo come conteggio e riquadro*):
   - prompt testuale dell'identità, in contrasto con le altre identità dello stesso titolo;
   - preferenza per scene a soggetto singolo, con riquadro che entra in un ritaglio 3:4 (un 3:4 da 16:9 conserva solo ~42 % della larghezza);
   - nitidezza/esposizione; ritaglio suggerito.
   - **Niente riconoscimento facciale degli attori** (dato biometrico, rischio privacy, non necessario).
3. **Uscita**: top-k (≈8) con punteggi e ritaglio suggerito, in `candidati.json`; scelta e conferma sempre manuali con un tocco.

## Salvaguardie di correttezza
- L'identità si decide dal filtro di continuità (passo 1), non dal punteggio visivo: il modello ordina soltanto.
- Varianti ambigue (stesso attore, universi diversi) restano a revisione manuale.
- L'avviso scena duplicata tra identità resta attivo.

## Costi e limiti
- Actions: repo pubblico = minuti gratuiti; CLIP-base su CPU ≈ secondi/immagine; per ~295 identità × ~100 scene restano nell'ordine di ore-CPU, da stimare sul pilota.
- Immagini scaricate solo nel runner, scartate a fine job; nel repo solo ID/punteggi/ritagli.
- **Non misurabile dalla sandbox** (niente rete né pesi): la qualità reale è ignota finché non gira su Actions.

## Validazione
Eseguire solo sulle 10 identità del pilota e misurare **recall@8** rispetto alle scene che sceglierai tu nel collaudo (verità di riferimento). Soglia proposta per procedere: la tua scelta è dentro il top-8 per ≥ 8 identità su 10. Se non raggiunta: restano i soli filtri duri (passo 1).

## Decisione richiesta
Autorizzare il prototipo di fattibilità sulle 10 identità del pilota (solo metadati, 0 €), **dopo** il tuo collaudo. Nessuna estensione alle 295 identità, A4 non avviata.
