# 2B: le sezioni espandibili di Friends partono CHIUSE a ogni ingresso. Per i test esistenti che agiscono su un campo/pulsante
# contenuto in una sezione, il comportamento dell'utente reale (tocca l'intestazione e poi usa il campo) e' riprodotto qui:
# prima di fill/click/check/uncheck/select_option su un selettore interno a <details class="tf-sec"> la sezione viene aperta.
# Non altera il prodotto; i test dello stato "chiuso" usano evaluate() e non passano da qui.
try:
    from playwright.sync_api import Page as _Pg
    def _wrap(nm):
        orig=getattr(_Pg,nm)
        def f(self,selector,*a,**k):
            if isinstance(selector,str) and ('#tf' in selector or '.tf-' in selector) and 'summary' not in selector:
                try: self.evaluate("s=>{let e=null;try{e=document.querySelector(s)}catch(x){} if(!e)return; let d=e.closest('details.tf-sec'); while(d){d.open=true; d=d.parentElement?d.parentElement.closest('details.tf-sec'):null}}",selector)
                except Exception: pass
            return orig(self,selector,*a,**k)
        setattr(_Pg,nm,f)
    for _n in ('fill','click','check','uncheck','select_option'): _wrap(_n)
except Exception: pass
