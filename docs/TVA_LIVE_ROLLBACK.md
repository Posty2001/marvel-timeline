# TVA Live - rilascio, rollback e recupero (procedure)

Nessuna di queste operazioni e stata eseguita: sono le procedure da usare dopo l autorizzazione al rilascio. Budget: 0 EUR/mese.

## 1. Cosa e accoppiato a cosa
- **App (Netlify)** e **catalogo (GitHub Pages)** sono indipendenti: l app accetta il catalogo remoto solo se schema 1, dimensioni e SHA-256 coincidono, la versione deriva dagli hash e `generated_at` non e piu vecchio di quello gia visto. Vince il piu recente tra remoto, copia salvata e dati inclusi.
- La produzione attuale (main 82a73c7) **non legge Pages** (la sua CSP non lo consente): per lei Pages e invisibile.
- Le build con Live (live4, live5, finale) leggono tutte lo stesso schema 1. I campi aggiunti dalla regola dei mercati (`officialDates`, `dateBasis`, `dateTMDB`) sono additivi: le build precedenti li ignorano e restano valide.
- Conclusione: **ripristinare Netlify non richiede nessuna azione su Pages** e non lascia versioni incompatibili. Pages cambia solo quando lo scheduler pubblica.

## 2. Rollback dell app (Netlify)
1. Netlify > Deploys > scegliere il deploy di produzione precedente > *Publish deploy* (oppure caricare di nuovo lo ZIP precedente).
2. Verificare da Safari: l app si apre, la data di build nelle Info e quella precedente (il service worker si aggiorna da solo al riavvio).
3. Dati personali: non vengono toccati (chiavi di storage separate; le nuove chiavi `live-*` e `episodes-v1` restano inerti nella build precedente).
4. Main su Git resta com era finche non si decide diversamente; se e stato avanzato, riportarlo a 82a73c7 solo con una decisione esplicita.

## 3. Catalogo remoto sbagliato ma valido (fermare lo scheduler NON basta)
Un catalogo gia pubblicato resta online e gia nella cache dei dispositivi. L app rifiuta qualunque catalogo piu vecchio di quello visto, quindi per sostituirlo serve un catalogo **piu recente**.
- **A. Correzione normale (preferita).** Correggere la causa (regola del generatore, oppure `exclude`/voce in `tools/live/manual.json`), poi eseguire `tmdb-sync` su `test/tva-archives` con `solo_live_build`, `live_commit`, `live_force` (solo se il cambio e bloccato dall anti-anomalie), quindi lo scheduler. Nuova versione con generated_at nuovo.
- **B. Recupero da una versione nota (emergenza).**
  1. Disattivare lo scheduler (repo `tva-live-scheduler` > Actions > TVA Live - scheduler > ... > Disable workflow): evita che rigeneri dati sbagliati.
  2. Individuare lo SHA buono: `git log --oneline -- assets/live/manifest.json` su `test/tva-archives` (o `catalog/c/<id>` nel repo scheduler).
  3. `tmdb-sync` (ref `test/tva-archives`): `live_recover_from=<sha>`, `live_commit=true`. Prima, volendo, con `live_dry_run=true`. Ripristina lo stesso contenuto con generated_at nuovo, rivalidato, solo i 4 file di `assets/live`.
  4. Scheduler: avvio manuale con `publish_only=true` (nessuna rigenerazione, controlla solo coerenza manifest/status e che main non sia cambiato). Deploy Pages come al solito.
  5. Verificare `current.json` (versione e generated_at nuovi) e, da iPhone online, la scheda Live ("aggiornamento online verificato").
  6. Correggere la causa, poi riattivare lo scheduler.
- **C. Disattivare Pages** (Settings > Pages > Unpublish) NON ritira il catalogo dai dispositivi che l hanno gia salvato: usare solo insieme a B.
Tempi: l app ricontrolla all apertura, al ritorno online e al rientro in primo piano (non piu di una volta ogni 30 minuti); Pages mette in cache il puntatore per circa 10 minuti.

## 4. Controllo dopo ogni rilascio o recupero
- `status.json` e `manifest.json` sul branch con lo stesso `content_hash`.
- Il puntatore pubblico ha `version` = id derivato dagli hash dei tre file; `generated_at` identico nei tre file.
- Doomsday: badge Provvisorio finche non esiste una fonte ufficiale per l Italia; date UK/USA nei dettagli.
- Primo cron (05:17 UTC): esito `unchanged`/`heartbeat`/`update` e `verify-endpoint` verde.
