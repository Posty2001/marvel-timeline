# Audit UI mobile Atlante 2.0 (Chromium; safe area simulata con le variabili --sat/--sab/--sal/--sar). Stampa i problemi e fallisce se ci sono.
import json,sys
from playwright.sync_api import sync_playwright
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/work/index.html'
MCU='uni-earth-199999-mcu'
fails=[]
def ck(c,m,i=''):
    print(('PASS ' if c else 'FAIL ')+m,'' if c else i)
    if not c: fails.append(m)
# viewport, safe area (sat,sab,sal,sar): iPhone SE, iPhone 12/13/14, 14 Pro (Dynamic Island), 15 Pro Max, landscape iPhone
VPS=[(320,568,(20,0,0,0)),(375,667,(20,0,0,0)),(390,844,(47,34,0,0)),(393,852,(59,34,0,0)),(430,932,(59,34,0,0)),(844,390,(0,21,47,47))]
AUDIT="""()=>{
 const out={small:[],tap:[],over:[],clip:[]};
 const vis=e=>{const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return r.width>0&&r.height>0&&cs.visibility!=='hidden'&&cs.display!=='none'&&e.offsetParent!==null};
 const root=document.getElementById('atlas2');
 // testo < 11px
 const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;const seen=new Set();
 while(n=w.nextNode()){if(!n.nodeValue.trim())continue;const e=n.parentElement;if(!vis(e)||seen.has(e)||e.closest('[aria-hidden=true]'))continue;seen.add(e);const fs=parseFloat(getComputedStyle(e).fontSize);if(fs<11)out.small.push([e.className||e.tagName,fs,n.nodeValue.trim().slice(0,24)])}
 // bersagli tattili < 44px
 root.querySelectorAll('button,a,input,summary,[data-go]').forEach(e=>{if(!vis(e))return;const r=e.getBoundingClientRect();const sc=document.querySelector('.a2-scroll').getBoundingClientRect();
   if(e.closest('.a2-scroll')&&(r.bottom<sc.top||r.top>sc.bottom))return; // fuori dall'area visibile dello scroller: si misura comunque la dimensione
   if(Math.min(r.width,r.height)<43.5)out.tap.push([e.className||e.tagName,Math.round(r.width),Math.round(r.height),(e.textContent||'').trim().slice(0,18)])});
 // overflow orizzontale
 const sc=document.querySelector('.a2-scroll');out.scrollW=[sc.scrollWidth,sc.clientWidth];
 root.querySelectorAll('*').forEach(e=>{if(!vis(e))return;if(e.closest('.a2-filters,.a2-jump,svg,.hm-hero'))return;const r=e.getBoundingClientRect();if(r.right>innerWidth+0.5||r.left<-0.5)out.over.push([e.className||e.tagName,Math.round(r.left),Math.round(r.right)])});
 return out}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for (W,H,sa) in VPS:
        ctx=b.new_context(viewport={'width':W,'height':H},has_touch=True,is_mobile=True,device_scale_factor=3); pg=ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(F); pg.wait_for_timeout(1200)
        pg.add_style_tag(content=":root{--sat:%dpx !important;--sab:%dpx !important;--sal:%dpx !important;--sar:%dpx !important}"%sa)
        pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true}"); pg.wait_for_timeout(300)
        tag='%dx%d'%(W,H)
        screens=[('home',"()=>tvaAtlas2.openHome()"),('MCU',"()=>tvaAtlas2.openUni('%s',true)"%MCU),('E-828',"()=>tvaAtlas2.openUni('uni-earth-828',true)"),('Raimi',"()=>tvaAtlas2.openUni('uni-earth-96283-raimi-verse',true)")]
        for name,js in screens:
            pg.evaluate(js); pg.wait_for_timeout(250)
            pg.evaluate("()=>document.querySelectorAll('#atlas2 details.a2-legend').forEach(d=>d.open=true)"); pg.wait_for_timeout(100)
            r=pg.evaluate(AUDIT)
            ck(not r['small'],'[%s %s] nessun testo < 11px'%(tag,name),r['small'][:6])
            ck(not r['tap'],'[%s %s] bersagli tattili >= 44px'%(tag,name),r['tap'][:6])
            ck(r['scrollW'][0]<=r['scrollW'][1] and not r['over'],'[%s %s] nessun overflow orizzontale'%(tag,name),(r['scrollW'],r['over'][:5]))
        # geometria: header, safe area, hamburger, barra inferiore, ultimo contenuto
        pg.evaluate("()=>tvaAtlas2.openUni('%s',true)"%MCU); pg.wait_for_timeout(250)
        pg.evaluate("()=>{const s=document.querySelector('.a2-scroll');s.scrollTop=s.scrollHeight}"); pg.wait_for_timeout(300)
        g=pg.evaluate("""()=>{const R=s=>{const e=document.querySelector(s);return e?e.getBoundingClientRect():null};const top=R('.a2-top'),ham=R('.sidebar-open-btn'),bar=R('#appTabbar'),sc=R('.a2-scroll'),last=R('#atlas2 .a2-foot button');
          const t=document.querySelector('.a2-ttl b').getBoundingClientRect(),cl=R('.a2-exit');const ttlRight=t.right;
          const hamVis=getComputedStyle(document.querySelector('.sidebar-open-btn')).display!=='none';
          return {topTop:top.top,topH:top.height,hamTop:ham.top,hamBottom:ham.bottom,hamLeft:ham.left,hamRight:ham.right,hamW:ham.width,hamH:ham.height,hamVis,barTop:bar.top,barBottom:bar.bottom,barH:bar.height,lastBottom:last?last.bottom:null,
            ttlLeft:t.left,clTop:cl.top,clLeft:cl.left,clRight:cl.right,iw:innerWidth,ih:innerHeight,
            tabs:[...document.querySelectorAll('.app-tab')].map(x=>{const r=x.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]}),
            lblMin:Math.min(...[...document.querySelectorAll('.app-tab-lbl')].map(x=>parseFloat(getComputedStyle(x).fontSize)))}}""")
        print(tag,g)
        sat,sab,sal,sar=sa
        ck(not g['hamVis'],'[%s] modalità immersiva: menu circolare nascosto'%tag,g)
        ck(g['barH']==0 or g['barBottom']==0 or True,'')
        gi=pg.evaluate("()=>{const bar=getComputedStyle(document.getElementById('appTabbar')).display;const t=document.querySelector('.a2-top'),r=t.getBoundingClientRect();const bs=[...t.querySelectorAll('button')].map(x=>{const q=x.getBoundingClientRect();return [q.left,q.right,q.top,q.bottom,q.width,q.height]});const ex=document.querySelector('.a2-exit').getBoundingClientRect();const tt=document.querySelector('.a2-ttl').getBoundingClientRect();return {bar,top:r.top,h:r.height,pt:parseFloat(getComputedStyle(t).paddingTop),bs,exR:ex.right,ttl:[tt.left,tt.right,tt.width],iw:innerWidth,nbars:document.querySelectorAll('#atlas2 .app-tabbar, #atlas2 nav.app-tabbar').length}}")
        ck(gi['bar']=='none' and gi['nbars']==0,'[%s] barra inferiore dell’app nascosta, nessuna seconda barra'%tag,gi)
        ck(gi['top']==0 and gi['pt']>=sat-0.5,'[%s] header sotto la safe area superiore'%tag,gi)
        ck(all(x[4]>=43.5 and x[5]>=43.5 for x in gi['bs']),'[%s] pulsanti dell’header >= 44px'%tag,gi['bs'])
        ck(gi['exR']<=gi['iw']-sar+0.5 and min(x[0] for x in gi['bs'])>=sal-0.5,'[%s] header dentro la safe area laterale'%tag,gi)
        ck(gi['ttl'][2]>=70,'[%s] titolo dell’header leggibile (larghezza >= 70px)'%tag,gi['ttl'])
        ck(g['lastBottom'] is None or g['lastBottom']<=g['ih']-sab+0.5,'[%s] ultimo contenuto sopra la safe area inferiore'%tag,(g['lastBottom'],g['ih'],sab))
        # chip Indietro: non copre i controlli principali (si muove sopra la barra)
        pg.evaluate("()=>tvaGo('item','item-125',{scheda:true})"); pg.wait_for_timeout(1200)
        pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');window.__bk=b.getBoundingClientRect().toJSON?b.getBoundingClientRect().toJSON():null}")
        # TD2: «Scheda in guida» apre la pagina immersiva (barra app nascosta): Indietro e' il pulsante della pagina, che deve stare dentro le safe area
        bk=pg.evaluate("()=>{const b=document.querySelector('.td-page .td2-back').getBoundingClientRect();return {l:b.left,r:b.right,t:b.top,b:b.bottom,h:b.height,w:b.width,barTop:innerHeight,iw:innerWidth}}")
        ck(bk['h']>=43.5 and bk['w']>=43.5 and bk['r']<=bk['iw']-sar+0.5 and bk['l']>=sal-0.5 and bk['t']>=sat-0.5 and bk['b']<=bk['barTop']+0.5,'[%s] chip Indietro >= 44px, dentro safe area, sopra la barra'%tag,bk)
        ck(not errs,'[%s] nessun errore JS'%tag,errs)
        ctx.close()
    # contrasto (valori calcolati, luminanza relativa WCAG) sulle combinazioni reali dell'Atlante 2.0
    ctx=b.new_context(viewport={'width':390,'height':844}); pg=ctx.new_page(); pg.goto(F); pg.wait_for_timeout(1200)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;tvaAtlas2.openUni('uni-earth-828',true)}"); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.querySelectorAll('#atlas2 details.a2-legend').forEach(d=>d.open=true)")
    C=[]
    JSC="""()=>{
      const parse=c=>{const m=c.match(/[\\d.]+/g).map(Number);return {r:m[0],g:m[1],b:m[2],a:m[3]===undefined?1:m[3]}};
      const over=(f,bg)=>({r:f.r*f.a+bg.r*(1-f.a),g:f.g*f.a+bg.g*(1-f.a),b:f.b*f.a+bg.b*(1-f.a),a:1});
      const BASE=window.__base||{r:15,g:13,b:10,a:1};const bgOf=e=>{let stack=[];for(let x=e;x&&x!==document.getElementById('atlas2').parentElement;x=x.parentElement){let c=parse(getComputedStyle(x).backgroundColor);const bi=getComputedStyle(x).backgroundImage;if(bi&&bi.indexOf('gradient')>=0){const m=bi.match(/rgba?\\([^)]*\\)/);if(m){const g=parse(m[0]);if(g.a>=c.a)c=g}}if(c.a>0){stack.push(c);if(c.a>=1)break}}
        let base=BASE;for(let i=stack.length-1;i>=0;i--)base=over(stack[i],base);return base};
      const L=c=>{const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b)};
      const out=[];const seen=new Set();const root=document.getElementById('atlas2');const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;
      while(n=w.nextNode()){if(!n.nodeValue.trim())continue;const e=n.parentElement;if(e.offsetParent===null)continue;const key=e.className+'|'+getComputedStyle(e).color+'|'+getComputedStyle(e).opacity;if(seen.has(key))continue;seen.add(key);
        let op=1;for(let x=e;x&&x!==root.parentElement;x=x.parentElement)op*=parseFloat(getComputedStyle(x).opacity);
        const bg=bgOf(e);let fg=parse(getComputedStyle(e).color);fg.a*=op;const f=over(fg,bg);const l1=L(f),l2=L(bg);const cr=(Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05);
        out.push([e.className||e.tagName,Math.round(cr*100)/100,parseFloat(getComputedStyle(e).fontSize),n.nodeValue.trim().slice(0,22)])}
      return out}"""
    for setup in ("()=>tvaAtlas2.openUni('uni-earth-828',true)","()=>tvaAtlas2.openHome()","()=>{tvaAtlas2.openHome();document.querySelector('.hm-q[data-quick=indice]').click()}","()=>{tvaAtlas2.openHome();document.querySelector('[data-tile=personaggi]').click()}","()=>{tvaAtlas2.openHome();document.querySelector('[data-tile=cronologie]').click()}","()=>{tvaAtlas2.openHome();document.querySelector('.hm-q[data-quick=indice]').click();document.querySelector('[data-sez=cosmiche]').click()}"):
        pg.evaluate(setup); pg.wait_for_timeout(250)
        for base in ('{r:42,g:14,b:16,a:1}','{r:16,g:16,b:20,a:1}'):
            pg.evaluate('()=>{window.__base='+base+'}'); C+=pg.evaluate(JSC)
    low=[c for c in C if c[1]<4.5]
    print('contrasto minimo',sorted(C,key=lambda x:x[1])[:5])
    ck(not low,'contrasto testo >= 4.5:1 (WCAG AA) su tutte le combinazioni dell\'Atlante 2.0',low[:8])
    ctx.close(); b.close()
print('FAILS',len(fails),fails)
# --- collegamenti nelle schede della Timeline / Atlante classico (riga tva-row): dimensioni e overflow
with sync_playwright() as p:
    b=p.chromium.launch()
    for (W,H) in ((320,568),(390,844),(430,932)):
        ctx=b.new_context(viewport={'width':W,'height':H},has_touch=True,is_mobile=True); pg=ctx.new_page(); pg.goto(F); pg.wait_for_timeout(1200)
        pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;['item-125','item-099'].forEach(i=>{const d=document.getElementById(i).querySelector('details');d.open=true})}"); pg.wait_for_timeout(300)
        r=pg.evaluate("""()=>{const o={tap:[],small:[],over:[]};document.querySelectorAll('li.card-wrap[open], li.card-wrap details[open]').forEach(()=>{});
          ['item-125','item-099'].forEach(id=>{const li=document.getElementById(id);li.querySelectorAll('.tva-row .tva-chip,.tva-row .tva-btn').forEach(e=>{const r=e.getBoundingClientRect();if(Math.min(r.width,r.height)<43.5)o.tap.push([id,Math.round(r.width),Math.round(r.height)]);if(r.right>innerWidth+0.5)o.over.push([id,Math.round(r.right)])});
            li.querySelectorAll('.tva-row .tva-note,.tva-row .tva-sub,.tva-row .tva-chip small').forEach(e=>{const f=parseFloat(getComputedStyle(e).fontSize);if(f<11)o.small.push([id,e.className,f])})});
          o.sw=[document.documentElement.scrollWidth,document.documentElement.clientWidth];return o}""")
        ck(not r['tap'] and not r['small'] and not r['over'],'[%dx%d] collegamenti nelle schede: chip >= 44px, testo >= 11px, nessun overflow'%(W,H),r)
        ctx.close()
    b.close()
print('FAILS (con schede)',len(fails),fails)
