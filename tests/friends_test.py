# TVA Friends: test dei moduli locali (Varianti, Nexus, Squadre, Serate, Quiz/Duelli, Archivio, Comunicazioni) con DUE dispositivi simulati
# (due contesti browser separati; scambio solo tramite i codici generati dall'app, come farebbero due persone). Cloud: DISATTIVATO, verificato come tale.
import json,re,os,sys,socket,subprocess,time,base64
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
SECRETS=['SEGRETO-DIARIO-XYZ','VOTO-PRIVATO-42']
LS={'marvel-ultimate-timeline-watched':json.dumps({"001":True,"002":True,"003":True,"005":True}),'marvel-ultimate-timeline-notes':json.dumps({"001":SECRETS[0]}),'marvel-ultimate-timeline-ratings':json.dumps({"001":4.5}),'marvel-ultimate-timeline-favorites':json.dumps({"002":True})}
CODES=[]
def mk(b,ls=None,name=None):
    cx=b.new_context(viewport={'width':390,'height':844},service_workers='block'); pg=cx.new_page(); errs=[]; pg.errs=errs; pg.net=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('request',lambda r: pg.net.append(r.url))
    pg.answer=True; pg.dlgs=[]
    def dlg(d): pg.dlgs.append(d.message); d.accept() if pg.answer else d.dismiss()
    pg.on('dialog',dlg)
    init="if(!sessionStorage.getItem('__s')){sessionStorage.setItem('__s','1');"+"".join("localStorage.setItem(%s,%s);"%(json.dumps(k),json.dumps(v)) for k,v in (ls or {}).items())+"}"
    pg.add_init_script(init)
    pg.route('**/*',lambda r: r.abort() if any(h in r.request.url for h in ('gstatic','googleapis','firebaseio','tmdb')) else r.continue_())
    return cx,pg
def start(pg):
    pg.goto(U); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
def opn(pg,tab=None):
    pg.evaluate("(t)=>tvaFriends.open(t)",tab); pg.wait_for_timeout(250); pg.evaluate("()=>document.querySelectorAll('#tfRoot details.tf-sec').forEach(d=>{d.open=true})")
def tab(pg,t): pg.click('#tfTab-'+t); pg.wait_for_timeout(200); pg.evaluate("()=>document.querySelectorAll('#tfRoot details.tf-sec').forEach(d=>{d.open=true})")
def tdet(pg):
    pg.click('#tfTab-squadre'); pg.wait_for_timeout(150)
    if not pg.query_selector('#tfTeamProg'): pg.click('[data-team]'); pg.wait_for_timeout(150)
def edet(pg):
    pg.click('#tfTab-serate'); pg.wait_for_timeout(150)
    if not pg.query_selector('#tfEvCounts') and not pg.query_selector('#tfEvMine'): pg.click('[data-ev]'); pg.wait_for_timeout(150)
def code(pg):
    c=pg.input_value('#tfOutCode'); CODES.append(c); return c
def imp(pg,c):
    pg.evaluate("()=>{const d=document.getElementById('tfImp'); if(d) d.open=true}")
    pg.fill('#tfImpText',c); pg.click('#tfImpBtn'); pg.wait_for_timeout(250); return pg.inner_text('#tfToast')
def store(pg): return json.loads(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-tvafriends-v1')") or 'null')
def dec(c):
    b=c.split('.')[1]; b+='='*(-len(b)%4); return json.loads(base64.urlsafe_b64decode(b).decode('utf-8'))
def keys(pg): return {k:v for k,v in pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}").items() if k not in ('marvel-ultimate-timeline-tvafriends-v1','marvel-ultimate-timeline-auto-backup')}
_html=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
_js=re.search(r'<script id="friends-js">(.*?)</script>',_html,re.S).group(1)
# --- analisi statica
sets=re.findall(r'localStorage\.(setItem|removeItem)\(([^,)]+)',_js)
ck(all(k.strip()=='KEY' for _,k in sets) and len(sets)>=1,'statica: l\'unica chiave scritta/rimossa e\' quella di TVA Friends',sets)
ck(not re.search(r"PROFILE_(OBJ|STR)_KEYS|sostituisciProfilo|normalizzaProfilo|syncPushNow|SYNC_CODE_KEY|rooms/|'sync/",_js),'statica: nessun accesso a profilo sincronizzato, motore sync, rooms/ o sync/')
rd=re.findall(r"localStorage\.getItem\('([^']+)'\)",_js)
ck(set(rd)<= {'marvel-ultimate-timeline-watched','marvel-ultimate-timeline-tessera-id','marvelGuideCustomTimelineOrder','marvel-ultimate-timeline-user-name'},'statica: letture limitate a: titoli visti (conteggio), id tessera, ordine custom, nome',set(rd))
ck('marvel-ultimate-timeline-notes' not in _js and 'marvel-ultimate-timeline-ratings' not in _js and 'marvel-ultimate-timeline-favorites' not in _js,'statica: chiavi di note, voti e preferiti mai referenziate')
ck('var CLOUD_ENABLED = false;' in _js,'cloud: costante di build CLOUD_ENABLED = false')
ck('eval(' not in _js and 'innerHTML' not in _js and 'document.write' not in _js and 'new Function' not in _js,'statica: nessun innerHTML/eval (contenuti altrui solo come testo)')
with sync_playwright() as p:
    b=p.chromium.launch()
    cxA,A=mk(b,LS); cxB,B=mk(b,LS); start(A); start(B)
    A.evaluate("()=>{document.getElementById('appTabMissioni').click();document.getElementById('cenTab-operazioni').click()}"); B.evaluate("()=>{document.getElementById('appTabMissioni').click();document.getElementById('cenTab-operazioni').click()}"); A.wait_for_timeout(6500); base=keys(A); baseB=keys(B); net0=len(A.net)+len(B.net)
    ck(store(A) is None and store(B) is None,'avvio: nessuna chiave Friends creata finche\' non si usa')
    ck(A.evaluate("()=>{document.getElementById('appTabMissioni').click();document.getElementById('cenTab-operazioni').click();return !document.getElementById('tfOpen')&&!document.getElementById('tfLauncher')&&!!document.getElementById('appTabFriends')}"),'Centrale TVA > Operazioni: nessun lancio Friends duplicato (rimosso per decisione); accesso dalla barra FRIENDS')
    ck(A.evaluate("()=>['cenTab-panoramica','cenTab-missioni','cenTab-strumenti','cenTab-operazioni'].every(i=>!!document.getElementById(i))"),'Centrale TVA: le 4 sezioni originali intatte')
    # ===== M1 Varianti
    opn(A); ck(A.evaluate("()=>document.querySelectorAll('.tf-tab').length")==7,'7 moduli presenti')
    A.evaluate("()=>{const d=document.getElementById('tfCustom');if(d)d.open=true}"); A.fill('#tfName','Alice'); A.fill('#tfMotto','Tempo al tempo'); A.click('.tf-pick:nth-child(3)'); A.click('#tfSaveMe'); A.wait_for_timeout(200)
    ck(store(A)['me']['name']=='Alice' and store(A)['me']['emblem']==2,'M1 Variante salvata (nome, emblema)')
    ck('Tempo al tempo' not in A.inner_text('#tfPrev'),'M1 anteprima: motto NON mostrato finche\' non condiviso')
    A.check('#tfSh-motto'); A.wait_for_timeout(100); ck('Tempo al tempo' in A.inner_text('#tfPrev'),'M1 anteprima aggiornata quando si abilita la condivisione del motto')
    A.uncheck('#tfSh-motto'); A.click('#tfSaveMe')
    A.fill('#tfName','x'*40); ck(len(A.input_value('#tfName'))<=20,'M1 nome limitato a 20 caratteri')
    A.fill('#tfName','Alice'); A.click('#tfSaveMe')
    opn(B); B.fill('#tfName','Bruno'); B.click('#tfSaveMe'); B.wait_for_timeout(200)
    # ===== M2 Nexus
    tab(A,'nexus'); A.click('#tfNxInvite'); invA=code(A); ck(invA.startswith('TVA1.'),'M2 invito generato')
    d=dec(invA); ck(d['t']=='nx.invite' and d['from']['name']=='Alice' and 'motto' not in d['from'],'M2 l\'invito contiene solo la carta pubblica (motto non condiviso assente)')
    tab(B,'nexus'); r=imp(B,invA); ck('Invito Nexus ricevuto' in r,'M2 B importa l\'invito',r)
    ck(B.evaluate("()=>document.querySelectorAll('[data-req]').length")==1 and not store(B)['nexus'],'M2 richiesta in attesa: NESSUN legame finche\' B non accetta')
    ck(imp(B,invA).startswith('Questo codice e\' gia\''),'M2 stesso codice importato due volte: rifiutato')
    tampered=invA[:-3]+('aaa' if not invA.endswith('aaa') else 'bbb'); ck('integrita' in imp(B,tampered) or 'trascritto' in imp(B,tampered),'M2 codice manomesso: rifiutato dal checksum')
    ck('non e\' un codice' in imp(B,'ciao mondo').lower() or 'valido' in imp(B,'ciao mondo'),'M2 testo casuale: rifiutato con messaggio')
    B.click('[data-act="nx-accept"]'); B.wait_for_timeout(200); resp=code(B); ck(dec(resp)['t']=='nx.accept','M2 B accetta: codice di risposta generato')
    ck(len([1 for v in store(B)['nexus'].values() if v['status']=='linked'])==1,'M2 B ha il legame con Alice')
    ck(len(store(A)['nexus'])==0,'M2 A non e\' ancora collegato (serve la risposta)')
    r=imp(A,resp); ck('Legame Nexus attivo' in r,'M2 A importa la risposta: legame attivo',r)
    # risposta falsa (nonce inventato) da una terza Variante
    cxC,C=mk(b,LS); start(C); opn(C); C.fill('#tfName','Carlo'); C.click('#tfSaveMe'); tab(C,'nexus'); C.click('#tfNxInvite'); invC=code(C)
    # B (non collegato a C) tenta di... C manda messaggi non-nexus ad A: es. pacchetto
    tab(C,'archivio'); C.evaluate("()=>{const l=document.querySelectorAll('#tfPkList input');l[0].checked=true}"); C.fill('#tfPkTitle','spam'); C.click('#tfPkMake'); spam=code(C)
    ck('non collegato' in imp(A,spam),'M2 messaggio da Variante NON collegata: rifiutato')
    forged=dec(resp); forged['id']='m_forged000001'; forged['b']['nonce']='0123456789abcdef'; forged['from']=dec(invC)['from']; forged['to']=store(A)['vid']
    import hashlib
    def reencode(m):
        j=json.dumps(m,separators=(',',':'),ensure_ascii=False); h=2166136261
        for ch in j.encode('utf-16-le').decode('utf-16-le'):
            for cu in ch.encode('utf-16-le')[::1][0:0]: pass
        # fnv su unita' UTF-16 come JS
        u=j.encode('utf-16-le'); h=2166136261
        for i in range(0,len(u),2):
            h^=u[i]|(u[i+1]<<8); h=(h*16777619)&0xFFFFFFFF
        return 'TVA1.'+base64.urlsafe_b64encode(j.encode('utf-8')).decode().rstrip('=')+'.'+('%08x'%h)
    ck('non attesa' in imp(A,reencode(forged)),'M2 risposta Nexus con nonce inventato: rifiutata')
    ck(len([1 for v in store(A)['nexus'].values() if v['status']=='linked'])==1,'M2 nessun legame creato dalla risposta falsa')
    # ===== M3 Squadre
    tab(A,'squadre'); A.fill('#tfTeamName','Avengers TVA'); A.fill('#tfTeamGoal','20'); A.click('#tfTeamNew'); A.wait_for_timeout(200)
    ck('Avengers TVA' in A.inner_text('#tfPanel-squadre'),'M3 squadra creata')
    A.click('#tfTeamInvite'); inv=code(A); ck(dec(inv)['t']=='team.invite' and dec(inv)['to']==store(B)['vid'],'M3 invito squadra destinato a B')
    tab(B,'squadre'); r=imp(B,inv); ck('Invito squadra' in r,'M3 B riceve l\'invito',r)
    tab(B,'squadre'); B.click('[data-act="team-join"]'); B.wait_for_timeout(200); join=code(B)
    ck(len(store(B)['teams'])==1,'M3 B e\' nella squadra')
    r=imp(A,join); ck('aggiunto' in r,'M3 A (capo) importa l\'ingresso',r)
    tdet(A); pA=A.inner_text('#tfTeamProg')
    ck('0 / 20' in pA,'M3 avanzamento iniziale 0/20 (nessuna condivisione automatica)',pA)
    A.click('#tfTeamShare'); A.wait_for_timeout(200); stA=code(A)
    ck('4 / 20' in A.inner_text('#tfTeamProg') and dec(stA)['b']['members'][store(A)['vid']]['seen']==4,'M3 A condivide SOLO il conteggio dei titoli visti (4) dopo conferma')
    ck(any('numero dei tuoi titoli visti' in m for m in A.dlgs),'M3 conferma esplicita prima di condividere l\'avanzamento')
    tdet(B); r=imp(B,stA); ck('aggiornata' in r,'M3 B importa l\'aggiornamento',r)
    tdet(B); ck('4 / 20' in B.inner_text('#tfTeamProg'),'M3 B vede l\'avanzamento di A',B.inner_text('#tfTeamProg'))
    B.click('#tfTeamShare'); stB=code(B); r=imp(A,stB); tdet(A)
    ck('8 / 20' in A.inner_text('#tfTeamProg'),'M3 somma di squadra 8/20 dopo l\'avanzamento di B',A.inner_text('#tfTeamProg'))
    # membro che tenta di falsificare l'avanzamento di un altro
    fs=dec(stB); fs['id']='m_forged000002'; fs['b']['members'][store(A)['vid']]={'name':'Alice','seen':999,'ts':9999999999999}; fs['to']=None
    r=imp(A,reencode(fs)); tdet(A)
    ck('999' not in A.inner_text('#tfTeamProg') and store(A)['teams'][list(store(A)['teams'])[0]]['members'][store(A)['vid']]['seen']!=999,'M3 un membro non puo\' alterare l\'avanzamento di un altro')
    fs2=dec(stB); fs2['id']='m_forged000003'; fs2['b']['team']['id']='t_nonmembro0001'; r=imp(A,reencode(fs2)); ck('Non fai parte' in r,'M3 aggiornamento per squadra sconosciuta: rifiutato',r)
    # ===== M4 Serate
    tab(A,'serate'); A.fill('#tfEvTitle','Maratona Spider-Man'); A.select_option('#tfEvItem','001')
    import datetime
    soon=(datetime.datetime.now()+datetime.timedelta(hours=5)).strftime('%Y-%m-%dT%H:%M'); A.fill('#tfEvWhen',soon); A.fill('#tfEvPlace','Casa mia')
    A.evaluate("()=>{document.querySelector('#tfPanel-serate fieldset input').checked=true}"); A.click('#tfEvNew'); A.wait_for_timeout(200)
    ck('Maratona Spider-Man' in A.inner_text('#tfPanel-serate'),'M4 serata creata')
    A.click('#tfEvSend'); evc=code(A); ck(dec(evc)['t']=='ev.invite','M4 inviti generati')
    tab(B,'serate'); r=imp(B,evc); ck('Invito alla serata' in r,'M4 B riceve l\'invito',r)
    edet(B); ck('in attesa' in B.inner_text('#tfEvMine'),'M4 B: risposta iniziale «in attesa»')
    B.click('[data-rsvp="si"]'); rsvp=code(B); ck('si' in B.inner_text('#tfEvMine'),'M4 B risponde «Ci sono»')
    r=imp(A,rsvp); edet(A); ck('1 si' in A.inner_text('#tfEvCounts'),'M4 A vede la risposta',A.inner_text('#tfEvCounts'))
    with A.expect_download() as di: A.click('#tfEvIcs')
    ics=open(di.value.path(),encoding='utf-8').read(); ck('BEGIN:VEVENT' in ics and 'Maratona Spider-Man' in ics and 'DTSTART:' in ics,'M4 esportazione .ics valida')
    ck(SECRETS[0] not in ics,'M4 .ics senza dati privati')
    tab(A,'com'); ck('Promemoria' in A.inner_text('#tfPanel-com'),'M4/M7 promemoria della serata nelle Comunicazioni (<24h)')
    edet(A); A.click('.tf-danger'); A.wait_for_timeout(200); canc=code(A); r=imp(B,canc); ck('annullata' in r,'M4 annullamento propagato a B',r)
    # risposta di un non invitato
    rr=dec(rsvp); rr['id']='m_forged000004'; rr['b']['rsvp']='boh'; ck('non valida' in imp(A,reencode(rr)),'M4 risposta con valore non valido: rifiutata')
    # ===== M5 Quiz e Duelli
    tab(A,'sfide'); A.click('#tfSolo5'); A.wait_for_timeout(200)
    qtxt=[]; 
    for i in range(5):
        qtxt.append(A.inner_text('#tfQ')); ck(A.evaluate("()=>document.querySelectorAll('.tf-opt').length")==4,'M5 domanda %d con 4 opzioni'%(i+1)) if i==0 else None
        A.click('.tf-opt >> nth=0'); A.wait_for_timeout(100); fb=A.inner_text('#tfFb'); 
        if i==0: ck(len(fb)>8,'M5 feedback con spiegazione')
        A.click('#tfNext'); A.wait_for_timeout(100)
    ck('Risultato:' in A.inner_text('#tfGame'),'M5 risultato finale mostrato'); A.click('#tfGameEnd'); A.wait_for_timeout(150)
    ck(store(A)['best']['n']==5,'M5 miglior risultato registrato')
    ck(len(set(qtxt))==5,'M5 domande tutte diverse')
    h1=A.evaluate("()=>{const q=(window.__x=1);return 0}")
    A.click('#tfDuelNew'); ch=code(A); dm=dec(ch); ck(dm['t']=='duel.challenge' and dm['b']['n']==10,'M5 sfida generata (10 domande, seme + impronta)')
    tab(B,'sfide'); r=imp(B,ch); ck('Sfida di Alice' in r,'M5 B riceve la sfida',r)
    ck('versione diversa' not in r,'M5 stesse domande su entrambi i dispositivi (impronta uguale)')
    # A gioca (tutte la prima opzione), B gioca (tutte la prima)
    def play(pg,n=10):
        pg.click('[data-act="duel-play"]'); pg.wait_for_timeout(200)
        for i in range(n): pg.click('.tf-opt >> nth=0'); pg.click('#tfNext'); pg.wait_for_timeout(60)
        res=pg.inner_text('#tfGame'); pg.wait_for_timeout(200); return res
    tab(A,'sfide'); ra=play(A); A.click('#tfGameEnd'); A.wait_for_timeout(300); resA=code(A) if A.evaluate("()=>!document.getElementById('tfOut').hidden") else None
    tab(B,'sfide'); rb=play(B); B.click('#tfGameEnd'); B.wait_for_timeout(300); resB=code(B)
    ck(ra.split('\n')[0]==rb.split('\n')[0],'M5 stesse risposte su stesse domande: stesso punteggio su A e B',(ra,rb))
    r=imp(A,resB); ck('Risultato di Bruno' in r,'M5 A importa il risultato di B',r); tab(A,'sfide')
    ck(A.evaluate("()=>document.querySelectorAll('[data-duel] .tf-board li').length")==2,'M5 classifica con 2 giocatori')
    bad=dec(resB); bad['id']='m_forged000005'; bad['b']['score']=99; ck('non valido' in imp(A,reencode(bad)),'M5 punteggio impossibile (99/10): rifiutato')
    bad2=dec(resB); bad2['id']='m_forged000006'; bad2['b']['id']='d_inesistente01'; ck('non trovato' in imp(A,reencode(bad2)),'M5 risultato per duello sconosciuto: rifiutato')
    # ===== M6 Archivio condiviso
    tab(A,'archivio'); A.fill('#tfPkTitle','Da vedere'); A.fill('#tfPkDesc','Per iniziare'); A.evaluate("()=>{const l=document.querySelectorAll('#tfPkList input');l[0].checked=true;l[1].checked=true;l[2].checked=true}"); A.click('#tfPkMake'); pk=code(A)
    ck(dec(pk)['b']['kind']=='picks' and len(dec(pk)['b']['items'])==3,'M6 pacchetto di 3 titoli')
    tab(B,'archivio'); r=imp(B,pk); ck('aggiunto all\'Archivio' in r,'M6 B riceve il pacchetto',r)
    B.click('#tfTab-archivio'); B.wait_for_timeout(150); B.click('[data-pkg] summary'); ck(B.evaluate("()=>document.querySelectorAll('[data-pkg] .tf-pk li').length")==3,'M6 B vede i 3 titoli (nomi dal catalogo)')
    ck('gia\' visto' in B.inner_text('[data-pkg]'),'M6 B vede quali ha gia\' visto (solo in locale)')
    ck(store(B)['shared']['inn'] and {k:v for k,v in keys(B).items() if k in baseB and k!='marvel-ultimate-timeline-missione-snapshot'}=={k:v for k,v in baseB.items() if k!='marvel-ultimate-timeline-missione-snapshot'} ,'M6 il pacchetto ricevuto non modifica i dati di B')
    tab(A,'archivio'); A.click('#tfPkOrder'); A.wait_for_timeout(150); ck('ordine Timeline personalizzato' in ' '.join(A.dlgs) or 'non hai un ordine' in A.inner_text('#tfToast').lower(),'M6 ordine custom: richiede ordine esistente/conferma')
    # ===== M7 Comunicazioni
    tab(B,'com'); n0=B.evaluate("()=>document.querySelectorAll('.tf-note').length"); ck(n0>=4,'M7 B ha comunicazioni (nexus, squadra, serata, sfida, pacchetto)',n0)
    B.select_option('#tfFilter','duel'); ck(B.evaluate("()=>[...document.querySelectorAll('.tf-note')].every(n=>n.textContent.includes('\U0001F3AF'))"),'M7 filtro per tipo')
    B.select_option('#tfFilter',''); u0=B.evaluate("()=>tvaFriends.unread()"); B.click('#tfReadAll'); B.wait_for_timeout(150); ck(B.evaluate("()=>tvaFriends.unread()")<u0 or u0==0,'M7 segna tutto come letto',(u0,))
    B.click('.tf-note .reset-btn >> text=Elimina >> nth=0'); B.wait_for_timeout(150); ck(B.evaluate("()=>document.querySelectorAll('.tf-note').length")<n0,'M7 elimina singola comunicazione')
    # ===== PRIVACY: nessun codice contiene dati privati; profilo invariato
    allc=' '.join(CODES); dec_all=' '.join(json.dumps(dec(c)) for c in CODES)
    ck(CODES and not any(s in allc or s in dec_all for s in SECRETS) and '4.5' not in dec_all and '"favorites"' not in dec_all,'PRIVACY: nessuno dei %d codici generati contiene note/Diario, voti o preferiti'%len(CODES))
    ck(SECRETS[0] not in json.dumps(store(A)) and SECRETS[0] not in json.dumps(store(B)),'PRIVACY: archivio Friends senza dati privati')
    IDENT=('marvel-ultimate-timeline-user-name','marvel-ultimate-timeline-fav-char','marvel-ultimate-timeline-identity-v1','marvel-ultimate-timeline-identity-premigration-v1','marvel-ultimate-timeline-tessera-id')
    dif=[k for k in set(keys(A))|set(base) if keys(A).get(k)!=base.get(k) and k not in IDENT]; ck(not dif,'PRIVACY: voti, note, progressi, XP, badge, missioni di A identici dopo tutti i flussi (Friends 2.0 scrive solo l\'identita\' condivisa: nome, personaggio, identity)',dif)
    ident_ok=all(k in IDENT for k in [k for k in set(keys(A))|set(base) if keys(A).get(k)!=base.get(k)]); ck(ident_ok,'PRIVACY: le sole chiavi esterne modificate sono quelle dell\'identita\' condivisa (per design Tessera 3.0)')
    ck(not [u for u in (A.net+B.net)[net0:] if 'firebase' in u or 'googleapis' in u or 'gstatic' in u],'CLOUD: nessuna richiesta verso Firebase/Google con il cloud disattivato')
    ck(A.evaluate("()=>tvaFriends.cloudEnabled()")==False,'CLOUD: disattivato')
    # ===== offline + errori
    cxA.set_offline(True); A.evaluate("()=>window.dispatchEvent(new Event('offline'))"); A.wait_for_timeout(150)
    ck(A.evaluate("()=>!document.getElementById('tfNet').hidden"),'OFFLINE: indicatore «offline» visibile')
    tab(A,'nexus'); A.click('#tfNxInvite'); ck(code(A).startswith('TVA1.'),'OFFLINE: i moduli locali funzionano senza rete'); cxA.set_offline(False)
    # archivio corrotto: l'app non va in errore
    A.evaluate("()=>localStorage.setItem('marvel-ultimate-timeline-tvafriends-v1','{rotto')"); A.reload(); start(A); opn(A)
    ck(A.evaluate("()=>document.querySelectorAll('.tf-tab').length")==7 and not A.errs,'ERRORI: archivio corrotto -> ripartenza pulita senza crash',A.errs)
    # spazio pieno
    A.evaluate("()=>{const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='marvel-ultimate-timeline-tvafriends-v1')throw new Error('quota');return o.apply(this,arguments)}}")
    A.fill('#tfName','Zed'); A.click('#tfSaveMe'); A.wait_for_timeout(200); ck('Spazio del browser pieno' in A.inner_text('#tfToast') or 'NON salvata' in A.inner_text('#tfToast') or 'pieno' in A.inner_text('#tfToast').lower(),'ERRORI: spazio pieno segnalato (nessun crash)',A.inner_text('#tfToast'))
    # backup/ripristino Friends
    A.reload(); start(A); opn(A); A.fill('#tfName','Alice'); A.click('#tfSaveMe'); A.wait_for_timeout(150)
    with A.expect_download() as d2: A.click('#tfExp')
    bk=json.load(open(d2.value.path(),encoding='utf-8')); ck(bk['v']==1 and bk['me']['name'] in ('Alice','Zed') and SECRETS[0] not in json.dumps(bk),'BACKUP: esportazione Friends valida e senza dati privati')
    allerr=[e for pg in (A,B,C) for e in pg.errs]; ck(not allerr,'nessun errore JS',allerr[:3])
    b.close()
SRV.terminate(); print('FAILS:',fails); sys.exit(1 if fails else 0)
