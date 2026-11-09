# TVA FRIENDS — report (build 20261109-2030-friends, copia di lavoro; NESSUN commit/push/deploy; Firebase NON toccato)

## Analisi iniziale e dipendenze da F-A2/F-A3
- Gia' presenti: codici amico offline, gruppi, Live Room (`rooms/`), dati catalogo (titoli, anni, interpreti, livelli di potere, curiosita'), Centrale TVA > Operazioni.
- **Dipendenza locale da F-A2/F-A3: nessuna.** I dati Friends stanno in una chiave propria (`marvel-ultimate-timeline-tvafriends-v1`), fuori dal profilo sincronizzato: il motore sync, il backup profilo e TD2/Timeline/Atlante non sono toccati.
- **Dipendenza cloud:** account verificato (F-A2) + regole `users` e `friends` verificate su emulatore. Finche' non sono verificate: `CLOUD_ENABLED = false`.

## Architettura
Un unico bus di messaggi (`TVA1.<base64url>.<checksum>`) con due trasporti: **manuale** (copia/incolla, file `.tvafriends`, Condividi) attivo ora, **cloud** (`inbox/{uid}`) pronto ma spento. I 7 moduli poggiano sui messaggi. Ricezione con whitelist di campi, limiti di lunghezza, anti-replay, testo mostrato solo come testo (nessun innerHTML/eval).

## Funzionalita' (tutte attive in locale)
1. **Varianti**: nome, emblema, colore, motto, universo e personaggio preferiti (dal catalogo), anteprima esatta di cio' che vedono i collegati, flag per campo (default: solo nome ed emblema + numero Variante), backup/ripristino dei dati Friends.
2. **Legame Nexus**: invito → accettazione → risposta, a doppio consenso, nonce monouso con scadenza 14 giorni; scollega, blocca/sblocca; risposte non attese o false rifiutate.
3. **Squadre TVA**: squadra con obiettivo comune, inviti ai soli collegati, ingresso con consenso, avanzamento condiviso SOLO su azione esplicita (invia solo il conteggio dei titoli visti), il capo gestisce i membri, nessuno puo' alterare i dati di un altro, registro attivita'.
4. **Serate Marvel**: creazione con titolo del catalogo, data, luogo, invitati; inviti, risposte (si'/forse/no), annullamento, promemoria <24 h, esportazione `.ics`.
5. **Quiz e Duelli**: domande generate dal catalogo (anno di uscita, primo uscito, interprete, livello di potere, curiosita'); quiz singolo 5/10/15; duelli asincroni con stesso seme e impronta anti-versioni-diverse, classifica per punteggio e tempo, risultati validati. Non cambia XP/badge/progressi.
6. **Archivio condiviso**: pacchetti di titoli scelti (max 12) o ordine Timeline personalizzato (con conferma); il ricevente li vede in sola lettura con "gia' visto" calcolato solo in locale. Whitelist rigida: mai Diario/note/voti/preferiti/progressi.
7. **Centro Comunicazioni**: notifiche e attivita' (Nexus, squadre, serate, duelli, pacchetti), non letti con badge, filtri, promemoria; solo in-app, nessuna push.
Ingresso: Centrale TVA > Operazioni > «TVA Friends» (nessuna modifica al resto della Centrale).

## Cloud (pronto, DISATTIVATO)
`handles/{vid}→uid`, `profiles/{uid}`, `links/{uid}`, `blocked/{uid}`, `inbox/{uid}/{id}`. Regole proposte in `firebase/rules.friends.proposed.json` (NON applicate): solo email verificata; mittente = uid autenticato; messaggi create-only; inbox leggibile/cancellabile solo dal proprietario; non collegati possono inviare solo inviti/risposte Nexus; blocchi; codice ≤ 24000 car. e formato verificato.
Limite noto: chiunque sia verificato puo' inviare inviti a chiunque (spam di inviti); mitigazione = blocco da parte del destinatario; nessun rate limit possibile con le sole regole RTDB.

## Test
Vedi tabella risultati sotto (aggiornata a fine regressione).

## Da attivare / restano
- Eseguire `firebase/emulator` (aggiungere `rules.friends.proposed.json` al merge) sul tuo PC; poi, con tua autorizzazione, pubblicare le regole (users + friends) e impostare `CLOUD_ENABLED = true`.
- Prova su iPhone reale (layout/tastiera/Condividi/file) e con due persone vere.
- Sicurezza cloud NON verificata finche' non gira l'emulatore.
- I dati Friends non sono nel profilo sincronizzato: restano su ogni dispositivo (backup Friends manuale); la loro sincronizzazione per account e' una scelta futura.

## Risultati dei test (build 20261109-2030-friends)
| Suite | Esito |
|---|---|
| friends_test — 7 moduli, 2-3 dispositivi simulati, codici reali, privacy, offline, errori, backup | PASS 86/86 |
| friends_cloud_test — trasporto cloud con SDK MOCK + DB SIMULATO (regole proposte) | PASS 26/26 |
| friends_rules_test — regole friends+users+rooms/sync sul SIMULATORE (7 mutazioni testate) | PASS 40/40 |
| fa2_test / fa2_rules_test (F-A2/F-A3) | PASS 69 / 54 |
| Regressione completa 65 suite | PASS 43 · FAIL 6 (storici: b32, bl, cron3c, fx_test4, fy, ui_audit) · BLOCKED 6 (storici: cons, cop, f3, fx_test2, nav, net) · NOT RUN 10 (dipendenze esterne) — nessun nuovo FAIL (m32 aggiornato al nuovo id build: PASS) |
| BLOCKED | emulatore Firebase, SDK reale, regole su Firebase reale, iPhone reale, due persone reali |
Correzioni emerse dai test: anteprima Variante non si aggiornava con i flag; l'accettazione Nexus via cloud era bloccata dalle regole (ora `nx.accept` e' marcata come handshake); mock senza `remove`; messaggio "salvata" sovrascriveva l'errore di spazio pieno.
