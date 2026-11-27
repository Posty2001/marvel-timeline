# Miss Minutes 2.0 — hotfix mm2e.1 (viewport iOS, fallback locale, naturalezza)

Build `20261127-1500-mm2e1` · solo TEST · produzione congelata · A5 sospesa · 0 €. **In attesa di collaudo reale su Safari iPhone: non dichiarata completata.**

## 1. Viewport iOS («Miss Minutes scivola in basso e mostra la Home»)
Gli screenshot (IMG_2741.png) **non sono arrivati nella sessione**: l'analisi si basa sul codice dell'host (`index.html`, blocco MM-HOST) e va confermata sul dispositivo.
Causa probabile: l'overlay veniva posizionato (`top`/`height`) direttamente dal `visualViewport`. Alla pressione di Invia la tastiera si chiude: iOS emette `resize`/`scroll` con valori intermedi (offsetTop > 0, height ridotta) e l'overlay stesso si accorciava/traslava, lasciando scoperta la pagina sotto; inoltre la catena di scorrimento dell'iframe verso il documento ospite poteva muovere la pagina.
Correzione (solo host + CSS dell'assistente, nessun dato toccato):
- l'overlay è `fixed` su **tutto** il viewport di layout, sfondo opaco più `box-shadow` di spread (copre anche il rubber-band): la pagina sotto non è mai visibile, qualunque sia lo stato della tastiera;
- solo l'**iframe** segue il `visualViewport` (top/height), con aggiornamenti coalizzati in un frame (rAF) e riassestamenti a 90/260/600 ms dopo `resize`, `orientationchange`, scroll;
- pagina ospite bloccata mentre l'assistente è aperto (`html.mm-open`: overflow hidden, overscroll none; `touchmove` sull'overlay annullato);
- documento dell'assistente non scorrevole (`html` overflow hidden, `body` fixed): nessuna catena di scorrimento verso la pagina;
- chiusura: la classe viene tolta, la posizione originale (tab e scroll) ripristinata come prima; lo scroll della conversazione resta (l'iframe non viene distrutto).

## 2. Motore locale e fallback
Il motore locale rispondeva perché le domande tipo «chi è / poteri di / che livello» sono classificate SEMPLICI (anagrafica) e per design non vanno online; la risposta era l'intera scheda (poteri, livello, legami, «Riferimento: … [verifica]»).
Ora `describe(e, ctx, aspetto)` restituisce **solo** l'aspetto chiesto (poteri, legami, universo, uscita, posizione, generale = nome + universo + testo). Se il dato non c'è: lo dice («nella guida dell'app non ci sono dati sui poteri…») e, con AI online attiva, passa all'AI (`needsOnline`); nessuna informazione inventata. Rimossi dal testo i riferimenti tecnici «[verification]», livello e legami non richiesti, e il blocco «Vedi anche» per le domande specifiche.

## 3. Naturalezza
Eliminati i flair/battute fisse del motore locale (aperture e chiusure tipo «Il Tempo non perdona», «Altro da potare?»), le frasi su Linea Temporale/«complimenti, Variante» e i consigli non richiesti. Il prompt del gateway (già nel repo scheduler, `1846ea0`) resta da ridistribuire.

## 4. Test
`ui_viewport_test.py` (18 controlli con `visualViewport` simulato: apertura, tastiera, 5 transizioni rapide, scroll pagina, documento non scorrevole, chiusura/riapertura con scroll pagina e conversazione preservati), `engine_test.js` 42 (poteri/legami/livello/chi è, niente battute). Limite: Chromium con visualViewport simulato non riproduce l'animazione reale di iOS Safari: il collaudo su iPhone resta necessario.
