# Miss Minutes 2.0 — fase C.1 (consolidamento di intelligenza e affidabilità)

Data: 27/11/2026 · build `20261127-1200-mm2e` · solo TEST, produzione congelata, A5 sospesa, budget 0 €.

## Stato onesto
- **Il JSON integrale della valutazione reale NON è arrivato in questa sessione** (nessun allegato leggibile). Quindi **il punto 1 (revisione integrale delle 81 risposte) NON è stato eseguito** e il **report comparativo prima/dopo con dati reali non è ancora producibile**: non ho inventato nulla sulle risposte che non ho letto. Prima: restano solo i tuoi numeri riassuntivi (74 corrette, 2 incerte, 5 sbagliate, 79/81 online, 58/81 con fonti, TTFB 805 ms, mediana 9,8 s, p90 23,8 s).
- Gli interventi sotto derivano dai difetti che hai **nominato** (mcu07, Fantastic Four: First Steps, avvisi su Brand New Day, fal03, note «non lo riporto», UI) e dall'analisi del codice, in forma **generale** (nessuna eccezione per titolo).
- **L'obiettivo ≥ 95 % di accuratezza fattuale verificata non è dimostrato**: si misura solo rieseguendo la valutazione e rivedendo a mano i casi dubbi.

## Interventi (per punto della richiesta)
**2 · Sistema temporale**
- Lo stato di uscita **non si deduce più dalla data trascorsa**: viene dallo stato TMDB (Released/Ended/… = uscito; Planned/Post Production/In Production = non uscito). Senza stato (es. N°125, ancora senza voce TMDB) i fatti dicono che l'uscita effettiva non è confermata e il verificatore **non blocca** né l'una né l'altra affermazione. Una data futura documentata resta indizio di «non ancora uscito».
- Date regionali: nei fatti IT/US/altri mercati dall'archivio; il verificatore conosce tutte le date regionali, quindi **niente più falso avviso** quando la risposta cita la data italiana (29/07/2026) invece di quella Timeline (31/07/2026). La nota residua è naturale («Per «X» in archivio risultano queste date: …»), non più la formula «le uscite variano per paese, verifica la fonte».
- Negazioni e riferimenti: «non è ancora uscito» non conta come «è uscito»; frasi su seguiti/spin-off/prossima stagione non giudicano il titolo in discussione; «non è uscito prima di luglio» non è una negazione di esistenza.
- Prompt del gateway: distinzione esplicita tra data odierna, data di uscita (prima Italia poi USA, mercato dichiarato), ambientazione narrativa, pubblicazione editoriale; i fatti vincono sulla memoria obsoleta (**richiede ridistribuzione del gateway**).

**3 · Intento**
- mcu07: le intenzioni personali (statistiche, consigli, voti, amici, giochi…) ora richiedono un riferimento a chi parla o all'app («ho», «mi», «tessera», «TVA Live»…) oppure un comando brevissimo; «Quanti film compongono la Saga dell'Infinito?» va all'AI online. Test: 3 casi.
- Spoiler: richiesta esplicita («spoiler», «chi muore», «come finisce», «alla fine di…») consente gli spoiler **solo per quella domanda**; la preferenza generale resta.
- Soggetto dei seguiti: il titolo in discussione si cerca nelle ultime 4 domande dell'utente (non solo l'ultima).
- Film/serie/animazione/fumetti: già coperto dal verificatore (formato/omonimia); aggiunte 4 domande di validazione dedicate.

**4 · Verificatore** — controlli per frase con negazioni e riferimenti temporali (sopra); quando una frase contraddice un dato documentato, **non resta un'affermazione errata seguita da una nota**: la frase non viene mostrata e viene sostituita da una correzione composta dai dati documentati («Su questo punto mi attengo ai dati documentati: «X» è un film già uscito: in Italia dal …»). Per attore/continuità senza dato: «non ho una conferma abbastanza solida, quindi preferisco non darti un'informazione che potrebbe essere sbagliata». Il superamento dei controlli non è più presentato come verifica.

**5 · Fonti** — una fonte compare solo se **supporta** la risposta (condivide date/anni/nomi propri con il testo) oltre a essere pertinente al titolo; ordinata per autorevolezza (ufficiale > archivio app > TMDB > Wikipedia); niente Wikidata, niente date di consultazione, niente URL del modello.

**6 · Naturalezza** — prompt: niente formule di sistema, niente «non è una conferma ufficiale» ripetuto, continuità citate solo se servono, incertezza una volta e con parole naturali; nei fatti rimossa la parentesi «(TMDB non è una conferma ufficiale)» che il modello ripeteva (**richiede ridistribuzione del gateway per la parte di prompt**).

**8 · Interfaccia** — sotto le risposte non compaiono più elenco fonti, date, «Wikipedia non ufficiale/Wikidata», la scritta «online · AI · controlli automatici… spoiler non garantiti», né note tecniche; resta il pulsante discreto **«Fonti»** accanto a Copia/Ascolta (si apre solo su richiesta). Restano visibili solo gli stati che l'utente deve conoscere (risposta locale, parziale, interrotta). Avvisi generali sull'AI invariati in Impostazioni/Informazioni. Le incertezze rilevanti passano nel testo (fatto «lacuna» per rete assente, stato non verificato). Tutti i controlli restano attivi internamente.

**7 · Valutatore (v2)** — fal03: la smentita della premessa falsa è corretta con **qualunque formulazione naturale** (prima serviva una regex rigida); nuove dimensioni: completezza, pertinenza (risposte troppo lunghe), naturalezza (marcatori tecnici), gestione dell'incertezza, fonti, nopers (domande generali non trattate come personali); **42 domande nuove (set V)** mai usate per sviluppare il sistema, su titoli e casi diversi (Fantastic Four: First Steps, date IT/US di Brand New Day, formato, spoiler, falsi presupposti, seguiti a 3 turni). Il runner ha il pulsante «Solo le domande nuove (validazione)».

## Come chiudere il confronto prima/dopo
1. Reinviami il JSON della valutazione reale (o salvalo come `miss-minutes/eval/prima.json`).
2. Ridistribuisci il gateway (workflow «Miss Minutes - gateway», commit scheduler `1846ea0`), installa la build mm2e.
3. Esegui in app «Valutazione risposte» → completa (123 domande) → «Salva il file JSON».
4. `python3 tools/mm_eval_report.py --confronta prima.json dopo.json --md docs/MISS_MINUTES_2_0_FASE_C1_CONFRONTO.md` (stessi criteri v2 su entrambi; il giudizio manuale in `manuale.json` prevale).

## Verifiche eseguite qui
Vedi tabella nel registro di roadmap. Nessuna risposta reale di Gemini è stata verificata da me in questa fase.
