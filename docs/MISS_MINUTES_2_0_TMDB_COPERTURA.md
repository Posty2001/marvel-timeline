# Archivio TMDB di Miss Minutes 2.0 – verifica e copertura (27/11/2026)

Fonte: workflow «TMDB sync (manuale)» #50, opzione `mm_tmdb` + `mm_tmdb_commit`, ref `test/tva-archives` → commit `5e18986` (autore `tva-mm-bot`, **un solo file**: `miss-minutes/knowledge/tmdb_titoli.json`, 148 KB, generato 2026-11-26T20:56:33Z). `main` non toccato.

## Copertura (Timeline = 138 titoli)
| Dato | Copertura |
|---|---|
| Voci in archivio | **131 / 138** (85 film + 46 serie TMDB) |
| Sinossi it-IT | 131 / 131 (2 con ripiego en-US dichiarato) |
| Regia | 85 / 85 film · 0 / 46 serie (TMDB non espone la regia per le serie) |
| Cast principale | 127 / 131 (85 film, 42 serie) |
| Stato TMDB | 131 / 131 |
| Date di uscita per paese | film: IT 78/85, US 84/85; serie: solo la prima messa in onda della serie |

**Titoli senza voce (7):** N°073 The Defenders, N°074 The Punisher S1, N°077 Team Thor/Team Darryl shorts, N°086 The Punisher S2, N°107 Guardians of the Galaxy Holiday Special, N°115 I Am Groot shorts, **N°125 Fantastic Four: First Steps** (film, assente da `tmdb_map.json`: da correggere con un override verificato dall'utente, non l'ho indovinato).

## Limiti dei dati e come l'app li gestisce
1. **Le serie sono per l'intera serie:** per titoli come «Loki S2» TMDB dà sinossi, cast e data della serie (S1). L'app etichetta «della SERIE (non della singola stagione)» e scrive che la data TMDB «NON è la data di questa stagione» (vale la Timeline). 25 titoli hanno date TMDB diverse dalla Timeline, in gran parte per questo motivo.
2. **Date film con anteprime:** il generatore prendeva la prima data tra i tipi 2–6 (incluse anteprime/limited): es. Ghost Rider 2 → US 10/12/2011 contro 17/02/2012. Il generatore è corretto (priorità: cinema, poi digitale/fisico/TV, anteprime solo se non c'è altro) **ma l'archivio attuale è stato generato con la vecchia regola**: va rigenerato (stesso workflow). Nel frattempo l'app dichiara «DISCORDANZA con la Timeline» invece di sceglierne una.
3. **Sinossi troncate:** 37 sinossi erano tagliate a 600 caratteri a metà frase. Ora l'app taglia a fine frase/parola; il generatore tronca a 700 caratteri a fine frase. Si risolve del tutto rigenerando.
4. TMDB non è una conferma ufficiale: classe «tmdb», sotto «archivio-app» nella gerarchia.

## Spider-Man: Brand New Day (N°132)
- TMDB: film (movie 969681), stato **Released**, regia Destin Daniel Cretton, cast Tom Holland, Sadie Sink, Tramell Tillman, Zendaya, Jacob Batalon, Jon Bernthal, Mark Ruffalo, Florence Pugh; uscite **IT/GB/FR/DE/ES 29/07/2026, US 31/07/2026**, coerente con la Timeline (31/07/2026, mercato USA). Sinossi it-IT presente (4 anni dopo No Way Home).
- Distinzione film/fumetti: la voce TMDB è per costruzione un **film**; il fatto Timeline dichiara «film»; il ciclo a fumetti del 2008 compare solo come omonimia (via Wikipedia, se raggiungibile) e il verificatore blocca «ciclo fumettistico / non è un film / non esiste» per i titoli del catalogo. Non è stata verificata presso una pagina ufficiale Marvel/Sony (ancora «archivio-app» + TMDB, non «ufficiale»).

## Uso reale nelle risposte (test `ui_tmdb_test.py`, 10/10)
Con Wikipedia volutamente non raggiungibile, la domanda su BND invia al gateway i fatti `tmdb` (sinossi + regia, date per paese), senza «lacuna», in ordine di gerarchia, con link TMDB nelle «Fonti consultate» (data 26/11/2026); stagioni e discordanze dichiarate; nessun dato personale nel payload.

## Cache e PWA
`tmdb_titoli.json` è nella lista di precache del service worker (cache `…-mm2b1`): verificato in Chromium che è presente in cache e leggibile **offline** (131 voci). La cache delle ricerche Wikipedia è separata (localStorage, TTL 6 h/14 gg, svuotabile dalle Impostazioni).
