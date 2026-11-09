# TVA ARCHIVES — Report TD2: pagina dettaglio immersiva

Build di lavoro: `20261107-1745-td2` (solo `/home/claude/work`; repository `marvel-timeline` fermo a `c9ed9b1`). **Nessun commit, push o deploy.**

## Come funziona (nessuna nuova architettura di routing)
- Il tocco sulla testata di una scheda film/serie non espande più la card: la **stessa scheda** (stessi nodi, stessi handler, stessi dati) passa a schermo intero (`position:fixed`, classe `.td-page`). Nella Timeline resta un segnaposto invisibile di pari altezza: posizione, filtri, ricerca e selezioni non cambiano.
- Navigazione = router esistente: `tvaPushNav` (snapshot filtri/scorrimento) + `tvaBack` + `popstate`. Tre micro-modifiche al router: `snapshot().td`, riapertura in `restore()`, esclusione della pagina da `anchorOf()`.
- La pagina è un overlay: `marvelChiudiOverlay` la chiude. I collegamenti verso un altro titolo (`tvaGo('item')`) restano nella pagina e "Indietro" torna al titolo precedente. I chip dei personaggi aprono l'Atlante e "Indietro" riapre la pagina.
- Nessuna barra inferiore (nascosta con `html.td-lock`), pulsante Indietro sticky 46 px con safe-area, Esc, focus intrappolato, `role=dialog aria-modal`.
- Dati: nessuna scrittura nuova, nessuna chiave nuova, nessuna migrazione. Il modulo non usa storage/rete/Firebase (verificato da analisi statica nel test).
- Locandina: solo quella già associata (TMDB/personalizzata già nell'app), come immagine e come sfondo sfumato via CSS; senza locandina, fallback a gradiente. Attribuzione TMDB mostrata.

## Contenuto della pagina
Testata (locandina, N°, titolo, anno, stato, voto personale, **Da vedere/Completato**, **Preferito**) → Info principali → **Diario TVA** → Personaggi in archivio → Approfondimenti (Trama/Curiosità/Dietro le quinte/Collegamenti) → Universo/Ambientazione → Guarda e File locale (o stato esplicito "non disponibile" per i 10 titoli senza azioni).

## Decisioni/limiti da conoscere
1. Entrano nella pagina i tocchi sulla Timeline. Chi arriva da Atlante/Centrale tramite `tvaGo('item')` mantiene il comportamento precedente (espansione nella Timeline), per non alterare le suite c2/b2/a2. Da decidere se unificare.
2. Se il titolo è nascosto (filtro/gruppo chiuso) si usa il comportamento precedente.
3. Diario: una nota per titolo, come richiesto (multi-nota solo in `PROPOSTA_DIARIO_TVA_MULTI_NOTA.md`). La pagina parte dall'anteprima della nota; lo stato aperto/chiuso originale viene ripristinato in chiusura.
4. Anteprima visiva 2: usata l'immagine allegata. Il voto mostrato è quello personale (non il "8,4/10" dell'immagine: non è un dato dell'app e non è stato inventato).
5. Tema chiaro/scuro: la pagina è sempre scura (cinematografica), con testi a contrasto ≥ 4.5:1 in entrambi i temi.

## m31_test
Cause: asserzione sulla struttura (`first=='detail-row'`) falliva perché da TD1 le righe dati sono in `.td-info`. La locandina non è nel pannello (parte sostanziale del test: invariata). Risolto adattando solo il selettore: la prima voce è ora la prima riga dentro `.td-info`; copertura invariata. Esito: 15/15.

## Test (Chromium + viewport emulati; nessun Safari/iPhone reale)
| Suite | Esito |
|---|---|
| `td2_test` (nuova) | **PASS 59 / FAIL 0** — apertura/chiusura, DOM identico dopo apertura+chiusura di **tutte le 139 schede**, scorrimento ripristinato (pulsante e gesto Indietro), filtri/ricerca conservati, note (lettura, modifica, conferma eliminazione, annulla), voto/visione/preferito dalla pagina, collegamenti personaggi/titoli e ritorno, film/serie/titoli senza azioni, offline, tastiera/focus, reduced-motion, 320/360/390/430 px senza overflow e target ≥ 44 px, contrasto ≥ 4.5:1 (tema scuro e chiaro), nessun errore JS/CSP |
| `td1_test`, `fa1_test`, `b2_test` (121/0), `m31_test` (15/15), c2/c3/c4/a2… | PASS |
| Giro completo `run_suites.py` (build td2) | **PASS 37 · FAIL 7 · BLOCKED 6 · NOT RUN 10** |
| FAIL documentati preesistenti (b32, bl, cron3c, fx_test4, fy, ui_audit) | invariati (6) |
| **FAIL nuovo: `m32_test` «secondo tap chiude»** | **Regressione attesa**: il test verifica la vecchia espansione in-place (secondo tocco sulla stessa scheda la chiude); ora il tocco apre la pagina a schermo intero e si chiude con Indietro. «tap sulla locandina apre» passa. Test NON modificato: proposta = sostituire il secondo tap con il pulsante Indietro (stessa copertura) — da approvare |
| BLOCKED (cons, cop, f3, fx_test2, nav, net) | invariati rispetto a TD1: errori/timeout del runner preesistenti |
| NOT RUN (10) | dipendenze esterne non incluse nel repo, come prima |

## BLOCKED / non verificato
Safari iOS reale, PWA installata, Dynamic Island/safe area reali (verificata solo la presenza di `env(safe-area-inset-*)`), gesto di bordo di iOS, scorrimento con barra indirizzi dinamica (`100dvh`).

## Collaudo su iPhone (dopo approvazione e pubblicazione)
1. Timeline → tocca un film: pagina a schermo intero, nessuna barra in basso, pulsante ‹ in alto a sinistra sotto la Dynamic Island.
2. Scorri la Timeline molto in basso, apri una scheda, torna con ‹ e con il gesto di bordo: stessa posizione, stessi filtri/ricerca.
3. Nella pagina: assegna un voto, segna Completato, Preferito; scrivi/modifica una nota; chiudi e verifica nella Timeline.
4. Tocca un personaggio → Atlante → Indietro: torna alla pagina. Da PWA installata ripeti 2.
5. Titoli lunghi, tastiera aperta (nota), ruota lo schermo, modalità offline, tema chiaro/scuro.

---
# CHIUSURA TD2 — build `20261108-1010-td2`

## Modifiche rispetto alla build approvata
- **Navigazione unificata (una sola implementazione `openPage`)**: Timeline, Atlante («Scheda in guida»), Centrale TVA, collegamenti tra titoli (`mvNavigateTo` → `tvaGo('item')`) e titoli nascosti da filtri/universo aprono la stessa pagina immersiva. Per i titoli nascosti si azzerano solo i filtri responsabili (come faceva il router) e **Indietro li ripristina**. Il numero opera dentro l'Atlante continua ad aprire il Dossier Opera (comportamento proprio dell'Atlante); «Scheda in guida» apre la pagina.
- Safe area tramite le variabili dell'app `--sat/--sab/--sal/--sar` (+ `env()`), anche laterali.
- Nessuna modifica a dati, Firebase, regole, formato storage, Registro Master.

## Test adattati (solo dove il comportamento atteso è cambiato; nessuna verifica eliminata)
| Test | Cosa è cambiato |
|---|---|
| `m32_test` | «secondo tap chiude» → «pagina aperta» + «Indietro chiude» (stesse verifiche di apertura/chiusura) |
| `tva_test` D1–D3 | dopo «Scheda in guida»: pagina immersiva aperta, barra app nascosta (per progetto), Indietro = pulsante della pagina; poi ritorno al dossier invariato |
| `a2_test`, `f4b_test`, `cons_test`, `net_test` | clic su Indietro dal titolo = pulsante ‹ della pagina (se presente) altrimenti chip; «scheda visibile/aperta» accetta la pagina immersiva |
| `ui_audit` | misura del pulsante Indietro sulla pagina: ≥ 44 px, dentro safe area laterali e superiore (6 viewport) |
| `m31_test` | (già comunicato) prima riga dati dentro `.td-info` |
| `td2_test` | +8 verifiche di navigazione unificata (nascosto dai filtri, link tra titoli, Atlante, Centrale, Indietro con stato) → **67 PASS** |
`c2_test` e `b2_test` non hanno richiesto modifiche (PASS).

## Regressione completa (`run_suites.py`, build td2 finale)
**PASS 38 · FAIL storici 6 · FAIL nuovi 0 · BLOCKED 6 · NOT RUN 10** (60 suite)
- FAIL storici documentati (invariati): b32, bl, cron3c, fx_test4, fy, ui_audit (contrasto `.ud-st-ok` 4.4).
- BLOCKED (invariati dalla build TD1 e precedenti, errori del runner/timeout preesistenti): cons (Back 2 «8.016 px vs tolleranza 8» identico prima di TD2), cop, f3, fx_test2, nav, net.
- NOT RUN (10): dipendenze esterne, come prima.
- Nessuna regressione non spiegata.

## Rollback (verificato)
Simulazione su clone locale: commit TD2 sopra `c9ed9b1` + `git revert` → contenuto **identico** a `c9ed9b1` (index.html e sw.js). Il service worker cambia identificativo a ogni build, quindi sia l'aggiornamento sia il rollback arrivano ai client al successivo avvio. I dati non vengono toccati in nessuno dei due sensi (nessuna chiave nuova).

## Preview iPhone: opzioni (nessuna attivata)
GitHub Pages serve un solo sito per repository e da qui non è raggiungibile; creare una preview richiede un servizio esterno.
- **A (consigliata) — deploy bozza su Netlify** (connettore già disponibile): URL separato, origine diversa = nessun dato reale dell'archivio coinvolto (importi il profilo di prova se vuoi); Firebase/login non servono a TD2. Zero effetti su `posty2001.github.io`.
- **B — pubblicazione controllata su GitHub Pages** come per F-A1: 1 commit funzionale, tag `pre-td2` locale (il push dei tag è bloccato), verifica build online, collaudo iPhone, rollback pronto (sopra).
- **C — repo/Pages separato**: stessa origine del sito reale (dati condivisi): sconsigliata.
Proposta: **A per il collaudo iPhone**, poi **B** per la pubblicazione definitiva dopo il tuo OK.

## Chiusura finale — build 20261108-2050-td2 (9/11/2026)
**Rifiniture estetiche**: testata più compatta (locandina invariata), tipografia metadati sans-serif con cifre tabulari, bordi secondari più leggeri (Diario TVA invariato = prioritario), badge PREVIEW solo nel pacchetto di anteprima (mai in produzione).
**Correzione "Continua"**: nessuna scheda resta espansa in linea; Home › Prossimo titolo / Continua porta alla scheda nella Timeline senza aprirla (MutationObserver su `details[open]`, stampa esclusa).
**Regressione completa 60 suite** (`run_suites.py --jobs 1`): PASS 38 · FAIL storici 6 (b32, bl, cron3c, fx_test4, fy, ui_audit — tutti documentati in KNOWN_FAILS.json, invariati) · BLOCKED 6 (cons, cop, f3, fx_test2, nav, net — invariati) · NOT RUN 10 · **FAIL nuovi 0**.
Adattamenti di test (solo dove il comportamento è cambiato per richiesta): m32_test (ID build verificato contro sw.js, 4 controlli al posto di 1), m341_test («Continua»/«Inizia» portano alla scheda in vista, NON aperta), td1_test / fx_test4 / net_test (apertura come pagina immersiva invece dell'espansione in linea), td2_test (chiusura della celebrazione XP, che dipende dalla missione del giorno).
**Scroll dopo Indietro**: 16/16 prove (8 titoli × pulsante e cronologia) con scarto 0 px. Un'oscillazione di 4 px (814→810) osservata una volta in td2_test non si è ripetuta: dovuta alle altezze stimate di `content-visibility:auto`; documentata come instabilità nota.
**Dati e produzione**: nessun badge in index.html/sw.js; configurazione Firebase, SDK, CSP, chiavi di storage e percorsi RTDB identici a c9ed9b1; sw.js cambia solo l'identificativo di build. Nessuna migrazione.
