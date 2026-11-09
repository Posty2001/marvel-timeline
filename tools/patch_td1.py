#!/usr/bin/env python3
"""Patch TD1 (idempotente, dopo patch_fa1): restyling schede espanse + Diario TVA.
Solo CSS + JS di presentazione. NON tocca: formato/chiavi delle note (NOTES_KEY, 1 stringa per titolo), progressi, voti, XP, badge, Timeline,
Firebase/Auth/sync/rooms/Friends/Rankings. Il textarea originale (#note-NNN.user-note) e il suo salvataggio restano gli unici responsabili dello storage."""
import re
P='/home/claude/work/index.html'; SW='/home/claude/work/sw.js'
BUILD='20261107-1505-td1'
s=open(P,encoding='utf-8').read()
def rep(old,new,marker):
    global s
    if marker in s: return
    assert s.count(old)==1,(old[:70],s.count(old)); s=s.replace(old,new)

CSS=r'''<style id="td1-css">
/* TD1-CSS: restyling schede + Diario TVA (specificita' alzata per battere i layer m3/rs esistenti) */
html:not(#rs):not(#td1) .card-wrap > details.card .item-body { min-width: 0; }
html:not(#rs):not(#td1) .card-wrap > details.card .item-top .title { min-width: 0; max-width: 100%; overflow-wrap: anywhere; word-break: break-word; hyphens: auto; line-height: 1.22; text-wrap: balance; }
html:not(#rs):not(#td1) .card-wrap > details.card .item-top .yr { opacity: .85; letter-spacing: .04em; }
html:not(#rs):not(#td1) .card-wrap > details.card .item-top .tag { white-space: nowrap; }
html:not(#rs):not(#td1) .card-wrap > details.card > summary .rec { letter-spacing: .08em; }
html:not(#rs):not(#td1) .card-wrap > details.card > summary .chev { color: #d2b184; }

/* Info principali: card compatta a 2 colonne */
html:not(#rs):not(#td1) .card-wrap .detail-panel .td-info { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .45rem; margin: 0 0 .7rem; padding: .7rem; border: 1px solid rgba(210,177,132,.38); border-radius: 10px; background: linear-gradient(160deg, rgba(210,177,132,.09), rgba(160,30,40,.06)); box-shadow: inset 3px 0 0 var(--marvel-red); }
html:not(#rs):not(#td1) .card-wrap .detail-panel .td-info > .detail-row { margin: 0; padding: 0; border: 0; background: none; min-width: 0; display: block; }
html:not(#rs):not(#td1) .card-wrap .detail-panel .td-info > .td-wide { grid-column: 1 / -1; }
html:not(#rs):not(#td1) .card-wrap .detail-panel .td-info .detail-k { display: block; font-size: .62rem; letter-spacing: .12em; color: #d2b184; margin-bottom: .12rem; }
html:not(#rs):not(#td1) .card-wrap .detail-panel .td-info .detail-v { display: block; overflow-wrap: anywhere; line-height: 1.35; font-size: .95rem; }
html:not(#rs):not(#td1) .card-wrap .detail-panel .td-info > .td-pos .detail-v { font-family: 'IBM Plex Mono', monospace; letter-spacing: .02em; font-size: .85rem; }
@media (max-width: 340px) { html:not(#rs):not(#td1) .card-wrap .detail-panel .td-info { grid-template-columns: minmax(0, 1fr); } }

/* Accordion: contrasto, indicatore evidente, tocco >= 48px */
html:not(#rs):not(#td1) .card-wrap .detail-panel details.sub-group { margin: .4rem 0 0; padding: 0; border: 1px solid rgba(210,177,132,.32); border-radius: 10px; overflow: hidden; background: rgba(210,177,132,.05); transition: border-color .2s, background .2s; }
html:not(#rs):not(#td1) .card-wrap .detail-panel details.sub-group[open] { border-color: var(--marvel-red); background: rgba(160,30,40,.07); }
html:not(#rs):not(#td1) .card-wrap .detail-panel details.sub-group > summary { display: flex; align-items: center; gap: .6rem; min-height: 48px; padding: .55rem .8rem; cursor: pointer; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--ink); -webkit-tap-highlight-color: transparent; }
html:not(#rs):not(#td1) .card-wrap .detail-panel details.sub-group > summary::before { display: none; }
html:not(#rs):not(#td1) .card-wrap .detail-panel details.sub-group > summary::after { content: ""; margin-left: auto; flex: 0 0 auto; width: .55rem; height: .55rem; border-right: 2px solid #d2b184; border-bottom: 2px solid #d2b184; transform: rotate(45deg); transition: transform .2s ease; }
html:not(#rs):not(#td1) .card-wrap .detail-panel details.sub-group[open] > summary::after { transform: rotate(-135deg); border-color: var(--marvel-red); }
html:not(#rs):not(#td1) .card-wrap .detail-panel details.sub-group > .sub-group-body { padding: .2rem .8rem .8rem; }
@keyframes td1-in { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: none; } }
html:not(#rs):not(#td1) .card-wrap details[open] > .sub-group-body, html:not(#rs):not(#td1) .card-wrap .td-diary details[open] > .user-note-box { animation: td1-in .22s ease; }
@media (prefers-reduced-motion: reduce) { html:not(#rs):not(#td1) .card-wrap * { animation: none !important; transition: none !important; } }
/* sezioni "nell'archivio" (chip) piu' compatte */
html:not(#rs):not(#td1) .card-wrap .detail-panel > .detail-row.tva-row { margin-top: .5rem; }

/* Diario TVA */
html:not(#rs):not(#td1) .card-wrap .td-diary { margin: .9rem 0 .6rem; padding: .85rem .9rem; border: 1px solid #d2b184; border-radius: 12px; background: linear-gradient(160deg, rgba(160,30,40,.12), rgba(210,177,132,.08)); box-shadow: 0 0 0 1px rgba(160,30,40,.55), 0 0 14px rgba(210,177,132,.22); min-width: 0; }
html:not(#rs):not(#td1) .card-wrap .td-diary > details.note-toggle { margin: 0; }
html:not(#rs):not(#td1) .card-wrap .td-diary details.note-toggle > summary { background: none !important; display: block; list-style: none; padding: 0; border: 0; cursor: pointer; min-height: 48px; -webkit-tap-highlight-color: transparent; }
html:not(#rs):not(#td1) .card-wrap .td-diary details.note-toggle > summary::-webkit-details-marker { display: none; }
.td-d-head { display: flex; align-items: center; gap: .5rem; flex-wrap: nowrap; min-width: 0; }
.td-d-ic { font-size: 1.15rem; line-height: 1; }
.td-d-t { white-space: nowrap; font-family: 'Special Elite', 'IBM Plex Mono', monospace; font-size: 1.1rem; color: var(--ink); letter-spacing: .02em; flex: 1 1 auto; min-width: 0; }
.td-d-priv { flex: 0 0 auto; font-family: 'IBM Plex Mono', monospace; font-size: .6rem; letter-spacing: .05em; text-transform: uppercase; padding: .2rem .5rem; border-radius: 999px; border: 1px solid #d2b184; color: #d2b184; white-space: nowrap; }
.td-d-chev { flex: 0 0 auto; width: .6rem; height: .6rem; border-right: 2px solid #d2b184; border-bottom: 2px solid #d2b184; transform: rotate(45deg); transition: transform .2s; margin: 0 .2rem 0 .1rem; }
.td-diary details[open] .td-d-chev { transform: rotate(-135deg); border-color: var(--marvel-red); }
.td-d-sub { display: block; margin: .3rem 0 0; font-size: .86rem; line-height: 1.35; color: var(--ink-soft); overflow-wrap: anywhere; }
.td-d-prev { display: block; margin: .5rem 0 0; padding: .55rem .7rem; border-left: 3px solid var(--marvel-red); border-radius: 0 8px 8px 0; background: rgba(0,0,0,.14); font-size: .92rem; line-height: 1.4; color: var(--ink); overflow-wrap: anywhere; }
.td-d-pt { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.td-d-prev.td-empty { color: var(--ink-soft); font-style: italic; }
.td-d-prev.td-empty .td-d-pt { -webkit-line-clamp: 2; }
.td-diary details[open] .td-d-prev { display: none; }
html:not(#rs):not(#td1) .card-wrap .td-diary .user-note-box { margin-top: .7rem; }
html:not(#rs):not(#td1) .card-wrap .td-diary textarea.user-note { display: block; width: 100%; min-height: 7.5rem; font-size: 16px; line-height: 1.45; padding: .7rem .8rem; border: 2px solid #d2b184; border-radius: 10px; background: var(--paper); color: var(--ink); resize: vertical; box-sizing: border-box; -webkit-text-size-adjust: 100%; }
html:not(#rs):not(#td1) .card-wrap .td-diary textarea.user-note:focus { outline: 2px solid var(--marvel-red); outline-offset: 2px; border-color: var(--marvel-red); }
.td-d-hint { margin: .5rem 0 0; font-size: .74rem; line-height: 1.4; color: var(--ink-soft); }
.td-d-bar { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .6rem; }
.td-btn { font: inherit; font-family: 'IBM Plex Mono', monospace; font-size: .78rem; letter-spacing: .05em; min-height: 46px; padding: .55rem .95rem; border-radius: 10px; border: 1px solid #d2b184; background: transparent; color: var(--ink); cursor: pointer; -webkit-tap-highlight-color: transparent; }
.td-btn:focus-visible { outline: 2px solid var(--marvel-red); outline-offset: 2px; }
.td-btn-main { background: #8f1d2a; border-color: #d2b184; color: #fff; font-weight: 700; }
.td-btn-danger { border-color: #c0303f; color: var(--ink); background: rgba(143,29,42,.25); }
.td-cta { display: block; width: 100%; margin-top: .7rem; min-height: 50px; font-size: .88rem; box-shadow: 0 0 12px rgba(160,30,40,.45); }
.td-diary.td-open .td-cta { display: none; }
.td-d-confirm { margin-top: .6rem; padding: .7rem; border: 1px solid var(--marvel-red); border-radius: 10px; background: rgba(160,30,40,.12); font-size: .88rem; line-height: 1.4; color: var(--ink); }
.td-d-confirm[hidden], .td-d-bar [hidden], .td-d-del[hidden] { display: none !important; }

/* Pulsanti finali */
html:not(#rs):not(#td1) .card-wrap .td-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .5rem; margin: .7rem 0 .5rem; align-items: stretch; }
html:not(#rs):not(#td1) .card-wrap .td-actions > details.watch-picker { margin: 0; min-width: 0; }
html:not(#rs):not(#td1) .card-wrap .td-actions > details.watch-picker[open] { grid-column: 1 / -1; grid-row: 2; }
html:not(#rs):not(#td1) .card-wrap .td-actions > details.watch-picker > summary, html:not(#rs):not(#td1) .card-wrap .td-actions > label.local-file-btn { display: flex; align-items: center; justify-content: center; gap: .4rem; min-height: 50px; margin: 0; padding: .6rem .8rem; border-radius: 10px; border: 1px solid #d2b184; font-weight: 700; letter-spacing: .05em; text-align: center; box-sizing: border-box; width: 100%; cursor: pointer; -webkit-tap-highlight-color: transparent; }
html:not(#rs):not(#td1) .card-wrap .td-actions > details.watch-picker > summary { background: #8f1d2a !important; border-color: #d2b184 !important; color: #fff !important; }
html:not(#rs):not(#td1) .card-wrap .td-actions > label.local-file-btn { background: rgba(210,177,132,.10) !important; color: var(--ink) !important; border-color: #d2b184 !important; grid-column: 2; grid-row: 1; }
html:not(#rs):not(#td1) .card-wrap .td-actions > details.watch-picker > summary *, html:not(#rs):not(#td1) .card-wrap .td-actions > label.local-file-btn * { color: inherit !important; }
@media (max-width: 340px) { html:not(#rs):not(#td1) .card-wrap .td-actions { grid-template-columns: minmax(0, 1fr); } html:not(#rs):not(#td1) .card-wrap .td-actions > label.local-file-btn { grid-column: 1; grid-row: auto; } }
html:not(#rs):not(#td1) .card-wrap .watch-picker-opts { display: flex; flex-wrap: wrap; gap: .45rem; padding: .6rem 0 0; }
html:not(#rs):not(#td1) .card-wrap .watch-picker-opts .watch-plat-btn { min-height: 44px; display: inline-flex; align-items: center; }
/* spazio per barra inferiore fissa e safe area */
html:not(#rs):not(#td1) .card-wrap { scroll-margin-bottom: calc(5.5rem + env(safe-area-inset-bottom)); }
/* TD1-CSS-END */
</style>
'''
rep('<style id="m1-css">',CSS+'<style id="m1-css">','TD1-CSS')

JS=r'''<script id="td1-js">/* TD1: restyling schede + Diario TVA. Solo presentazione: lo storage resta al blocco note esistente (textarea .user-note, NOTES_KEY). */
(function () {
  'use strict';
  var BYPASS = false;
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function norm(t) { return String(t || '').replace(/\s+/g, ' ').trim(); }
  function enhance(w, total) {
    if (w.getAttribute('data-td1')) return; w.setAttribute('data-td1', '1');
    var card = w.querySelector(':scope > details.card'); if (!card) return;
    var panel = card.querySelector(':scope > .detail-panel');
    /* 1) Info principali: card compatta (gli elementi originali vengono solo raggruppati, non modificati) */
    if (panel && !panel.querySelector(':scope > .td-info')) {
      var first = panel.querySelector(':scope > details.sub-group');
      var rows = Array.prototype.filter.call(panel.children, function (c) {
        return c.classList.contains('detail-row') && !c.classList.contains('tva-row') && (!first || (c.compareDocumentPosition(first) & 4));
      });
      if (rows.length) {
        var info = el('div', 'td-info'); panel.insertBefore(info, rows[0]);
        var pos = el('div', 'detail-row td-pos');
        var rec = card.querySelector('summary .rec'); var n = rec ? norm(rec.textContent) : '';
        pos.innerHTML = '<span class="detail-k">POSIZIONE CRONOLOGICA</span><span class="detail-v"></span>';
        pos.lastChild.textContent = (n || 'N°—') + (total ? ' su ' + total : '');
        rows.forEach(function (r, i) {
          var k = r.querySelector('.detail-k'); var kt = k ? norm(k.textContent).toUpperCase() : '';
          var v = r.querySelector('.detail-v'); var long = v && norm(v.textContent).length > 38;
          if (kt.indexOf('PERSONAGGI') === 0 || long) r.classList.add('td-wide');
          info.appendChild(r);
          if (kt.indexOf('DURATA') === 0) info.appendChild(pos);
        });
        if (!pos.parentNode) info.appendChild(pos);
      }
    }
    /* 2) Diario TVA */
    var nt = card.querySelector(':scope > details.note-toggle'); var ta = nt && nt.querySelector('textarea.user-note');
    var tEl = w.querySelector('.title'); var titolo = tEl ? norm(tEl.textContent) : 'questo titolo';
    if (nt && ta) {
      var box = el('div', 'td-diary'); card.insertBefore(box, nt); box.appendChild(nt);
      var sum = nt.querySelector(':scope > summary');
      if (sum) {
        sum.innerHTML = '';
        var head = el('span', 'td-d-head'); head.appendChild(el('span', 'td-d-ic', '&#128212;')); head.appendChild(el('span', 'td-d-t', 'Diario TVA'));
        head.appendChild(el('span', 'td-d-priv', '&#128274; Privato')); head.appendChild(el('span', 'td-d-chev'));
        sum.appendChild(head);
        var sub = el('span', 'td-d-sub'); sub.textContent = 'Le tue note personali su ' + titolo; sum.appendChild(sub);
        var prev = el('span', 'td-d-prev'), pt = el('span', 'td-d-pt'); prev.appendChild(pt); sum.appendChild(prev);
        ta.setAttribute('aria-label', 'Nota personale su ' + titolo); ta.setAttribute('maxlength', '100000'); ta.setAttribute('autocapitalize', 'sentences'); ta.setAttribute('rows', '5');
        ta.placeholder = 'Scrivi qui un tuo pensiero, un ricordo, un promemoria… si salva da solo.';
        var boxEl = nt.querySelector('.user-note-box');
        var hint = el('p', 'td-d-hint', '&#128274; Privato: la nota non viene condivisa con TVA Friends. Si salva da sola su questo dispositivo, anche offline.');
        var bar = el('div', 'td-d-bar'); var done = el('button', 'td-btn td-btn-main', 'Fatto'); done.type = 'button';
        var del = el('button', 'td-btn td-btn-danger td-d-del', '&#128465; Elimina nota'); del.type = 'button';
        bar.appendChild(done); bar.appendChild(del);
        var conf = el('div', 'td-d-confirm'); conf.hidden = true; conf.setAttribute('role', 'alertdialog');
        conf.innerHTML = '<p style="margin:0 0 .5rem"></p><div class="td-d-bar" style="margin:0"></div>';
        var cb = conf.lastChild, cy = el('button', 'td-btn td-btn-danger', 'S&igrave;, elimina'), cn = el('button', 'td-btn', 'Annulla'); cy.type = 'button'; cn.type = 'button'; cb.appendChild(cy); cb.appendChild(cn);
        boxEl.appendChild(hint); boxEl.appendChild(bar); boxEl.appendChild(conf);
        var cta = el('button', 'td-btn td-btn-main td-cta', ''); cta.type = 'button'; box.appendChild(cta);
        var last = ta.value;
        function refresh() {
          var t = norm(ta.value), has = !!t;
          prev.className = 'td-d-prev' + (has ? '' : ' td-empty');
          pt.textContent = has ? t.slice(0, 240) : 'Ancora nessuna nota. Qui puoi scrivere un ricordo, un pensiero o un promemoria su questo titolo.';
          cta.textContent = has ? '✎ Modifica nota' : '+ Aggiungi una nuova nota';
          del.hidden = !has; box.classList.toggle('td-open', nt.open);
        }
        function askDelete(msg, onYes, onNo) { conf.firstChild.textContent = msg; conf.hidden = false; cy.onclick = function () { conf.hidden = true; onYes(); }; cn.onclick = function () { conf.hidden = true; onNo(); }; try { cn.focus(); } catch (e) {} }
        /* intercetta lo svuotamento del testo: la nota si elimina solo dopo conferma (il salvataggio originale non parte finche' non confermi) */
        nt.addEventListener('input', function (ev) {
          if (ev.target !== ta || BYPASS) return;
          if (!norm(ta.value) && norm(last)) {
            ev.stopPropagation();
            var keep = last;
            askDelete('Hai svuotato la nota: eliminarla definitivamente?', function () { BYPASS = true; ta.value = ''; ta.dispatchEvent(new Event('input', { bubbles: true })); BYPASS = false; last = ''; refresh(); }, function () { ta.value = keep; refresh(); });
            return;
          }
          last = ta.value; conf.hidden = true; refresh();
        }, true);
        del.addEventListener('click', function () {
          askDelete('Eliminare definitivamente questa nota? L’operazione non si può annullare.', function () { BYPASS = true; ta.value = ''; ta.dispatchEvent(new Event('input', { bubbles: true })); BYPASS = false; last = ''; refresh(); }, function () {});
        });
        done.addEventListener('click', function () { conf.hidden = true; nt.open = false; refresh(); try { sum.scrollIntoView({ block: 'nearest' }); } catch (e) {} });
        cta.addEventListener('click', function () { nt.open = true; refresh(); try { ta.focus({ preventScroll: false }); var l = ta.value.length; ta.setSelectionRange(l, l); } catch (e) {} });
        nt.addEventListener('toggle', refresh);
        refresh();
      }
    }
    /* 3) Pulsanti finali: Guarda + File locale affiancati (stessi elementi, stessi handler) */
    var wp = card.querySelector(':scope > details.watch-picker'), lf = card.querySelector(':scope > label.local-file-btn');
    if (wp || lf) {
      var act = el('div', 'td-actions'); card.insertBefore(act, wp || lf);
      if (wp) act.appendChild(wp); if (lf) act.appendChild(lf);
      var anchor = card.querySelector(':scope > .td-diary'); if (anchor && anchor.nextSibling !== act) card.insertBefore(act, anchor.nextSibling);
    }
  }
  function run() {
    var total = document.querySelectorAll('.card-wrap .user-note').length;
    var list = Array.prototype.slice.call(document.querySelectorAll('.card-wrap[data-item]')), i = 0;
    (function chunk() { var end = Math.min(i + 20, list.length); for (; i < end; i++) { try { enhance(list[i], total); } catch (e) { if (window.console) console.error('TD1', e); } } if (i < list.length) setTimeout(chunk, 0); })();
    /* se una scheda viene aperta prima del suo turno, la sistemo subito */
    document.addEventListener('toggle', function (ev) { var d = ev.target; if (d && d.matches && d.matches('details.card')) { var w = d.closest('.card-wrap[data-item]'); if (w) try { enhance(w, total); } catch (e) {} } }, true);
  }
  if (document.readyState === 'complete') setTimeout(run, 60); else window.addEventListener('load', function () { setTimeout(run, 60); });
})();
</script>
'''
rep("<script id=\"fa1-js\">",JS+"<script id=\"fa1-js\">",'id="td1-js"')

s=re.sub(r'(name="tva-build" content=")[^"]*',lambda m:m.group(1)+BUILD,s)
open(P,'w',encoding='utf-8').write(s)
w=open(SW,encoding='utf-8').read()
w=re.sub(r"const SW_BUILD = '[^']*';","const SW_BUILD = '%s';"%BUILD,w)
w=re.sub(r"const CACHE_NAME = '[^']*';","const CACHE_NAME = 'marvel-timeline-cache-%s';"%BUILD,w)
open(SW,'w',encoding='utf-8').write(w)
print('ok',BUILD)
