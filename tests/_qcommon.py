import sys,subprocess,time,json,socket,os
from playwright.sync_api import sync_playwright
ROOT=os.environ.get('Q_ROOT','/home/claude/quiz_work')
def fp():
    s=socket.socket();s.bind(('127.0.0.1',0));p=s.getsockname()[1];s.close();return p
def start_server():
    port=fp();p=subprocess.Popen([sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1','--directory',ROOT],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1);return p,'http://127.0.0.1:%d'%port
RES=[]
def ck(c,m,i=''):
    RES.append(('PASS' if c else 'FAIL',m));print(('PASS ' if c else 'FAIL ')+m,'' if c else str(i)[:300],flush=True)
def blocked(m,why): RES.append(('BLOCKED',m));print('BLOCKED '+m,why,flush=True)
def summary():
    print('TOTALE: PASS %d FAIL %d BLOCKED %d'%tuple(sum(1 for r in RES if r[0]==x) for x in('PASS','FAIL','BLOCKED')))
def newctx(b,w=390,h=844,mobile=True,**kw):
    return b.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile,service_workers='block',**kw)
def enter(pg,base):
    pg.goto(base+'/index.html');pg.wait_for_timeout(1800)
    pg.evaluate("()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}");pg.wait_for_timeout(500)
exec(open(os.path.join(ROOT,'tests','_tfopen.py')).read())
