import os,sys
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
OUT='/home/claude/outputs/F2_T3_TEST/rk2_shots'; srv,base=start_server()
with sync_playwright() as p:
    b=p.chromium.launch(); c=newctx(b,390,844); pg=c.new_page(); enter(pg,base)
    pg.evaluate("tvaRankingsUI.open()"); pg.wait_for_timeout(900); pg.screenshot(path=OUT+'/e_vuoto_390.png')
    for i,t in enumerate(['Modelli','Backup']):
        pg.evaluate("t=>[...document.querySelectorAll('.rk-tab')].find(x=>x.textContent===t).click()",t); pg.wait_for_timeout(500); pg.screenshot(path=OUT+'/f_%s_390.png'%t.lower())
    pg.evaluate("[...document.querySelectorAll('.rk-tab')].find(x=>x.textContent==='Archivio').click()"); pg.wait_for_timeout(300)
    pg.click('#rkNew'); pg.wait_for_timeout(700); pg.screenshot(path=OUT+'/g_nuova_390.png')
    b.close()
srv.terminate()
