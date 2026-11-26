# Miss Minutes 2.0 – Fase b (build 20261127-mm2b) – IN COLLAUDO, non completata

Solo TEST. Produzione, A5, TVA Live non toccati. Nessun servizio a pagamento, nessun grounding, nessuna chiave nel codice. Budget 0 €.

## 1. Analisi del caso «Spider-Man: Brand New Day è già uscito? Di cosa parla?» (collaudo mm2a)
| Elemento | Esito |
|---|---|
| Fatti inviati | solo «uscita 31/07/2026, già uscito»: **nessun tipo** (film/serie), **nessuna sinossi**, nessuna omonimia. Alla domanda «di cosa parla» il modello non aveva nulla di verificato e ha completato dalla memoria (ciclo a fumetti del 2008, omonimo). |
| Prompt | diceva di usare i fatti ma non vietava di inventare la trama né distingueva film/fumetti/omonimie; non c'era gerarchia delle fonti. |
| Cronologia | le risposte precedenti (anche errate) tornavano al modello come contesto, senza alcuna marcatura: **propagazione degli errori**. |
| Verificatore | (1) controllava solo frasi che **nominano il titolo**; (2) conosceva solo «già uscito / in sviluppo», non «non è un film», «è un ciclo a fumetti», «non esiste»; (3) il pattern «non è ancora uscito» non scattava mai (difetto del `\b` finale, trovato in questa fase). |

## 2. Soluzione generale (nessuna eccezione per Spider-Man)
- **Titolo in discussione** (`V.setFocus`): titolo della domanda, o della domanda precedente nei follow-up; tracciato frase per frase. Una frase senza titolo («Si tratta di un ciclo fumettistico del 2008») viene controllata contro il titolo in discussione. Se la domanda cita due titoli, nessun giudizio arbitrario.
- **Nuovi controlli** (validi per qualunque titolo del catalogo): `formato` (film/serie descritto come non-film o come ciclo/storyline a fumetti), `esistenza` (negata l'esistenza/uscita di un titolo già uscito), `tempo` (corretto il pattern mancante). Eccezioni legittime: omonimia dichiarata («esiste anche…», «omonimo», «da non confondere»), basato su/ispirato a, e domande che chiedono dei fumetti.
- **Gerarchia delle fonti** nei fatti e nel prompt: ufficiale > archivio-app (Timeline/TVA Atlas) > TMDB > Wikipedia/Wikidata > memoria del modello. Wikipedia e TMDB sono dichiarate «non ufficiali». Conflitti tra fatti da segnalare, non da risolvere in silenzio.
- **Film / fumetti / adattamenti / omonimie:** i fatti Timeline dichiarano il tipo (film/serie, saga, studio). La ricerca Wikipedia classifica ogni pagina dalla descrizione breve Wikidata (film, serie, fumetti, altro) e, se il nome indica opere di tipo diverso, aggiunge un fatto **OMONIMIA** esplicito.
- **Incertezza dichiarata:** se si chiede la trama e non c'è sinossi verificata, entra un fatto «lacuna» («NON inventare la trama»). Se le fonti esterne non rispondono, avviso all'utente: «Fonti aggiornate non raggiungibili ora: i dati recenti non sono stati verificati». Dopo una violazione: una sola ripresa dal testo verificato (motivi: attore, continuità, tempo, formato, esistenza), poi dichiarazione di incertezza.
- **Niente propagazione:** le risposte precedenti non verificate o che violano i controlli attuali vengono sostituite nella cronologia da «[risposta precedente omessa…]»; il prompt dice che la cronologia non è una fonte.
- **Fonti realmente consultate:** sotto la risposta compare «Fonti consultate» con i soli collegamenti (Wikipedia, Wikidata, TMDB) forniti al modello e il cui nome compare nella risposta, con data di consultazione; mai URL scritti dal modello (restano rimossi). Host in lista consentita, apertura in nuova scheda con `noopener`.
- **Ricerca Wikipedia/Wikidata** (`lookup.js`, lato app, senza chiave, senza passare dalle quote Gemini/Cloudflare): massimo 3 nomi per domanda, **solo il nome del titolo/personaggio** (da Timeline o schede dell'Atlante, mai la domanda o dati personali), timeout 3,5 s, fail-open, cache locale con TTL differenziato (titoli recenti/futuri 6 h, storici 14 giorni; cache scaduta usata se la rete fallisce). Impostazione «Fonti aggiornate» (attiva di default solo con AI online consentita) e «Svuota la cache».
- **TMDB:** la chiave non può stare nell'app: archivio generato offline `tools/mm_tmdb.py` (sinossi it-IT con ripiego en-US dichiarato, regia, cast, stato, **date per paese**, URL) tramite opzione `mm_tmdb` del workflow esistente «TMDB sync (manuale)» (ref test/tva-archives) con i Secret già esistenti. L'app lo usa se presente (`knowledge/tmdb_titoli.json`), altrimenti prosegue. **Non generato in questa build** (non ho accesso ai Secret).
- **Fonti ufficiali Marvel/Sony/Disney:** le loro pagine non espongono API pubbliche né CORS: non interrogabili dall'app a 0 €. Restano come classe «ufficiale» per voci curate a mano con URL verificato (non inserite in questa fase: BND da riscontrare).
- **Attribuzioni** in «Informazioni e crediti» (Wikipedia CC BY-SA 4.0, Wikidata CC0, TMDB).
- **CSP:** unica modifica, `connect-src` della finestra Miss Minutes + `https://en.wikipedia.org`.

## 3. Autoscroll stile ChatGPT
Segue il testo solo se sei in fondo; si sospende scorrendo verso l'alto (rotella/tocco); riprende con la freccia ↓ o tornando in fondo; niente animazioni sovrapposte (assegnazione istantanea solo quando serve), nessun salto a fine risposta (se segui resti in fondo, altrimenti la posizione non cambia). Le tre velocità (25/45/80 car/s) invariate.

## 4. Test (tutti in locale, Chromium emulazione iPhone; Safari iOS reale da collaudare)
Vedi tabella risultati nel messaggio di consegna. Nuovi: `verify_test.js` (37), `lookup_test.js` (14), `ui_mm2_test.py` (27), `ui_scroll_test.py` (11), gateway 58. L'endpoint reale di Wikipedia **non è raggiungibile da questo ambiente**: il formato della richiesta segue la documentazione MediaWiki (`generator=search` + `prop=extracts|pageprops`); la prima verifica reale è il collaudo su iPhone (Diagnostica → riga «Fonti»).

## 5. Quote e costi
Nessun costo. Wikipedia/Wikidata: chiamate dal dispositivo (≤3 per domanda, cache), non consumano Gemini né Cloudflare. Gemini: al massimo **+1 chiamata** per risposta che richiede la ripresa (limiti del gateway invariati: 6/min per IP, 12/min globali, 450/giorno). TMDB: ~140–300 richieste per esecuzione manuale dell'archivio.

## 6. Ridistribuire il gateway (necessario per il comportamento completo)
1. Repo **Posty2001/tva-live-scheduler**, branch `main`: il `worker.ts` aggiornato è già pubblicato (nessun deploy fatto).
2. Actions → **Miss Minutes - gateway** → Run workflow: prima `action = check`, poi `action = deploy` (stessi Secret e impostazioni di prima, AI come già configurata; nessun nuovo Secret).
3. Senza ridistribuzione l'app funziona comunque (verificatore, cronologia ripulita, ricerca fonti, autoscroll), ma il modello non riceve data odierna, gerarchia delle fonti e motivi di ripresa nuovi.
4. Facoltativo (archivio TMDB): Actions → **TMDB sync (manuale)** → «Use workflow from» = `test/tva-archives` → spunta `mm_tmdb` (e `mm_tmdb_commit` per scrivere il solo `tmdb_titoli.json` su `test/tva-archives`). Il workflow separato è stato rimosso: un file solo sul branch TEST non compare nelle Actions (GitHub elenca i workflow manuali dal branch predefinito); `main` non è stato modificato.

## 7. Limiti noti
- Il verificatore intercetta contraddizioni di tipo noto; non garantisce la verità di ogni frase. Una trama inventata ma priva delle parole-spia non è rilevabile deterministicamente: la difesa è il fatto «lacuna» + prompt (da misurare in fase c).
- Nessuna fonte ufficiale interrogabile automaticamente; BND non ancora riscontrato su pagina ufficiale Marvel/Sony.
- Fase c (≥50 domande documentate, metriche) e sonda grounding **non eseguite** (la sonda richiede la tua conferma che la fatturazione sia disattivata).
