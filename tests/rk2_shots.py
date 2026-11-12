import os,sys,json
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
OUT=os.environ.get('SHOTS','/home/claude/outputs/F2_T3_TEST/rk2_shots')
srv,base=start_server()
SEED="""async()=>{
 const c=tvaRankings.catalog; const chars=c.search('char','',14), items=c.search('item','',14);
 const t=await tvaRankings.create({kind:'top',title:'I miei personaggi Marvel preferiti di sempre in assoluto, titolo molto lungo per provare il layout',preset:'personaggi',imageMode:'images',description:'Classifica reale di prova'});
 const id=t.id||t.ranking.id; const rid=(t.ranking||t).id;
 const rows=(chars.rows||chars).slice(0,12);
 for(const r of rows){ try{ await tvaRankings.addItem(rid,{source:{type:'catalog',cat:'char',ref:r.ref||r.id},name:r.name||r.label}); }catch(e){} }
 await tvaRankings.addItem(rid,{source:{type:'manual'},name:'Elemento manuale senza immagine con nome molto lungo da gestire'});
 await tvaRankings.updateMeta(rid,{view:'podium'});
 const u=await tvaRankings.create({kind:'tier',title:'Film Marvel per fasce',preset:'film',imageMode:'images'});
 const uid=(u.ranking||u).id; const its=(items.rows||items).slice(0,10);
 for(const r of its){ try{ await tvaRankings.addItem(uid,{source:{type:'catalog',cat:'item',ref:r.ref||r.id},name:r.name||r.label}); }catch(e){} }
 await tvaRankings.addItem(uid,{source:{type:'manual'},name:'Senza immagine'});
 const full=await tvaRankings.get(uid); const ts=full.tiers.map(x=>x.id);
 let k=0; for(const it of full.items){ try{ await tvaRankings.moveItemToTier(uid,it.id,ts[k%ts.length]||null); }catch(e){} k++; }
 await tvaRankings.create({kind:'top',title:'Top 3 vuota',preset:'libera',imageMode:'text'});
 return [rid,uid];}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h in ((320,640),(390,844),(412,915),(768,1024)):
        c=newctx(b,w,h); pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:120]))
        enter(pg,base); pg.evaluate("document.getElementById('appTabHome').click()"); pg.wait_for_timeout(400)
        ids=pg.evaluate(SEED); 
        pg.evaluate("tvaRankingsUI.open()"); pg.wait_for_timeout(1200)
        pg.screenshot(path=f'{OUT}/a_archivio_{w}.png')
        pg.evaluate("[...document.querySelectorAll('.rk-card-main')].find(x=>x.textContent.includes('personaggi')).click()"); pg.wait_for_timeout(1200)
        pg.screenshot(path=f'{OUT}/b_podio_{w}.png'); print('PODIO',w,pg.evaluate("Math.round(document.getElementById('rkPodium').getBoundingClientRect().height)"))
        pg.evaluate("document.getElementById(\"rkViewList\").click()"); pg.wait_for_timeout(800); pg.screenshot(path=f'{OUT}/c_elenco_{w}.png')
        pg.evaluate("document.querySelector('.rk-head .rk-ib[aria-label^=Torna]').click()"); pg.wait_for_timeout(600)
        pg.evaluate("[...document.querySelectorAll('.rk-card-main')].find(x=>x.textContent.includes('Film Marvel')).click()"); pg.wait_for_timeout(1200)
        pg.screenshot(path=f'{OUT}/d_tier_{w}.png')
        print(w,ids,errs)
        c.close()
    b.close()
srv.terminate()
