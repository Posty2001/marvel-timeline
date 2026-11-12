# TVA Friends - controlli pre-rilascio: cloud disattivato a runtime, F-A2/F-A3 spenti, import/export sicuri, file alterati rifiutati.
import json,re,os,sys,socket,subprocess,time,base64,tempfile
ROOT=os.environ.get('TVA_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def freeport():
    s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); return p
PORT=freeport()
SRV=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1','--directory',ROOT],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1.2)
from playwright.sync_api import sync_playwright
U='http://127.0.0.1:%d/index.html'%PORT
fails=[]
def ck(c,m,i=''):
    print(('PASS ' if c else 'FAIL ')+m,'' if c else i)
    if not c: fails.append(m)
KEY='marvel-ultimate-timeline-tvafriends-v1'
SEC='SEGRETO-DIARIO-XYZ'
LS={'marvel-ultimate-timeline-watched':json.dumps({"001":True,"002":True}),'marvel-ultimate-timeline-notes':json.dumps({"001":SEC}),'marvel-ultimate-timeline-ratings':json.dumps({"001":4.5})}
def fnv(s):
    h=2166136261
    for ch in s:
        for u in ([ord(ch)] if ord(ch)<0x10000 else [0xD800+((ord(ch)-0x10000)>>10),0xDC00+((ord(ch)-0x10000)&1023)]):
            h^=u; h=(h*16777619)&0xFFFFFFFF
    return '%08x'%h
def b64(s): return base64.urlsafe_b64encode(s.encode('utf-8')).decode().rstrip('=')
def forge(o): j=json.dumps(o,separators=(',',':'),ensure_ascii=True); return 'TVA1.'+b64(j)+'.'+fnv(j)
def card(vid='vabcdefgh12',name='Eve'): return {'vid':vid,'name':name,'emblem':1,'color':1}
def msg(t,b,**k):
    m={'v':1,'id':'m_abcdefgh1234','t':t,'ts':int(time.time()*1000),'from':card(),'b':b}; m.update(k); return m
def mk(b):
    cx=b.new_context(viewport={'width':390,'height':844},service_workers='block',accept_downloads=True); pg=cx.new_page(); pg.errs=[]; pg.net=[]; pg.dlgs=[]
    pg.on('pageerror',lambda e:pg.errs.append(str(e))); pg.on('request',lambda r: pg.net.append(r.url))
    def dlg(d): pg.dlgs.append(d.message); d.accept()
    pg.on('dialog',dlg)
    pg.add_init_script("if(!sessionStorage.getItem('__s')){sessionStorage.setItem('__s','1');"+"".join("localStorage.setItem(%s,%s);"%(json.dumps(k),json.dumps(v)) for k,v in LS.items())+"}")
    pg.route('**/*',lambda r: r.abort() if any(h in r.request.url for h in ('gstatic','googleapis','firebaseio','tmdb','identitytoolkit')) else r.continue_())
    return cx,pg
def start(pg):
    pg.goto(U); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    pg.evaluate("()=>tvaFriends.open('nexus')"); pg.wait_for_timeout(300)
def st(pg): return pg.evaluate("(k)=>localStorage.getItem(k)",KEY) or '{}'
def imp(pg,c):
    pg.evaluate("()=>{const d=document.getElementById('tfImp'); if(d) d.open=true}")
    pg.fill('#tfImpText',c); pg.click('#tfImpBtn'); pg.wait_for_timeout(250); return pg.inner_text('#tfToast')
def others(pg): return {k:v for k,v in pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}").items() if k not in (KEY,'marvel-ultimate-timeline-auto-backup','marvel-ultimate-timeline-user-name','marvel-ultimate-timeline-fav-char','marvel-ultimate-timeline-identity-v1','marvel-ultimate-timeline-identity-premigration-v1','marvel-ultimate-timeline-tessera-id')}  # Friends 2.0: nome/personaggio/identity sono l'identita' condivisa con la Tessera (per design)
html=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
ck('var CLOUD_ENABLED = false;' in html and 'var ACCT_SYNC_ENABLED = false;' in html,'build: CLOUD_ENABLED=false e ACCT_SYNC_ENABLED=false')
with sync_playwright() as p:
    b=p.chromium.launch(); cx,pg=mk(b); start(pg)
    # --- 1) cloud disattivato a runtime
    ck(pg.evaluate("()=>tvaFriends.cloudEnabled")in(False,None) or pg.evaluate("()=>String(tvaFriends.cloudEnabled)")=='false','runtime: tvaFriends.cloudEnabled falso')
    ck(pg.query_selector('#tfCloudNote') is None or 'non attivo' in pg.evaluate("()=>{const e=document.getElementById('tfCloudNote');return e?e.textContent:'non attivo'}"),'UI: nota cloud non attivo')
    pg.evaluate("()=>tvaFriends.open('varianti')"); pg.wait_for_timeout(200)
    txt=pg.inner_text('#tfRoot')
    ck('Pubblica la mia Variante nel cloud' not in txt and 'Invia nel cloud' not in txt,'UI: nessun comando cloud esposto')
    # gate account F-A2/F-A3
    s0=pg.evaluate("()=>JSON.stringify(window.tvaAccountSync&&tvaAccountSync.state())")
    pg.evaluate("()=>{try{tvaAccountSync.connect()}catch(e){}try{tvaAccountSync.backupNow()}catch(e){}}"); pg.wait_for_timeout(500)
    ck(pg.evaluate("()=>JSON.stringify(tvaAccountSync.state())")==s0,'F-A2/F-A3: connect/backupNow inerti (stato invariato)')
    DATA=r'firebaseio|identitytoolkit|securetoken|firestore'
    ck(not [u for u in pg.net if re.search(DATA,u)],'rete: nessuna richiesta dati/auth Firebase (il solo SDK statico e\' baseline F-A1)',[u for u in pg.net if re.search(DATA,u)][:3])
    ck(not [u for u in pg.net if re.search(r'/(handles|inbox|users|friends|links|blocked)/',u)],'rete: nessun percorso handles/inbox/users')
    # --- 2) dati locali Friends non sovrascrivono altro
    base=others(pg)
    s_start=st(pg)
    pg.evaluate("()=>tvaFriends.open('nexus')"); pg.wait_for_timeout(200)
    pg.evaluate("()=>tvaFriends.open('varianti')"); pg.wait_for_timeout(200); pg.evaluate("()=>document.querySelectorAll('#tfRoot details.tf-sec').forEach(d=>{d.open=true})"); pg.fill('#tfName','Alice'); pg.click('#tfSaveMe'); pg.wait_for_timeout(200)
    pg.evaluate("()=>tvaFriends.open('nexus')"); pg.wait_for_timeout(200); pg.click('text=Crea invito Nexus')
    pg.wait_for_timeout(200)
    code=pg.input_value('#tfOutCode') if pg.query_selector('#tfOutCode') else ''
    ck(code.startswith('TVA1.'),'nexus: codice invito generato')
    # export .tvafriends: scarica e scansiona
    if pg.query_selector('text=Scarica file'):
        with pg.expect_download() as d: pg.click('text=Scarica file')
        dp=d.value; path=tempfile.mktemp(); dp.save_as(path); body=open(path,encoding='utf-8').read()
        ck(dp.suggested_filename.endswith('.tvafriends'),'export: estensione .tvafriends')
        ck(body.strip()==code,'export: il file contiene solo il codice mostrato')
        ck(SEC not in body,'export: nessun contenuto del Diario')
        dec=json.loads(base64.urlsafe_b64decode(body.split('.')[1]+'==').decode())
        flat=json.dumps(dec)
        ck(SEC not in flat and '4.5' not in flat and 'watched' not in flat,'export: nessun dato di diario/voti/progressi')
        ck(set(dec.keys())<={'v','id','t','ts','from','b','to'} and set(dec['from'].keys())<={'vid','name','emblem','color','motto','univ','ch','tid'},'export: solo campi previsti',list(dec.keys()))
    else: ck(False,'export: pulsante Scarica file presente')
    o1=others(pg); ck(o1==base,'dati locali Friends non alterano nessun altra chiave',[k for k in set(o1)|set(base) if o1.get(k)!=base.get(k)])
    ab=pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-auto-backup')") or ''
    ck('tvafriends' not in ab and not any(('"'+k+'"') in ab for k in ('nexus','pendingOut','reqs','teams','evenings','duels','inbox','msgs')),'auto-backup dell\'app (scritto dall\'app stessa) non contiene dati Friends (nexus, squadre, serate, duelli, messaggi); il solo nome condiviso con la Tessera e\' nel profilo, come prima')
    # --- 3) import alterati/malformati
    s_before=st(pg)
    good=forge(msg('nx.invite',{'nonce':'abcdefgh12345678'}))
    bad={'prefisso':'TVB1.'+good[5:],'troncato':good[:-12],'checksum errato':good[:-1]+('0' if good[-1]!='0' else '1'),'base64 rotto':'TVA1.@@@@.'+good.split('.')[2],'vuoto':'   ',
      'json non valido con checksum valido':'TVA1.'+b64('{not json')+'.'+fnv('{not json'),
      'tipo sconosciuto':forge(msg('x.evil',{})),'versione 2':forge({**msg('nx.invite',{'nonce':'abcdefgh12345678'}),'v':2}),
      'id non valido':forge({**msg('nx.invite',{'nonce':'abcdefgh12345678'}),'id':'../../etc'}),'mittente mancante':forge({k:v for k,v in msg('nx.invite',{'nonce':'abcdefgh12345678'}).items() if k!='from'}),
      'vid mittente non valido':forge({**msg('nx.invite',{'nonce':'abcdefgh12345678'}),'from':card('V<script>')}),
      'troppo lungo':'TVA1.'+'A'*30000+'.00000000','array al posto di oggetto':'TVA1.'+b64('[1,2]')+'.'+fnv('[1,2]')}
    for k,c in bad.items():
        r=imp(pg,c); ck(st(pg)==s_before,'import rifiutato senza modifiche: '+k,r)
    ck(not pg.errs,'nessun errore JS durante gli import alterati',pg.errs[:2])
    # nonce invalido su nx.invite, indirizzato ad altri, mittente non collegato per team.state
    for k,c in {'nx.invite senza nonce':forge(msg('nx.invite',{})),'team.state da non collegato':forge(msg('team.state',{'team':{'id':'t_abcdefgh1234'}})),
                'ev.rsvp da non collegato':forge(msg('ev.rsvp',{'ev':'e_abcdefgh1234','rsvp':'si'})),'destinatario diverso':forge(msg('nx.invite',{'nonce':'abcdefgh12345678'},to='vzzzzzzzzzz'))}.items():
        s1=st(pg); imp(pg,c); s2=json.loads(st(pg)); 
        ck(not s2.get('reqs') and not s2.get('teams') and not s2.get('evenings') and not s2.get('nexus'),'import neutro: '+k)
    # HTML nei nomi: testo, mai markup
    evil=forge(msg('nx.invite',{'nonce':'abcdefgh12345678'},**{'from':card('vevil1234567','<img src=x onerror=window.__pwn=1>')}))
    imp(pg,evil); pg.evaluate("()=>tvaFriends.open('nexus')"); pg.wait_for_timeout(300)
    ck(pg.evaluate("()=>!window.__pwn && !document.querySelector('#tfRoot img')"),'XSS: nome con HTML mostrato solo come testo')
    ck('<img' in pg.inner_text('#tfRoot'),'XSS: il testo letterale e\' visibile')
    # file importati
    big=tempfile.mktemp(); open(big,'w').write('A'*60000)
    pg.set_input_files('#tfImpFile',big); pg.wait_for_timeout(300); ck('troppo grande' in pg.inner_text('#tfToast'),'file import oltre il limite rifiutato')
    binf=tempfile.mktemp(); open(binf,'wb').write(bytes(range(256))*4)
    s2=st(pg); pg.set_input_files('#tfImpFile',binf); pg.wait_for_timeout(300); ck(st(pg)==s2,'file binario rifiutato senza modifiche',pg.inner_text('#tfToast'))
    # backup Friends malevolo
    pg.evaluate("()=>tvaFriends.open('varianti')"); pg.wait_for_timeout(200)
    mal='{"v":1,"vid":"vabcdefgh12","__proto__":{"polluted":"si"},"constructor":{"prototype":{"polluted2":"si"}},"me":{"name":"'+'N'*500+'","emblem":"x","share":{"tid":"no"},"__proto__":{"polluted3":1}},'\
        '"nexus":{"__proto__":{"vid":"vabcdefgh99"},"vbadbad":{"status":"linked"},"vgoodgood12":{"name":"<b>Ok</b>","status":"linked","emblem":99999,"color":-3}},'\
        '"teams":"stringa","evenings":[1,2],"duels":{"d_abcdefgh1234":{"id":"d_abcdefgh1234","seed":-5,"n":7}},"inbox":[{"id":"n_abcdef1234","text":"'+'T'*9000+'"}],"seen":{"__proto__":1,"m_abcdefgh1234":5},"unknown":{"x":1}}'
    f=tempfile.mktemp(suffix='.json'); open(f,'w').write(mal)
    pg.set_input_files('#tfBkFile',f); pg.wait_for_timeout(500)
    ck(pg.evaluate("()=>({}).polluted===undefined&&({}).polluted2===undefined&&({}).polluted3===undefined"),'backup malevolo: nessun prototype pollution')
    s3=json.loads(st(pg))
    ck(set(s3.keys())<={'v','vid','me','nexus','pendingOut','reqs','teams','evenings','duels','shared','inbox','seen','best'},'backup malevolo: campi sconosciuti scartati',list(s3.keys()))
    ck(len(s3['me']['name'])<=20 and isinstance(s3['me']['emblem'],int),'backup malevolo: nome troncato, emblema normalizzato')
    ck('vbadbad' not in s3['nexus'] and 'vgoodgood12' in s3['nexus'] and s3['nexus']['vgoodgood12']['emblem']<20,'backup malevolo: voci Nexus non valide scartate, valide normalizzate',s3['nexus'])
    ck(s3['teams']=={} and s3['evenings']=={} and s3['duels']=={},'backup malevolo: collezioni con tipo/valori errati azzerate',(s3['teams'],s3['duels']))
    ck(all(len(n['text'])<=220 for n in s3['inbox']) and 'm_abcdefgh1234' in s3['seen'],'backup malevolo: testi troncati, seen filtrato')
    o2=others(pg); ck(o2==base,'backup malevolo: nessuna altra chiave toccata',[k for k in set(o2)|set(base) if o2.get(k)!=base.get(k)])
    f2=tempfile.mktemp(suffix='.json'); open(f2,'w').write('{"v":1,"nexus":{')
    s4=st(pg); pg.set_input_files('#tfBkFile',f2); pg.wait_for_timeout(300); ck(st(pg)==s4,'backup JSON troncato rifiutato',pg.inner_text('#tfToast'))
    f3=tempfile.mktemp(suffix='.json'); open(f3,'w').write('{"v":2}')
    pg.set_input_files('#tfBkFile',f3); pg.wait_for_timeout(300); ck(st(pg)==s4,'backup di altra versione rifiutato')
    # nessuna richiesta di rete dopo tutto
    ck(not [u for u in pg.net if re.search(DATA,u)],'rete: ancora nessuna richiesta dati/auth Firebase a fine test')
    ck(not pg.errs,'nessun errore JS finale',pg.errs[:2])
    b.close()
SRV.terminate()
print('TOTALE FAIL:',len(fails))
sys.exit(1 if fails else 0)
