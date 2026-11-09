# F-A2 + F-A3 — piano tecnico (sintesi)

## Analisi di ciò che esiste (riutilizzo)
- **Motore sync 4.0C/4.0E** (blocco `SYNC40C`): profilo = UNA stringa JSON (`PROFILE_OBJ_KEYS/PROFILE_STR_KEYS`), barriera di inizializzazione, confronto stabile, stati reali (connecting/synced/auth/offline/conflict), retry limitati, conflitto con scelta esplicita, ripristino transazionale con copia di sicurezza (`sostituisciProfilo`). Oggi punta a `sync/<codice>` (codice condiviso = nessuna identità; regole utente solo su `rooms`, quindi probabilmente non funzionante). **Riuso integrale**: cambia solo il percorso, la scrittura e le regole di sicurezza.
- **F-A1** (account email/password, verifica email): fornisce uid ed `emailVerified`. Nessun dato era collegato all'account.
- `rooms/*` (Live Room) e `sync/*` restano **invariati**; il codice-sync resta disponibile (storico), mutuamente esclusivo con la sync account.
- Non esistono: regole `users/{uid}`, versioning, backup cloud, proprietà locale del profilo.

## Schema dati (nuovo, additivo)
```
users/{uid}/profile      string JSON (formato/validazione 4.0C, max 5 MB)
users/{uid}/meta         {schema:1, rev:n, updatedAt:ServerValue.TIMESTAMP, device}
users/{uid}/backups/{id} {at, device, size, sha256, reason, profile}   (create-only, ultimi 5)
```
Locale (additivo, fuori dal profilo/export/sync): `…-profile-owner` (uid proprietario dei dati locali), `…-acct-sync` ({uid,on}), `…-device-id`.
**TVA Friends (solo architettura, nessuna funzione):** nodo `users/{uid}` ha `$other:false` → nessun dato pubblico oggi. Futuro: `profiles/{uid}` (profilo pubblico minimo, scrittura solo dal proprietario, lettura solo autenticati/amici), `variants/{variantId}→uid` (indice), `links/{pairId}`, `inbox/{uid}`; mai il Diario/ note/voti; ogni condivisione = opt-in esplicito per campo.

## Regole di sicurezza (PROPOSTE, non applicate) — `firebase/rules.users.proposed.json`
Solo il proprietario (`auth.uid == $uid`) **con email verificata** legge/scrive; nessun accesso a `users` radice (niente enumerazione); `$other:false`; stringa profilo ≤ 5 MB; **CAS**: scrivere un profilo diverso richiede `meta/rev = rev_precedente + 1` (un dispositivo con dati obsoleti viene rifiutato, mai sovrascrive in silenzio); `updatedAt = now`; backup create-only (non sovrascrivibili), cancellabili solo dal proprietario.

## Migrazione sicura (nessuna cancellazione)
1. Sync account **mai automatica la prima volta**: pulsante «Attiva» + conferma con conteggi.
2. Dati locali senza proprietario + cloud vuoto → conferma → upload (rev 1) + backup cloud «migrazione»; locale intatto.
3. Cloud ≠ locale → **conflitto** con scelte esplicite: mantieni locale (sync spenta) · differenze · ripristina dal cloud (copia di sicurezza locale) · **usa questo dispositivo** (prima backup cloud del contenuto sostituito + conferma).
4. Locale appartenente ad **altro account**: mai caricato nel nuovo account; solo «sostituisci con i dati del tuo account» (copia di sicurezza locale) o annulla.
5. Cloud mai applicato in automatico: se il locale non è cambiato dall'ultima sync appare «Aggiornamento da un altro dispositivo» con bottone Applica.

## Offline / dispositivi
Il locale resta la fonte primaria (offline pieno). Modifiche in coda inviate dal ciclo di sync; `online`/visibilità riavviano i tentativi; stato «N non sincronizzato» onesto; CAS risolve cambi di dispositivo e scritture concorrenti.

## Backup e ripristino verificabili
Backup cloud (SHA-256 + dimensione) manuale, prima di ogni sostituzione del cloud e alla migrazione; «Verifica» rilegge e ricalcola hash + `normalizzaProfilo`; «Ripristina» = copia di sicurezza locale + validazione + sync. Export/import file esistenti invariati.

## Test
Valutatore regole RTDB simulato (Node) + matrice autorizzazioni; mock database con regole per test end-to-end Playwright a due dispositivi/due account; regressione completa. **Limite:** emulatore Firebase/SDK reale non raggiungibili da qui (rete) → test regole su emulatore e SDK reale = BLOCKED.
