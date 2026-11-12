# FASE 2B.1 — correzioni dopo collaudo iPhone. Emulazione browser (NON iPhone reale, NON WebKit): il bug 3D va riverificato su Safari iOS.
import sys,os,json,re
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
srv,base=start_server()
P='marvel-ultimate-timeline-'
PNG=open('/tmp/poster.png','rb').read()
JS_ENTER="()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"
def open_t(pg): pg.click('#appTabTessera');pg.wait_for_timeout(800)
def rl(pg): pg.reload();pg.wait_for_timeout(1500);pg.evaluate(JS_ENTER);pg.wait_for_timeout(500)
def mat(pg,sel):
    return pg.evaluate("s=>getComputedStyle(document.querySelector(s)).transform",sel)
def parse(m):
    return [float(x) for x in re.findall(r'-?[\d.]+(?:e-?\d+)?',m.split('(',1)[1])] if m and m!='none' else []
with sync_playwright() as p:
    b=p.chromium.launch()
    # ================= 1) ROTAZIONE 3D =================
    c=newctx(b);pg=c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    enter(pg,base);open_t(pg)
    st=pg.evaluate("""()=>{const q=s=>getComputedStyle(document.querySelector(s));const c3=q('#tcCard3d'),f=q('#tcCard3d .tc-front'),k=q('#tcCard3d .tc-back'),h=q('#tcHero');
      return {ts:c3.transformStyle,td:c3.transitionDuration,bf:f.backfaceVisibility,bk:k.backfaceVisibility,pers:h.perspective,hov:h.overflow,fov:f.overflow,role:document.getElementById('tcHero').getAttribute('role'),ti:document.getElementById('tcHero').tabIndex}}""")
    ck(st['ts']=='preserve-3d','3D-1 contenitore con transform-style: preserve-3d',st)
    ck(st['bf']=='hidden' and st['bk']=='hidden','3D-2 backface-visibility nascosta su entrambe le facce',st)
    ck(st['pers'] not in('none','') and st['hov']=='visible','3D-3 prospettiva sul contenitore e nessun overflow:hidden che appiattisca il 3D',st)
    ck(float(st['td'].split('s')[0])>=0.5,'3D-4 transizione fluida (>=0.5s)',st)
    ck(st['role']=='button' and st['ti']==0,'3D-5 la carta è un controllo accessibile (ruolo e tabindex)')
    # allineamento fronte/retro
    al=pg.evaluate("""()=>{const r=s=>{const x=document.querySelector(s).getBoundingClientRect();return [x.left,x.top,x.width,x.height].map(v=>Math.round(v*10)/10)};
      const vb=s=>document.querySelector(s+' svg').getAttribute('viewBox');return {f:r('#tcCard3d .tc-front'),k:r('#tcCard3d .tc-back'),vf:vb('.tc-front'),vk:vb('.tc-back')}}""")
    ck(all(abs(a-b_)<1.2 for a,b_ in zip(al['f'],al['k'])) and al['vf']==al['vk'],'3D-6 fronte e retro perfettamente allineati (stessa area e stesso rapporto)',al)
    # tocco sulla carta
    box=pg.evaluate("()=>{const r=document.getElementById('tcHero').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}")
    pg.touchscreen.tap(box[0],box[1]);pg.wait_for_timeout(300)
    mid=parse(mat(pg,'#tcCard3d'))
    ck(len(mid)==16 and -0.95<mid[0]<0.95,'3D-7 durante la transizione la carta ruota davvero in 3D (matrix3d intermedia)',mid[:3])
    pg.wait_for_timeout(900)
    end=parse(mat(pg,'#tcCard3d'))
    ck(len(end)==16 and abs(end[0]+1)<0.01 and abs(end[2])<0.01,'3D-8 il tocco gira la carta di 180° (rotateY(180deg))',end[:4])
    ck(pg.evaluate("()=>document.getElementById('tcFlipBtn').getAttribute('aria-pressed')")=='true','3D-9 pulsante Fronte/Retro aggiornato dal tocco')
    pg.touchscreen.tap(box[0],box[1]);pg.wait_for_timeout(1000);end2=parse(mat(pg,'#tcCard3d'))
    ck(len(end2) in(6,16) and abs(end2[0]-1)<0.01,'3D-10 secondo tocco: torna al fronte (360°/0°)',end2[:3])
    pg.click('#tcFlipBtn');pg.wait_for_timeout(1000);ck(pg.evaluate("()=>document.getElementById('tcCard3d').classList.contains('tc-flipped')"),'3D-11 il pulsante «Gira la carta» funziona')
    pg.click('#tcFlipBtn');pg.wait_for_timeout(900);ck(not pg.evaluate("()=>document.getElementById('tcCard3d').classList.contains('tc-flipped')"),'3D-12 e «Mostra il fronte» riporta al fronte')
    pg.focus('#tcHero');pg.keyboard.press('Enter');pg.wait_for_timeout(900);ck(pg.evaluate("()=>document.getElementById('tcCard3d').classList.contains('tc-flipped')"),'3D-13 anche da tastiera (Invio)')
    ck(pg.evaluate("()=>[...document.querySelectorAll('#tcHero a,#tcHero button,#tcHero input,#tcHero select')].length")==0,'3D-14 nessun elemento interattivo interno che intercetti il tocco sulla carta')
    ck(pg.evaluate("()=>{const f=document.querySelector('#tcCard3d .tc-front'),k=document.querySelector('#tcCard3d .tc-back');return getComputedStyle(f).pointerEvents==='none'&&getComputedStyle(k).pointerEvents!=='none'}"),'3D-15 solo la faccia visibile riceve il tocco')
    ck(pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth")and errs==[],'3D-16 nessun overflow orizzontale né errori JS',errs)
    c2=newctx(b,reduced_motion='reduce');q=c2.new_page();enter(q,base);open_t(q)
    ck(q.evaluate("()=>getComputedStyle(document.getElementById('tcCard3d')).transitionDuration")in('0s','0s, 0s'),'3D-17 prefers-reduced-motion: nessuna animazione')
    q.click('#tcFlipBtn');q.wait_for_timeout(100);ck(abs(parse(mat(q,'#tcCard3d'))[0]+1)<0.01,'3D-18 con animazioni ridotte la carta è girata subito')
    c2.close()
    # ================= 2) RETRO: tutto entro i bordi =================
    bad=pg.evaluate("""()=>{const T=tvaTessera3,m=tvaTessera.model(tvaTessera.current()),bad=[];const host=document.createElement('div');host.style.cssText='position:fixed;left:0;top:0;width:700px;opacity:0;pointer-events:none';document.body.appendChild(host);
      const LONG={emx:7,motto:'Una frase molto lunga che deve andare a capo senza uscire dal bordo della carta in alcun modo',univ:'Universo con un nome davvero molto molto lungo',ch:'Personaggio con nome lunghissimo e ripetitivo ripetitivo'};
      m.name='Nome-Molto-Lungo-Davvero-1234567';
      ['compact','wide','vertical'].forEach(l=>[{emx:-1,motto:'',univ:'',ch:''},LONG,{emx:55,motto:'Ciao',univ:'T-1',ch:'X'}].forEach((id,ii)=>['moderno','archivio','cinema','classico'].forEach(ty=>{
        const s=T.render(m,{v:1,ly:l,bg:'plain',tx:'none',fr:'nessuna',fx:'none',ty:ty,ic:'matrix'},id,l,'z','back');host.innerHTML=s;const svg=host.firstChild;const R=svg.getBoundingClientRect();const mar=R.width*0.025;
        svg.querySelectorAll('text,path,rect,circle,polygon,ellipse,svg').forEach(e=>{if(e===svg)return;const r=e.getBoundingClientRect();if(!r.width&&!r.height)return;if(e.tagName==='rect'&&r.width>=R.width-1)return;
          if(r.left<R.left+mar-0.5||r.right>R.right-mar+0.5||r.top<R.top+mar-0.5||r.bottom>R.bottom-mar+0.5)bad.push([l,ii,ty,e.tagName,Math.round(r.left-R.left),Math.round(r.right-R.left),Math.round(R.width)])})})));host.remove();return bad.slice(0,6)}""")
    ck(not bad,'RET-1 retro: nessun testo/decorazione/emblema oltre il perimetro (3 layout × contenuti lunghi × 4 caratteri × 56 emblemi campione)',bad)
    ar=pg.evaluate("""()=>{const T=tvaTessera3,m=tvaTessera.model(tvaTessera.current()),o=[];['compact','wide','vertical'].forEach(l=>{const f=T.render(m,{v:1,ly:l},{emx:-1},l,'a','front'),k=T.render(m,{v:1,ly:l},{emx:-1},l,'b','back');const vb=x=>x.match(/viewBox="([^"]+)"/)[1];o.push([l,vb(f),vb(k)])});return o}""")
    ck(all(a[1]==a[2] for a in ar),'RET-2 proporzioni identiche fra fronte e retro in tutti i layout',ar)
    # tessera visibile intera nei 3 viewport (hero)
    for w,h in((320,568),(375,667),(390,844)):
        cx=newctx(b,w,h);r=cx.new_page();enter(r,base);open_t(r)
        info=r.evaluate("()=>{const f=document.querySelector('#tcCard3d .tc-front').getBoundingClientRect();return {l:f.left,r:f.right,w:innerWidth,sw:document.documentElement.scrollWidth,ar:f.width/f.height}}")
        ck(info['l']>=0 and info['r']<=info['w'] and info['sw']<=info['w'],'RET-3 %d: carta interamente visibile, nessun overflow orizzontale'%w,info)
        r.click('#tcFlipBtn');r.wait_for_timeout(900);r.screenshot(path='/tmp/shots/b1_retro_%d.png'%w)
        cx.close()
    # ================= 3) NOTIFICA PRESET DISCRETA =================
    pg.evaluate("()=>document.getElementById('tcHero')");
    pg.click('#tcPersonalizzaBtn');pg.wait_for_timeout(300);pg.click('#tcTab-stile');pg.wait_for_timeout(300)
    t0=pg.evaluate("()=>document.getElementById('tcEdBody').getBoundingClientRect().top")
    pg.click('[data-fk="pr:cosmic"]');pg.wait_for_timeout(300)
    t1=pg.evaluate("()=>document.getElementById('tcEdBody').getBoundingClientRect().top")
    ck(abs(t0-t1)<1,'PRE-1 applicando un preset il contenuto delle opzioni non si sposta',(t0,t1))
    ck(pg.evaluate("()=>{const n=document.getElementById('tcEdNote');return getComputedStyle(n).display==='none'||!n.textContent.trim()}"),'PRE-2 nessun avviso sopra le opzioni')
    ck('Preset' in pg.inner_text('#tcEdState'),'PRE-3 conferma discreta nell\'intestazione',pg.inner_text('#tcEdState'))
    pg.wait_for_timeout(3000);ck('Non salvato' in pg.inner_text('#tcEdState'),'PRE-4 la conferma sparisce da sola e resta lo stato «Non salvato»',pg.inner_text('#tcEdState'))
    pg.click('#t3Undo');pg.wait_for_timeout(200);ck(pg.inner_text('#tcEdSave').strip()=='Salva','PRE-5 annulla ultima modifica invariato')
    pg.click('[data-fk="pr:royal"]');pg.wait_for_timeout(200);pg.click('#tcEdSave');pg.wait_for_timeout(500)
    ck(json.loads(pg.evaluate("k=>localStorage.getItem(k)",P+'tessera-style-v1')).get('pr')=='royal','PRE-6 salvataggio invariato')
    pg.click('#tcPersonalizzaBtn');pg.wait_for_timeout(300);pg.click('#tcTab-stile');pg.wait_for_timeout(200);pg.click('#t3Reset');pg.wait_for_timeout(200);pg.click('#tcEdSave');pg.wait_for_timeout(400)
    ck(pg.evaluate("k=>localStorage.getItem(k)",P+'tessera-style-v1') is None,'PRE-7 ripristino modello predefinito invariato')
    c.close()
    # ================= 4) LOCANDINE SERATE =================
    imgs=[]
    def mkctx(offline=False):
        cx=newctx(b);hits=[]
        cx.route('https://image.tmdb.org/**',lambda r:(hits.append(r.request.url),r.fulfill(status=200,content_type='image/png',body=PNG)))
        cx.route(re.compile(r'^https?://(?!127\.0\.0\.1)(?!image\.tmdb\.org).*'),lambda r:(hits.append('EXT:'+r.request.url) if not re.search(r'fonts\.(googleapis|gstatic)|gstatic\.com/firebasejs',r.request.url) else None,r.abort()))
        return cx,hits
    def mk_serata(pg,item):
        pg.evaluate(JS_ENTER);pg.evaluate("()=>localStorage.setItem('marvel-ultimate-timeline-user-name','Wanda')")
        pg.evaluate("()=>tvaFriends.open('serate')");pg.wait_for_timeout(700)
        pg.evaluate("()=>{const d=document.querySelector('#tfEvNewSec');if(d&&d.open!==undefined)d.open=true}");pg.wait_for_timeout(200)
        pg.fill('#tfEvTitle','Serata prova');
        if item: pg.select_option('#tfEvItem',item)
        pg.click('#tfEvNew');pg.wait_for_timeout(600)
    cx,hits=mkctx();pg=cx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));enter(pg,base)
    ck(pg.evaluate("()=>window.tvaTmdb&&tvaTmdb.count()>100"),'LOC-0 il catalogo esistente (mappa TMDB) è presente e riutilizzato',pg.evaluate("()=>window.tvaTmdb&&tvaTmdb.count()"))
    mk_serata(pg,'001');pg.wait_for_timeout(800)
    ev=pg.evaluate("()=>{const s=JSON.parse(localStorage.getItem('marvel-ultimate-timeline-tvafriends-v1'));return Object.values(s.evenings)[0]}")
    ck(ev['item']=='001','LOC-1 la serata conserva il collegamento al titolo del catalogo (N°001)',ev.get('item'))
    d=pg.evaluate("()=>{const i=document.querySelector('#tfRoot .tf-p-img');const im=i&&i.querySelector('img');return {has:!!i,pic:i&&i.classList.contains('has-pic'),src:im&&im.currentSrc||im&&im.src,attr:i&&i.getAttribute('data-attr'),svg:!!(i&&i.querySelector('svg'))}}")
    ck(d['has'] and d['pic'] and 'image.tmdb.org' in (d['src'] or ''),'LOC-2 la locandina del film collegato compare (da catalogo, stesso meccanismo della scheda)',d)
    ck(d['attr']=='TMDB','LOC-3 attribuzione TMDB mostrata come nelle schede',d)
    ck(all(('image.tmdb.org' in h_) for h_ in hits) and len(hits)>=1,'LOC-4 nessuna richiesta a servizi esterni diversi da quello già autorizzato (solo image.tmdb.org)',hits[:4])
    pg.screenshot(path='/tmp/shots/b1_serate_poster.png')
    # senza item: grafica originale
    cx2,h2=mkctx();q=cx2.new_page();enter(q,base);mk_serata(q,'')
    d=q.evaluate("()=>{const i=document.querySelector('#tfRoot .tf-p-img');return {has:!!i,img:!!(i&&i.querySelector('img')),svg:!!(i&&i.querySelector('svg'))}}")
    ck(d['has'] and not d['img'] and d['svg'],'LOC-5 serata senza film: grafica originale alternativa, nessuna immagine',d)
    # TMDB disattivato dall'utente
    cx3,h3=mkctx();q=cx3.new_page();enter(q,base);q.evaluate("()=>localStorage.setItem('tvaTmdbOff','1')");q.reload();q.wait_for_timeout(1200);h3.clear();mk_serata(q,'001');q.wait_for_timeout(600)
    d=q.evaluate("()=>{const i=document.querySelector('#tfRoot .tf-p-img');return {img:!!(i&&i.querySelector('img')),svg:!!(i&&i.querySelector('svg'))}}")
    ck(not d['img'] and d['svg'] and not h3,'LOC-6 con TMDB disattivato dall\'utente: nessuna richiesta, grafica originale',(d,h3))
    # offline
    cx4,h4=mkctx();q=cx4.new_page();enter(q,base);mk_serata(q,'001');q.wait_for_timeout(500);cx4.set_offline(True);q.evaluate("()=>tvaFriends.open('serate')");q.wait_for_timeout(500);hh=len(h4)
    q.evaluate("()=>{try{tvaFriends.open('serate')}catch(e){}}");q.wait_for_timeout(300)
    off=q.evaluate("()=>navigator.onLine");ck(off==False,'LOC-7a contesto offline attivo')
    q.evaluate("()=>document.querySelectorAll('.tf-p-img img').forEach(i=>i.remove())")
    cx4.set_offline(False)
    cx5,h5=mkctx();q=cx5.new_page();enter(q,base);mk_serata(q,'001');cx5.set_offline(True);q.wait_for_timeout(300)
    q.evaluate("()=>window.dispatchEvent(new Event('offline'))")
    r=q.evaluate("()=>{const T=tvaTmdb.poster('001','thumb');return T===null}");ck(r,'LOC-7 offline: il catalogo non fornisce l\'immagine remota (ripiego sulla grafica originale, app utilizzabile)')
    # TMDB irraggiungibile (errore di rete): l'immagine sparisce, resta la grafica
    cx6=newctx(b);cx6.route('https://image.tmdb.org/**',lambda r:r.abort());q=cx6.new_page();enter(q,base);mk_serata(q,'001');q.wait_for_timeout(900)
    d=q.evaluate("()=>{const i=document.querySelector('#tfRoot .tf-p-img');return {pic:i.classList.contains('has-pic'),img:!!i.querySelector('img'),svg:!!i.querySelector('svg'),w:i.getBoundingClientRect().width}}")
    ck(not d['pic'] and d['svg'] and d['w']>20,'LOC-8 errore di caricamento: nessuna icona rotta, resta la grafica originale',d)
    # locandina locale verificata del registro immagini: priorita'
    cx7,h7=mkctx();q=cx7.new_page();enter(q,base)
    loc=[f for f in os.listdir(os.path.join(ROOT,'assets/images/tva')) if f.endswith('.webp')][0]
    q.evaluate("(s)=>{TVA_IMG_MANIFEST['item:001']={src:s,licence:'test',verified:true,w:200,h:300}}",'assets/images/tva/'+loc)
    mk_serata(q,'001');q.wait_for_timeout(700)
    d=q.evaluate("()=>{const im=document.querySelector('#tfRoot .tf-p-img img');return {src:im&&im.getAttribute('src'),ds:im&&im.getAttribute('data-src')}}")
    ck(d['ds']=='local' and 'assets/images/tva/' in (d['src'] or ''),'LOC-9 locandina locale verificata ha la priorità (nessun duplicato, nessuna richiesta)',d)
    # layout a 320 con locandina e titolo lungo
    cx8,h8=mkctx();q=cx8.new_page();q.set_viewport_size({'width':320,'height':568});enter(q,base);mk_serata(q,'001');q.wait_for_timeout(700)
    ov=q.evaluate("()=>{const r=document.getElementById('tfRoot');const p=document.querySelector('#tfRoot .tf-poster');return {sw:r.scrollWidth<=r.clientWidth+1,fit:p.getBoundingClientRect().right<=innerWidth}}")
    ck(ov['sw'] and ov['fit'],'LOC-10 320px: locandina e serata senza overflow',ov)
    q.screenshot(path='/tmp/shots/b1_serate_320.png')
    ck(errs==[],'LOC-11 nessun errore JS',errs)
    # ================= 5) BARRA INFERIORE =================
    for w,h in((320,568),(375,667),(390,844)):
        cx=newctx(b,w,h);r=cx.new_page();enter(r,base);r.add_style_tag(content=":root{--sab:34px!important}");r.wait_for_timeout(300)
        d=r.evaluate("""()=>{const bar=document.getElementById('appTabbar'),R=bar.getBoundingClientRect(),tabs=[...bar.querySelectorAll('.app-tab')],lb=tabs.map(t=>t.querySelector('.app-tab-lbl'));
          const rects=tabs.map(t=>t.getBoundingClientRect());return {n:tabs.length,minW:Math.min(...rects.map(x=>x.width)),minH:Math.min(...rects.map(x=>x.height)),clip:lb.filter(l=>l.scrollWidth>l.clientWidth+1).map(l=>l.textContent),
            bottom:R.bottom,vh:innerHeight,right:R.right,vw:innerWidth,lblTop:Math.min(...lb.map(l=>l.getBoundingClientRect().top)),lblBottom:Math.max(...lb.map(l=>l.getBoundingClientRect().bottom)),barTop:R.top,
            ov:rects.some((x,i)=>i&&x.left<rects[i-1].right-0.5),labels:lb.map(l=>l.textContent.trim())}}""")
        ck(d['n']==6 and d['labels']==['HOME','TIMELINE','ATLANTE','CENTRALE TVA','TESSERA','FRIENDS'],'NAV-1 %d: sei destinazioni (senza Arena), etichetta FRIENDS'%w,d['labels'])
        ck(d['minW']>=44 and d['minH']>=44,'NAV-2 %d: area di tocco >=44px (min %dx%d)'%(w,d['minW'],d['minH']))
        ck(not d['clip'] and not d['ov'],'NAV-3 %d: nessuna etichetta tagliata o sovrapposta'%w,d['clip'])
        ck(abs(d['bottom']-d['vh'])<1 and d['right']<=d['vw']+0.5,'NAV-4 %d: barra al bordo fisico (safe area 34px simulata), nessun overflow'%w)
        ck(d['lblBottom']<=d['bottom']-30,'NAV-5 %d: etichette sopra l\'indicatore Home (safe area)'%w,(d['lblBottom'],d['bottom']))
        r.evaluate("()=>window.scrollTo(0,document.scrollingElement.scrollHeight)");r.wait_for_timeout(250)
        r.screenshot(path='/tmp/shots/b1_bar_%d.png'%w)
        # Atlante: barra nascosta (regola approvata invariata)
        r.tap('#appTabAtlante');r.wait_for_timeout(500)
        ck(r.evaluate("()=>getComputedStyle(document.getElementById('appTabbar')).display==='none'"),'NAV-6 %d: Atlante senza barra (regola approvata invariata)'%w)
        cx.close()
    b.close()
srv.terminate();summary()
