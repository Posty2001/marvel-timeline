import os,sys
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
OUT=os.environ.get('SHOTS','/home/claude/outputs/F2_T3_TEST/ops_shots'); os.makedirs(OUT,exist_ok=True); srv,base=start_server()
tag=sys.argv[1] if len(sys.argv)>1 else 'x'
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h in ((390,844),(320,640)):
        c=newctx(b,w,h); pg=c.new_page(); enter(pg,base)
        pg.evaluate("document.getElementById('appTabMissioni').click();document.getElementById('cenTab-operazioni').click()"); pg.wait_for_timeout(1500)
        pg.screenshot(path=f'{OUT}/ops_{tag}_{w}.png',full_page=False)
        print(w,pg.evaluate("[document.getElementById('cenPan-operazioni').scrollHeight,[...document.querySelectorAll('#cenPan-operazioni > section, #cenPan-operazioni > details')].map(e=>e.id||e.querySelector('h3,summary')?.textContent)]"))
        c.close()
    b.close()
srv.terminate()
