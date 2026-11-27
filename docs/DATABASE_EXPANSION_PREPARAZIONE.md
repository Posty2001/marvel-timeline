# Preparazione alla fase «Database Expansion» — NON AVVIATA

Documento di passaggio (27/11/2026). Nessun lavoro della fase è stato iniziato; serve l'autorizzazione esplicita dell'utente e la definizione dell'ambito (non inventato qui).

## Stato di partenza verificato nel codice
- Registro dati Atlas: `data/atlante/` (identità, relazioni, lotti, `_verifiche.json`), strumenti `tools/atlante_*.py` con `--verifica`; dati runtime lazy in `atlante2/data/` (index 452 voci, shard dossier, `nexus/g.json`).
- Identità: 315 personaggi (298+ separati per continuità, nessuna unificazione di persone distinte); hub 3, mantelli 2; ID e chiavi `tva-atlante-*` immutabili.
- Relazioni: 245 narrative (207 con fonte, 4 guida, 34 da verificare), 1026 editoriali, 5 controparti; co-apparizioni ≠ relazioni.
- Archivio titoli Miss Minutes: 136/138 (mancano N°077 e N°125, nessun ID inventato).

## Punti aperti da decidere con l'utente prima di iniziare
1. Ambito: quali tabelle/registri espandere (identità, relazioni, titoli, attori, universi) e priorità.
2. Obiettivo relazioni narrative (500 non raggiunto, non prerequisito): confermare o ridefinire.
3. N°077 e N°125: fonte per completare l'archivio.
4. Discrepanza Johnny Storm N°117 (segnalata in a43).
5. 34 relazioni «da verificare»: criterio di promozione/scarto.
6. Ritratti: compilazione ancora aperta (immagini private, mai nel repository).
7. Regole XP per le nuove voci: i totali di badge/progressione crescono con il database (i badge ottenuti non si revocano).

## Vincoli permanenti
Solo `test/tva-archives`; produzione congelata; 0 €; nessuna perdita di dati personali; nessun dato inventato; nessun servizio a pagamento; Miss Minutes congelata.
