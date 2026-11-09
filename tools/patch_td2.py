#!/usr/bin/env python3
"""Patch TD2 (idempotente, dopo patch_td1): pagina dettaglio immersiva a schermo intero per film/serie.
La scheda (li.card-wrap) NON viene ricostruita ne' copiata: si presenta a schermo intero (position:fixed) con classe .td-page,
lasciando nella Timeline un segnaposto della stessa altezza. Stessi nodi, stessi handler, stessi dati: nessuna migrazione.
Navigazione: usa il router esistente (tvaPushNav / tvaBack / popstate / snapshot). 3 microscopiche modifiche al router:
snapshot().td, ripristino in restore(), esclusione della pagina da anchorOf()."""
import re
P='/home/claude/work/index.html'; SW='/home/claude/work/sw.js'
BUILD='20261108-2050-td2'
s=open(P,encoding='utf-8').read()
def rep(old,new,marker):
    global s
    if marker in s: return
    assert s.count(old)==1,(old[:80],s.count(old)); s=s.replace(old,new)

# --- 1) router: snapshot.td, restore reopen, anchorOf exclusion ---
rep("a2: (W.tvaAtlas2 && $('atlas2Toggle') && $('atlas2Toggle').checked) ? W.tvaAtlas2.getState() : null };",
    "a2: (W.tvaAtlas2 && $('atlas2Toggle') && $('atlas2Toggle').checked) ? W.tvaAtlas2.getState() : null,\n        td: W.tvaTd2 ? W.tvaTd2.state() : null /* TD2 */ };",'/* TD2 */')
a="""        if (an && an.offsetParent !== null) settle(an, s.an.off, function () { busy = false; refreshProg(); });
        else { busy = false; refreshProg(); }"""
b="""        if (an && an.offsetParent !== null) settle(an, s.an.off, function () { busy = false; refreshProg(); if (s.td && W.tvaTd2) W.tvaTd2.open(s.td.id, { restoring: true }); });
        else { busy = false; refreshProg(); if (s.td && W.tvaTd2) W.tvaTd2.open(s.td.id, { restoring: true }); }"""
rep(a,b,'W.tvaTd2.open(s.td.id')
rep("!(e.closest && (e.closest('#appTabbar') || e.closest('.sidebar')))","!(e.closest && (e.closest('#appTabbar') || e.closest('.sidebar') || e.closest('.td-page')))",".closest('.td-page')")

r_old="            else if (ARCMAP[type]) ok = W.tvaGo('arc', ARCMAP[type] + ':' + id);"
rep(r_old, r_old + "\n            else if (W.tvaTd2 && /^item-/.test(id) && $(id) && $(id).matches('.card-wrap[data-item]')) ok = W.tvaGo('item', id); /* TD2: titoli -> pagina immersiva */", "/* TD2: titoli ->")
AT='html:not(#rs):not(#td1):not(#td2) .card-wrap.td-page'
CSS=r'''<style id="td2-css">
/* TD2-CSS: pagina dettaglio immersiva (la scheda diventa a schermo intero; nessun contenuto rimosso) */
@keyframes td2-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
html.td-lock, html.td-lock body { overflow: hidden !important; }
html.td-lock #appTabbar, html.td-lock .tva-back, html.td-lock .sidebar-open-btn { display: none !important; }
@P { --ink: #f3ecdf; --ink-soft: #cbbfac; --paper: #17110f; --marvel-red: #e04a5c; --g: clamp(14px, 4.5vw, 22px);
  position: fixed; inset: 0; z-index: 90000; display: block; box-sizing: border-box; margin: 0; padding-top: 0; padding-bottom: calc(2.2rem + var(--sab, env(safe-area-inset-bottom, 0px)));
  height: 100vh; height: 100dvh; padding-left: var(--sal, 0px); padding-right: var(--sar, 0px); overflow-x: hidden; overflow-y: auto; -webkit-overflow-scrolling: touch; overscroll-behavior: contain;
  background: radial-gradient(120% 55% at 50% 0%, #3a1018 0%, #0d0909 52%, #050405 100%); color: var(--ink); border: 0; border-radius: 0; box-shadow: none;
  content-visibility: visible; contain: none; list-style: none; animation: td2-in .24s ease; }
@P::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 26rem; background: var(--td-poster, none) center 18% / cover no-repeat; filter: blur(14px) saturate(1.15); opacity: .5; pointer-events: none; z-index: 0; }
@P::after { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 26rem; background: linear-gradient(180deg, rgba(5,4,5,.25) 0%, rgba(5,4,5,.55) 55%, #050405 100%); pointer-events: none; z-index: 0; }
@P > details.card { position: relative; z-index: 1; display: flex; flex-direction: column; max-width: 680px; width: 100%; margin: 0 auto; padding: 0; border: 0; border-radius: 0; background: none; box-shadow: none; box-sizing: border-box; }
@P > details.card > .detail-panel > * { margin-left: var(--g); margin-right: var(--g); box-sizing: border-box; }
@P > details.card > .detail-panel { display: flex; flex-direction: column; margin: 0; padding: 0; border: 0; background: none; box-shadow: none; }
/* barra Indietro (sempre accessibile) */
@P > .td2-bar { position: sticky; top: 0; height: 0; z-index: 5; overflow: visible; }
@P .td2-back { position: absolute; left: max(12px, calc(var(--sal, env(safe-area-inset-left, 0px)) + 8px)); top: calc(var(--sat, env(safe-area-inset-top, 0px)) + 10px); width: 46px; height: 46px; display: inline-flex; align-items: center; justify-content: center; padding: 0; border: 1px solid #d2b184; border-radius: 50%; background: rgba(10,6,7,.72); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); color: #f0dcb4; font-size: 1.9rem; line-height: 1; cursor: pointer; -webkit-tap-highlight-color: transparent; }
@P .td2-back:focus-visible { outline: 2px solid #fff; outline-offset: 2px; }
/* testata */
@P > details.card > summary { display: grid; grid-template-columns: minmax(96px, 34%) minmax(0, 1fr); column-gap: 14px; row-gap: .25rem; align-items: start; padding: calc(var(--sat, env(safe-area-inset-top, 0px)) + 66px) var(--g) .4rem; margin: 0; min-height: 0; list-style: none; cursor: default; background: none; border: 0; box-shadow: none; position: relative; }
@P > details.card > summary::-webkit-details-marker { display: none; }
@P > details.card > summary::marker { content: ""; }
@P > details.card > summary > img.m3-tl { display: block; grid-column: 1; grid-row: 1 / span 4; width: 100%; height: auto; aspect-ratio: 2 / 3; object-fit: cover; margin: 0; border-radius: 10px; box-shadow: 0 12px 32px rgba(0,0,0,.65), 0 0 0 1px rgba(210,177,132,.45); }
@P > details.card > summary > .rec { grid-column: 2; grid-row: 1; align-self: end; padding: 0; background: none; border: 0; font-family: 'IBM Plex Mono', monospace; font-size: .78rem; letter-spacing: .16em; color: #d2b184; }
@P > details.card > summary > .ic, @P > details.card > summary > .chev { display: none; }
@P > details.card > summary > .item-body { grid-column: 2; grid-row: 2; min-width: 0; margin: 0; }
@P > details.card > summary .item-top { display: flex; flex-direction: column; align-items: flex-start; gap: .4rem; min-width: 0; }
@P > details.card > summary .item-top .title { display: block; font-size: clamp(1.45rem, 6.6vw, 2.05rem); line-height: 1.12; font-weight: 700; color: #fff; text-shadow: 0 2px 14px rgba(0,0,0,.75); overflow-wrap: anywhere; word-break: break-word; hyphens: auto; text-wrap: balance; }
@P > details.card > summary .item-top .yr { font-family: 'IBM Plex Mono', monospace; font-size: 1rem; letter-spacing: .22em; color: #eadcc0; opacity: 1; }
@P > details.card > summary .item-top .tag { white-space: nowrap; }
@P > details.card > summary > .rating-widget.rw2 { grid-column: 1 / -1; grid-row: 5; margin: .9rem 0 0; padding: .6rem .75rem; max-width: 100%; width: 100%; box-sizing: border-box; border: 1px solid rgba(210,177,132,.38); border-radius: 12px; background: rgba(0,0,0,.38); box-shadow: none; }
@P .rw-inline .rw-s { width: 2rem; height: 2.75rem; }
@media (max-width: 340px) { @P .rw-inline .rw-s { width: 1.7rem; } }
@P > details.card > summary > .td2-act { grid-column: 1 / -1; grid-row: 6; display: flex; flex-wrap: wrap; gap: .6rem; margin: .7rem 0 0; }
@P.td2-nop > details.card > summary { grid-template-columns: minmax(0, 1fr); }
@P.td2-nop > details.card > summary > .rec, @P.td2-nop > details.card > summary > .item-body { grid-column: 1; }
/* stato di visione + preferito (stessi controlli della Timeline, solo spostati nella testata) */
@P .td2-act > .watch-box { position: static !important; transform: none; display: inline-flex; align-items: center; gap: .55rem; width: auto !important; height: auto; min-height: 46px; margin: 0; padding: 0 1rem !important; border: 1px solid rgba(210,177,132,.6); border-radius: 999px; background: rgba(0,0,0,.4); color: #f0e6d0; cursor: pointer; -webkit-tap-highlight-color: transparent; }
@P .td2-act > .watch-box .watch-mark { position: static; flex: 0 0 auto; width: 1.5rem; height: 1.5rem; display: inline-flex; align-items: center; justify-content: center; border: 1.6px solid rgba(242,232,216,.5); border-radius: 50%; font-size: .85rem; font-weight: 800; color: transparent; }
@P .td2-act > .watch-box .watch-mark::after { content: "Da vedere"; position: absolute; clip-path: inset(50%); }
@P .td2-act > .watch-box::after { content: "Da vedere"; font-family: 'IBM Plex Mono', monospace; font-size: .8rem; letter-spacing: .08em; text-transform: uppercase; }
@P .td2-act > .watch-box:has(.watch-check:checked) { border-color: #3fbf7f; background: rgba(20,80,50,.4); color: #d8f6e4; }
@P .td2-act > .watch-box:has(.watch-check:checked)::after { content: "Completato"; }
@P .td2-act > .watch-box .watch-check:checked ~ .watch-mark { color: #fff; background: #1f9d62; border-color: #1f9d62; }
@P .td2-act > .watch-box:has(.watch-check:focus-visible) { outline: 2px solid #fff; outline-offset: 2px; }
@P .td2-act > .fav-star { position: static !important; transform: none; display: inline-flex; align-items: center; gap: .5rem; width: auto !important; height: auto !important; min-height: 46px !important; margin: 0; padding: 0 1rem !important; border: 1px solid rgba(210,177,132,.6) !important; border-radius: 999px; background: rgba(0,0,0,.4) !important; color: #f0e6d0 !important; font-size: 1.15rem; line-height: 1; cursor: pointer; -webkit-tap-highlight-color: transparent; }
@P .td2-act > .fav-star::after { content: "Preferito"; font-family: 'IBM Plex Mono', monospace; font-size: .8rem; letter-spacing: .08em; text-transform: uppercase; }
@P .td2-act > .fav-star.is-fav { color: #f2b632 !important; border-color: #f2b632 !important; }
@P .td2-act > .fav-star:focus-visible { outline: 2px solid #fff; outline-offset: 2px; }
/* ordine delle sezioni (solo CSS: nessun nodo cambia genitore) */
@P .td-info { order: 1; }
@P .td-diary { order: 2; }
@P .tva-row[data-td="chars"] { order: 3; }
@P .td2-h { order: 4; }
@P details.sub-group { order: 4; }
@P .tva-row[data-td="uni"] { order: 5; }
@P .tva-row[data-td="amb"] { order: 5; }
@P .td-actions { order: 6; }
@P .td2-attr { order: 7; }
/* informazioni principali: fascia compatta senza riquadri annidati */
@P .td-info { margin-top: .9rem; margin-bottom: .9rem; padding: .2rem 0; border: 0; border-top: 1px solid rgba(210,177,132,.3); border-bottom: 1px solid rgba(210,177,132,.3); border-radius: 0; background: none; gap: .7rem .9rem; }
@P .td-info > .detail-row { padding-left: .6rem; border-left: 2px solid var(--marvel-red); }
@P .td-info .detail-k { color: #d2b184; }
@P .td-info .detail-v { color: var(--ink); }
/* personaggi */
@P .tva-row { display: block; margin-top: .9rem; margin-bottom: 0; padding: 0; border: 0; background: none; }
@P .tva-row > .detail-k { display: block; margin: 0 0 .5rem; font-family: 'IBM Plex Mono', monospace; font-size: .74rem; letter-spacing: .14em; color: #d2b184; text-transform: uppercase; }
@P .tva-row[data-td="chars"] > .detail-k::before { content: "👥 "; }
@P .tva-row > .detail-v { display: flex; flex-wrap: wrap; gap: .5rem; color: var(--ink); }
@P .tva-chip { min-height: 44px; padding: .5rem .8rem; border: 1px solid rgba(210,177,132,.45); border-left: 3px solid var(--marvel-red); border-radius: 10px; background: rgba(255,255,255,.04); color: var(--ink); font: inherit; font-size: .92rem; text-align: left; cursor: pointer; overflow-wrap: anywhere; -webkit-tap-highlight-color: transparent; }
@P .tva-chip:focus-visible { outline: 2px solid #fff; outline-offset: 2px; }
@P .tva-note { color: var(--ink-soft); }
/* approfondimenti */
@P .td2-h { margin: 1.3rem var(--g) .1rem; font-family: 'IBM Plex Mono', monospace; font-size: .8rem; font-weight: 600; letter-spacing: .16em; text-transform: uppercase; color: #d2b184; }
@P .td2-h::before { content: "📖 "; }
@P details.sub-group { margin-top: .5rem; margin-bottom: 0; border: 0; border-left: 3px solid var(--marvel-red); border-radius: 0 10px 10px 0; background: rgba(255,255,255,.045); }
@P details.sub-group[open] { background: rgba(160,30,40,.14); }
@P details.sub-group > summary { color: #f6efe2; }
@P details.sub-group .detail-k { color: #d2b184; }
@P details.sub-group .detail-v { color: var(--ink); }
/* Diario TVA e azioni */
@P .td-diary { margin-top: .9rem; margin-bottom: 0; }
@P .td-actions { margin-top: 1.2rem; margin-bottom: 0; }
@P .td-actions::before { content: "GUARDA E FILE LOCALE"; grid-column: 1 / -1; grid-row: 1; font-family: 'IBM Plex Mono', monospace; font-size: .74rem; letter-spacing: .14em; color: #d2b184; }
@P .td-actions > details.watch-picker { grid-column: 1; grid-row: 2; }
@P .td-actions > label.local-file-btn { grid-column: 2; grid-row: 2; }
@P .td-actions > details.watch-picker[open] { grid-column: 1 / -1; grid-row: 2; }
@P .td-actions > details.watch-picker[open] ~ label.local-file-btn { grid-column: 1 / -1; grid-row: 3; }
@media (max-width: 340px) { @P .td-actions > details.watch-picker, @P .td-actions > label.local-file-btn, @P .td-actions > details.watch-picker[open], @P .td-actions > details.watch-picker[open] ~ label.local-file-btn { grid-column: 1; grid-row: auto; } }
@P .td-actions.td-na { display: block; }
@P .td-actions.td-na p { margin: .5rem 0 0; font-size: .88rem; line-height: 1.4; color: var(--ink-soft); }
@P .td2-attr { margin-top: 1.2rem; margin-bottom: 0; font-size: .7rem; line-height: 1.4; color: var(--ink-soft); opacity: .8; }
@P .td2-attr a { color: inherit; text-decoration: underline; }
/* TD2-R: rifinitura finale (testata piu' compatta, tipografia dei metadati, bordi secondari piu' leggeri; Diario TVA invariato = elemento prioritario) */
@P { --sans: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; --line: rgba(210,177,132,.2); }
@P > details.card > summary { padding-top: calc(var(--sat, env(safe-area-inset-top, 0px)) + 56px); padding-bottom: .2rem; column-gap: 13px; row-gap: .15rem; }
@P > details.card > summary > .rec { font-family: var(--sans); font-size: .72rem; font-weight: 600; letter-spacing: .14em; font-variant-numeric: tabular-nums; }
@P > details.card > summary .item-top { gap: .3rem; }
@P > details.card > summary .item-top .title { line-height: 1.1; }
@P > details.card > summary .item-top .yr { font-family: var(--sans); font-size: .98rem; font-weight: 600; letter-spacing: .05em; font-variant-numeric: tabular-nums; color: #e6d7b8; }
@P > details.card > summary .item-top .tag { font-family: var(--sans); font-size: .66rem; font-weight: 600; letter-spacing: .07em; }
@P > details.card > summary > .rating-widget.rw2 { margin-top: .6rem; padding: .35rem .7rem; border: 1px solid var(--line); background: rgba(0,0,0,.28); }
@P > details.card > summary > .td2-act { gap: .5rem; margin-top: .5rem; }
@P .td2-act > .watch-box, @P .td2-act > .fav-star { min-height: 44px !important; border-color: rgba(210,177,132,.34) !important; background: rgba(0,0,0,.3) !important; }
@P .td2-act > .watch-box:has(.watch-check:checked) { border-color: rgba(63,191,127,.7) !important; background: rgba(20,80,50,.38) !important; }
@P .td2-act > .fav-star.is-fav { border-color: rgba(242,182,50,.75) !important; }
@P .td2-act > .watch-box::after, @P .td2-act > .fav-star::after { font-family: var(--sans); font-size: .74rem; font-weight: 600; letter-spacing: .07em; }
@P .td-info { margin-top: .6rem; margin-bottom: .5rem; padding: .1rem 0; border-top-color: var(--line); border-bottom-color: var(--line); gap: .55rem .9rem; }
@P .td-info > .detail-row { border-left: 2px solid rgba(224,74,92,.5); padding-left: .65rem; }
@P .td-info .detail-k, @P .tva-row > .detail-k, @P .td2-h, @P .td-actions::before { font-family: var(--sans); font-weight: 600; letter-spacing: .1em; color: #d8bb8f; }
@P .td-info .detail-k { font-size: .64rem; letter-spacing: .06em; margin-bottom: .1rem; white-space: nowrap; }
@P .tva-row > .detail-v, @P .tva-row > .detail-v .tva-note, @P .tva-row > p, @P .tva-note { font-family: var(--sans); }
@P .td-info .detail-v { font-family: var(--sans); font-size: .93rem; line-height: 1.38; color: #f1e9da; }
@P .td-info > .td-pos .detail-v { font-family: var(--sans); font-variant-numeric: tabular-nums; letter-spacing: .01em; font-size: .93rem; }
@P .tva-row > .detail-k { font-size: .7rem; }
@P .td2-h { font-size: .72rem; margin-top: 1.1rem; }
@P .td-actions::before { font-size: .7rem; }
@P .tva-chip { font-family: var(--sans); font-size: .9rem; border-color: var(--line); border-left: 2px solid rgba(224,74,92,.6); background: rgba(255,255,255,.03); }
@P details.sub-group { border-left: 2px solid rgba(224,74,92,.5); background: rgba(255,255,255,.03); }
@P details.sub-group[open] { background: rgba(160,30,40,.1); }
@P details.sub-group > summary { font-family: var(--sans); }
@P .td-actions > label.local-file-btn { border-color: rgba(210,177,132,.4) !important; background: rgba(210,177,132,.06) !important; }
@P .td-actions > details.watch-picker > summary { border-color: rgba(210,177,132,.45) !important; }
@P .td-diary { margin-top: .75rem; }
@media (prefers-reduced-motion: reduce) { @P { animation: none; } }
</style>
'''.replace('@P',AT)

JS=r'''<script id="td2-js">
/* TD2: pagina dettaglio immersiva. Solo presentazione + navigazione: nessun accesso a localStorage/rete/Firebase.
   La scheda e' lo stesso nodo della Timeline (stessi handler, stessi dati); alla chiusura tutto torna com'era. */
(function () {
  'use strict';
  var D = document, W = window, CUR = null;
  function el(t, c, x) { var e = D.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
  function titleOf(li) { var t = li.querySelector('.item-top .title'); return t ? t.textContent.trim() : ''; }
  function onKey(ev) {
    if (!CUR) return;
    if (ev.key === 'Escape' && !(ev.target && ev.target.tagName === 'TEXTAREA')) { ev.preventDefault(); back(); return; }
    if (ev.key !== 'Tab') return;
    var f = Array.prototype.filter.call(CUR.li.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),textarea:not([disabled]),summary,[tabindex]:not([tabindex="-1"])'), function (e) { return e.getClientRects().length && e.getAttribute('tabindex') !== '-1'; });
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1], a = D.activeElement;
    if (ev.shiftKey && (a === first || !CUR.li.contains(a))) { ev.preventDefault(); last.focus(); }
    else if (!ev.shiftKey && (a === last || !CUR.li.contains(a))) { ev.preventDefault(); first.focus(); }
  }
  function mount(li, y0, opt) {
    var det = li.querySelector(':scope > details.card'); if (!det) return false;
    var rect = li.getBoundingClientRect(), cs = W.getComputedStyle(li);
    var ph = D.createElement(li.tagName.toLowerCase()); ph.className = 'td2-ph'; ph.setAttribute('aria-hidden', 'true');
    ph.style.cssText = 'height:' + Math.round(rect.height * 100) / 100 + 'px;margin:' + cs.margin + ';padding:0;border:0;visibility:hidden;list-style:none;';
    li.parentNode.insertBefore(ph, li);
    var r = { li: li, ph: ph, det: det, wasOpen: opt && opt.wasOpen != null ? opt.wasOpen : det.open, y: y0, added: [], id: li.getAttribute('data-item'), sum: det.querySelector(':scope > summary') };
    li.classList.add('td-page'); li.setAttribute('role', 'dialog'); li.setAttribute('aria-modal', 'true'); li.setAttribute('aria-label', titleOf(li));
    D.documentElement.classList.add('td-lock');
    det.open = true;
    var sum = r.sum, wb = li.querySelector(':scope > .watch-box'), fav = li.querySelector(':scope > .fav-star');
    if (sum && (wb || fav)) { var act = el('div', 'td2-act'); if (wb) act.appendChild(wb); if (fav) act.appendChild(fav); sum.appendChild(act); r.added.push(act); }
    var bar = el('div', 'td2-bar'), bb = el('button', 'td2-back'); bb.type = 'button'; bb.setAttribute('aria-label', 'Indietro'); bb.title = 'Indietro'; bb.innerHTML = '<span aria-hidden="true">‹</span>';
    bb.addEventListener('click', back); bar.appendChild(bb); li.insertBefore(bar, li.firstChild); r.added.push(bar); r.bb = bb;
    var pn = det.querySelector(':scope > .detail-panel'); r.pn = pn; r.moved = [];
    if (pn) ['.td-diary', '.td-actions'].forEach(function (q) { var n = det.querySelector(':scope > ' + q); if (n) { r.moved.push(n); pn.appendChild(n); } });
    var sg = det.querySelector('.detail-panel > details.sub-group');
    if (sg) { var h = el('h2', 'td2-h', 'Approfondimenti'); sg.parentNode.insertBefore(h, sg); r.added.push(h); }
    Array.prototype.forEach.call(det.querySelectorAll('.detail-panel > .tva-row'), function (row) {
      var k = row.querySelector('.detail-k'), t = k ? k.textContent.toUpperCase() : '';
      row.setAttribute('data-td', /PERSONAGGI/.test(t) ? 'chars' : /UNIVERSO/.test(t) ? 'uni' : 'amb');
    });
    var im = sum && sum.querySelector('img.m3-tl'), src = im ? (im.currentSrc || im.src) : '';
    if (src) li.style.setProperty('--td-poster', 'url("' + src.replace(/"/g, '%22') + '")'); else li.classList.add('td2-nop');
    if (im && im.getAttribute('data-src') === 'tmdb') {
      var at = el('p', 'td2-attr'), a = el('a', null, 'TMDB'); a.href = 'https://www.themoviedb.org/'; a.target = '_blank'; a.rel = 'noopener noreferrer';
      at.appendChild(D.createTextNode('Locandina: ')); at.appendChild(a); at.appendChild(D.createTextNode(' — This product uses the TMDB API but is not endorsed or certified by TMDB.'));
      (pn || det).appendChild(at); r.added.push(at);
    }
    if (!li.querySelector('.td-actions')) {
      var na = el('div', 'td-actions td-na'); na.appendChild(el('p', null, 'Nessuna opzione di visione o file locale disponibile per questo titolo.')); (pn || det).appendChild(na); r.added.push(na);
    }
    var nt = det.querySelector('details.note-toggle'); r.ntOpen = nt ? nt.open : null;
    if (nt && nt.open && !(D.activeElement && D.activeElement.tagName === 'TEXTAREA')) nt.open = false;   /* si parte dall'anteprima del Diario */
    D.addEventListener('keydown', onKey, true);
    li.scrollTop = 0; CUR = r;
    try { bb.focus({ preventScroll: true }); } catch (e) {}
    return true;
  }
  function unmount(keepLock, focusBack) {
    if (!CUR) return; var r = CUR, li = r.li; CUR = null;
    D.removeEventListener('keydown', onKey, true);
    var nt = r.det.querySelector('details.note-toggle'); if (nt && r.ntOpen !== null && nt.open !== r.ntOpen) nt.open = r.ntOpen;
    var wb = li.querySelector('.td2-act > .watch-box'), fav = li.querySelector('.td2-act > .fav-star');
    if (wb) li.insertBefore(wb, r.det); if (fav) li.insertBefore(fav, r.det);
    r.added.forEach(function (n) { if (n.parentNode) n.parentNode.removeChild(n); });
    if (r.pn) { var ref = r.pn.nextSibling; r.moved.forEach(function (n) { r.det.insertBefore(n, ref); }); }
    Array.prototype.forEach.call(r.det.querySelectorAll('.detail-panel > .tva-row[data-td]'), function (row) { row.removeAttribute('data-td'); });
    li.classList.remove('td-page', 'td2-nop'); li.removeAttribute('role'); li.removeAttribute('aria-modal'); li.removeAttribute('aria-label'); li.style.removeProperty('--td-poster');
    r.det.open = r.wasOpen;
    if (r.ph.parentNode) r.ph.parentNode.removeChild(r.ph);
    if (!keepLock) D.documentElement.classList.remove('td-lock');
    if (focusBack && r.sum) { try { r.sum.focus({ preventScroll: true }); } catch (e) {} }
  }
  function exitHub() { var x = D.getElementById('homeHubExited'); if (x) x.checked = true; var h = D.getElementById('homeHub'); if (h) h.style.display = 'none'; }
  /* rende visibile il titolo come faceva il router (solo i filtri responsabili vengono azzerati; Indietro li ripristina) */
  function reveal(li, cb) {
    var n = 0;
    (function step() {
      if (li.offsetParent !== null) return cb(true);
      var uf = W.marvelUniFiltroStato && W.marvelUniFiltroStato(), du = li.getAttribute('data-uni');
      if (n === 0 && uf && uf.uid && du && du.indexOf(uf.uid) === -1 && W.marvelUniFiltroReset) W.marvelUniFiltroReset();
      else if (n === 1 && li.style.display === 'none' && W.marvelFiltriSblocca) W.marvelFiltriSblocca(li);
      if (n > 3) return cb(li.offsetParent !== null);
      n++; setTimeout(step, 160);
    })();
  }
  var oCloseOv = null;
  /* UNICA implementazione: Timeline, Atlante, Centrale TVA, collegamenti tra titoli, titoli nascosti da filtri */
  function openPage(li, opt) {
    opt = opt || {}; install();
    if (typeof li === 'string') li = D.getElementById(/^item-/.test(li) ? li : 'item-' + li);
    if (!li || !li.matches || !li.matches('.card-wrap[data-item]')) return false;
    if (CUR && CUR.li === li) return true;
    var inPage = !!CUR, y0 = inPage ? CUR.y : (W.pageYOffset || 0), visible = li.offsetParent !== null;
    if (!visible && opt.restoring) return false;
    if (!opt.restoring && W.tvaPushNav) W.tvaPushNav('');        /* snapshot PRIMA di toccare il DOM: filtri, scorrimento, schermata/pagina di provenienza */
    if (inPage) unmount(true);
    if (!opt.restoring && !opt.fromTimeline) {                    /* provenienza da Atlante/Centrale/link: chiude gli overlay, come il router */
      if (oCloseOv) oCloseOv.call(W);
      exitHub(); if (W.marvelAggiornaTab) W.marvelAggiornaTab('timeline');
    }
    if (visible || opt.restoring) return mount(li, y0, opt);
    D.documentElement.classList.add('td-lock');
    reveal(li, function (ok) {
      if (!ok || !mount(li, y0, opt)) D.documentElement.classList.remove('td-lock');
    });
    return true;
  }
  function back() {
    if (!CUR) return; var done = false;
    try { done = W.tvaBack ? W.tvaBack() : false; } catch (e) { done = false; }
    if (!done) { var y = CUR.y; unmount(false, true); W.scrollTo(0, y); }
  }
  /* i wrapper si installano quando router e Atlante hanno gia' definito marvelChiudiOverlay/tvaGo (load): una sola volta */
  var done = false;
  function install() {
    if (done) return;
    var oClose = W.marvelChiudiOverlay, oGo = W.tvaGo; oCloseOv = oClose;
    if (typeof oClose !== 'function' || typeof oGo !== 'function') return;
    done = true;
    /* il router chiude gli overlay prima di ogni navigazione/ripristino: la pagina e' un overlay a tutti gli effetti */
    W.marvelChiudiOverlay = function () { if (CUR) unmount(false, false); return oClose.apply(this, arguments); };
    /* collegamenti verso altri titoli mentre la pagina e' aperta: si resta nella pagina, Indietro torna al titolo precedente */
    W.tvaGo = function (kind, id, opt) {
      if (kind === 'item' && !(opt && opt.scheda) && W.tvaAtlas2 && D.getElementById('atlas2Toggle') && D.getElementById('atlas2Toggle').checked && W.tvaAtlas2.stato) {
        var sc = W.tvaAtlas2.stato().screen;                    /* Atlante aperto: il numero opera apre il Dossier Opera (comportamento proprio dell'Atlante); «Scheda in guida» apre la pagina */
        if (sc !== 'mappa' && sc !== 'cron') { var rr = oGo.apply(this, arguments); if (rr) return rr; }
      }
      if (kind === 'item') { var k = String(id), li = D.getElementById(/^item-/.test(k) ? k : 'item-' + k); if (li && li.matches('.card-wrap[data-item]') && openPage(li, opt && opt.nopush ? { restoring: true } : {})) return true; }
      return oGo.apply(this, arguments);
    };
  }
  if (D.readyState === 'complete') setTimeout(install, 0); else W.addEventListener('load', function () { install(); setTimeout(install, 500); });
  /* apertura dalla Timeline: tocco sulla testata della scheda */
  D.addEventListener('click', function (ev) {
    var t = ev.target; if (!t || !t.closest) return;
    var sm = t.closest('.card-wrap[data-item] > details.card > summary'); if (!sm) return;
    var li = sm.closest('.card-wrap'), inter = t.closest('a,button,input,label,textarea,.rating-widget');
    if (li.classList.contains('td-page')) { if (!inter) ev.preventDefault(); return; }
    if (inter) return;
    if (openPage(li, { fromTimeline: true })) ev.preventDefault();
  }, true);
  /* nessuna scheda resta "espansa" in linea (es. Home > Continua, Ultima visione, link interni che impostano details[open]):
     l'espansione viene annullata (la scheda resta chiusa: i collegamenti che devono aprire la pagina usano tvaGo); stampa esclusa */
  var PRINTING = false;
  W.addEventListener('beforeprint', function () { PRINTING = true; }, true);
  W.addEventListener('afterprint', function () { PRINTING = false; }, true);
  try {
    new MutationObserver(function (list) {
      if (PRINTING) return;
      var opened = [];
      list.forEach(function (m) {
        var d = m.target; if (!d || !d.matches || !d.matches('.card-wrap[data-item] > details.card') || !d.open) return;
        var li = d.parentNode; if (li.classList.contains('td-page') || opened.indexOf(li) >= 0) return;
        opened.push(li);
      });
      if (!opened.length) return;
      opened.forEach(function (li) { li.querySelector(':scope > details.card').open = false; });
    }).observe(D, { subtree: true, attributes: true, attributeFilter: ['open'] });
  } catch (e) {}
  W.tvaTd2 = Object.freeze({ open: function (id, o) { return openPage(id, o); }, close: function () { back(); }, state: function () { return CUR ? { id: 'item-' + CUR.id } : null; }, isOpen: function () { return !!CUR; } });
})();
</script>
'''
rep('<script id="fa1-js">',JS+'<script id="fa1-js">','id="td2-js"')
rep('<style id="td1-css">',CSS+'<style id="td1-css">','id="td2-css"')
s=re.sub(r'(name="tva-build" content=")[^"]*',lambda m:m.group(1)+BUILD,s)
open(P,'w',encoding='utf-8').write(s)
w=open(SW,encoding='utf-8').read()
w=re.sub(r"const SW_BUILD = '[^']*';","const SW_BUILD = '%s';"%BUILD,w)
w=re.sub(r"const CACHE_NAME = '[^']*';","const CACHE_NAME = 'marvel-timeline-cache-%s';"%BUILD,w)
open(SW,'w',encoding='utf-8').write(w)
print('ok',BUILD)
