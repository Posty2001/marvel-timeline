# Database Expansion — sistema incrementale e ritratti (W7 Final, build db8)

## 1. Come continuare ad ampliare il database dopo la chiusura della macro-fase
Tutto è riprendibile e additivo: gli ID del registro (`data/atlante/espansione/ids_registro.json`) sono append-only e non cambiano mai.

| Passo | Comando (da `/home/claude/marvel-timeline`, branch `test/tva-archives`) |
|---|---|
| Raccolta narrativa W8 (artefatti, specie, eventi, entità cosmiche, universi) | `gh workflow run tmdb-sync.yml -R Posty2001/marvel-timeline --ref test/tva-archives -f db_w8=true -f solo_episodi=false` |
| Comic Vine (voci, extra, relazioni; riprende dal checkpoint, 305 personaggi di relazioni ancora da recuperare) | `... -f db_w5c=true -f solo_episodi=false` |
| Pagine Marvel Database con infobox | `... -f db_cvmd=true -f solo_episodi=false` |
| Relazioni Wikidata e verifica | `... -f db_rel=true -f db_relv=true -f solo_episodi=false` |
| Scarico risultati | `git fetch origin db-raw` e `git show origin/db-raw:<file>` in `data/atlante/espansione/raw/` |
| Costruzione canon/staging | `tools/db_w8_build.py`, `tools/db_cv_espandi.py --scrivi` (parametri di categoria in `w8_config.json`) |
| **Ricostruzione dei derivati (un solo comando)** | `python3 tools/db_ricostruisci.py` (ID → dossier/livelli → indice runtime → `rel.json` → archivio Miss Minutes → conteggi → candidati ritratti) |
| Verifica | `python3 tools/db_ricostruisci.py --verifica`, `python3 tests/db_integrazione_test.py`, `python3 tests/db_w8_test.py` |

Guardie: lo script si ferma se il registro ID perde ID rispetto a `HEAD` (gli ID rimossi devono diventare lapidi). Il passo runtime cancella `atlante2/data/db/`, quindi `rel.json` va sempre rigenerato dopo (lo script lo fa nell'ordine corretto).

**Regola D12 per le nuove voci**: una voce entra nel canon solo con due fonti indipendenti (Wikidata con collegamento Marvel, oppure nome esatto su Comic Vine nella risorsa coerente); altrimenti resta in `staging/*.jsonl` con il motivo («una sola fonte»). Revisione dello staging: aprire `staging/w8_staging.jsonl`, per i candidati con una seconda fonte reale aggiungere l'abbinamento (`cv_match.json` o QID) e rilanciare la costruzione; mai promuovere a mano senza fonte.

**Dove mancano ancora dati (limiti documentati, nessuna forzatura)**
- Varianti: 2.691 in staging (una sola fonte). Servirebbe una decisione dell'utente su una deroga D12, altrimenti restano in attesa.
- Universi/dimensioni: 4.123 pagine «Earth-N» in staging; nessuna seconda fonte gratuita indipendente.
- Eventi/saghe: 1.391 in staging.
- Relazioni: 8.390 narrative documentate, di cui 993 verificate; il campo `metodo` distingue verifica automatica da documentale.

## 2. Ritratti per le nuove identità — soluzione sostenibile e conforme
**Stato.** I ritratti approvati dall'utente restano intatti (IndexedDB privato `tva-atlante-ritratti`, mai nel repository, nello ZIP o nel deploy). La pipeline privata esistente (`atlante2/ritratti.js`) già permette, per **qualsiasi** identità del database esteso:
1. **Importa da foto o file** dal dispositivo (iPhone/iPad), con ritaglio 3:4, salvato solo in locale;
2. selettore scene TMDB come riferimento privato (solo dove i termini lo consentono);
3. esporta/importa l'intero archivio dei ritratti (backup personale).

**Limite.** L'estensione *automatica* a nuove identità richiederebbe di archiviare o distribuire immagini/metadati TMDB, i cui termini di archiviazione non sono confermati (D-regola: nessun nuovo metadato TMDB archiviato), e nessuna fonte gratuita offre ritratti Marvel con licenza di ridistribuzione. Non si distribuiscono quindi immagini non autorizzate né si usano API a pagamento.
**Preparato.** `data/atlante/espansione/ritratti_candidati.json`: 516 identità prioritarie (solo metadati: id, nome, rilevanza; nessuna immagine), rigenerabile con `python3 tools/db_ritratti_prep.py --scrivi`; utile come lista di lavoro per l'import privato. Fino ad allora le nuove voci usano gli emblemi grafici originali già esistenti, mai presentati come ritratti.
**Possibile evoluzione (solo nota, non attivata)**: immagini con licenza libera verificata caso per caso (es. Wikimedia Commons) potrebbero essere proposte come candidate private, previa verifica della licenza di ogni file.
