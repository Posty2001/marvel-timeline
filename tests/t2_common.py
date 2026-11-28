#!/usr/bin/env python3
"""Harness condiviso dei test Tessera 3.0 (server locale, profili seminati, apertura della Tessera). Copiato dal harness T0, senza eseguirne i test."""
import os, sys, json, http.server, threading, socket, functools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = 'marvel-ultimate-timeline-'
errs = []
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def handle(self):
        try: super().handle()
        except Exception: pass


s_ = socket.socket(); s_.bind(('127.0.0.1', 0)); port = s_.getsockname()[1]; s_.close()
srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/index.html' % port

PIXEL = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAIAAgDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDzmiiiuY+nP//Z'
ORDER = [str(i).zfill(3) for i in (1, 2, 3, 4, 5, 6, 7, 11, 12, 15, 16, 17, 22, 24, 41, 45, 47, 49, 50, 51, 53, 55, 56, 58, 59, 62, 63, 67, 70, 75, 76, 78)]


def prof_vuoto():
    return {}


def prof_medio():
    w = {i: True for i in ORDER[:12]}
    return {P + 'watched': json.dumps(w), P + 'ratings': json.dumps({ORDER[0]: 4, ORDER[1]: 5, ORDER[2]: 3}),
            P + 'notes': json.dumps({ORDER[0]: 'ok', ORDER[1]: 'bene'}), P + 'favorites': json.dumps({ORDER[0]: True, ORDER[3]: True})}


def prof_ricco():
    w = {i: True for i in ORDER}
    return {P + 'watched': json.dumps(w), P + 'ratings': json.dumps({i: 4 for i in ORDER[:14]}),
            P + 'notes': json.dumps({i: 'n' for i in ORDER[:6]}), P + 'favorites': json.dumps({i: True for i in ORDER[:9]})}


PROFILI = {'vuoto': prof_vuoto, 'medio': prof_medio, 'ricco': prof_ricco}

# profilo personale completo (gruppo B)
PERS = {
    P + 'user-name': 'Posty', P + 'tessera-id': 'VAR-402737',
    P + 'tessera-look': json.dumps({'v': 1, 'a': 'sentinella', 'b': [], 'ts': 1}),
    P + 'rewards': json.dumps({'v': 1, 'u': {'titolo-recluta-tva': '2026-11-10', 'cornice-bronzo-temporale': '2026-11-11', 'titolo-colui-che-rimane': '2026-11-12'},
                               'e': {'titolo': 'titolo-recluta-tva', 'cornice': 'cornice-bronzo-temporale'}, 't': {}}),
    P + 'tessera-photo': PIXEL,
}
PERS.update(prof_medio())
IDSEED = {'v': 1, 'emblem': 0, 'emx': 5, 'motto': 'Ordine e caos', 'univ': 'Terra-199999', 'ch': 'Loki', 'ts': 1700000000000}
STSEED = {'v': 1, 'bg': 'mist', 'tx': 'onde', 'ty': 'cinema', 'fr': 'doppia', 'ts': 1700000000000}
PERS_SEM = {P + 'identity-v1': IDSEED, P + 'tessera-style-v1': STSEED}
for _k, _v in PERS_SEM.items(): PERS[_k] = json.dumps(_v)

SEED_JS = """(d)=>{ if(localStorage.getItem('__t0seed')) return; localStorage.setItem('__t0seed','1');
  Object.keys(d).forEach(k=>localStorage.setItem(k, d[k])); }"""
READ_JS = """(pref)=>{ const o={}; for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i); if(k.indexOf(pref)===0) o[k]=localStorage.getItem(k);} return o; }"""


def boot(b, seed, w=390, h=844):
    c = b.new_context(viewport={'width': w, 'height': h}, has_touch=True, is_mobile=True, service_workers='block')
    c.add_init_script("(" + SEED_JS + ")(" + json.dumps(seed) + ")")
    pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto(URL); pg.wait_for_timeout(3000)
    pg.evaluate("()=>{try{journeyStarted.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"); pg.wait_for_timeout(700)
    return c, pg


def open_tessera(pg):
    pg.evaluate("()=>document.getElementById('appTabTessera').click()"); pg.wait_for_timeout(1500)


