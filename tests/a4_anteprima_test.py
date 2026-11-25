from playwright.sync_api import sync_playwright
R=[]
def ok(n,c):print(('PASS ' if c else 'FAIL ')+n);R.append(c)
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw,vh in ((390,844),(430,932),(320,640)):
        pg=b.new_page(viewport={'width':vw,'height':vh});err=[]
        pg.on('pageerror',lambda e:err.append(str(e)));pg.on('console',lambda m:err.append(m.text) if m.type=='error' else None)
        pg.goto('file:///home/claude/marvel-timeline/docs/atlante2/a4/anteprima_v2.html');pg.wait_for_timeout(500)
        ok(f'[{vw}] nessun overflow orizzontale',pg.evaluate('document.documentElement.scrollWidth')<=vw)
        ok(f'[{vw}] 27 universi disegnati',pg.evaluate("document.querySelectorAll('#v .stage .node').length")==27)
        if vw!=390: pg.close(); continue
        # selezione universo
        pg.evaluate("document.querySelectorAll('#v .stage .node')[5].dispatchEvent(new MouseEvent('click',{bubbles:true}))");pg.wait_for_timeout(200)
        ok('scheda universo cambia',pg.evaluate("document.querySelector('.sheet h2').textContent")!='Earth-199999 — MCU')
        # zoom/ricentra/fullscreen
        pg.click('.tb[aria-label=Ingrandisci]');ok('zoom applicato',pg.evaluate("document.querySelector('.stage svg g').getAttribute('transform').includes('scale(1.4')"))
        pg.click('.tb[aria-label=Ricentra]');ok('ricentra',pg.evaluate("document.querySelector('.stage svg g').getAttribute('transform').includes('scale(1)')"))
        pg.click('.tb[aria-label="Schermo intero"]');ok('schermo intero (overlay)',pg.evaluate("document.querySelector('.stage').classList.contains('fs')"));pg.click('.tb[aria-label="Schermo intero"]')
        # drag
        bb=pg.locator('.stage svg').bounding_box();pg.mouse.move(bb['x']+50,bb['y']+300);pg.mouse.down();pg.mouse.move(bb['x']+120,bb['y']+340,steps=5);pg.mouse.up()
        ok('trascinamento sposta la mappa',pg.evaluate("document.querySelector('.stage svg g').getAttribute('transform')")!='translate(0,0) scale(1)')
        pg.click('.tb[aria-label=Ricentra]')
        # confronto
        pg.click('text=Confronta con…');pg.evaluate("document.querySelectorAll('#v .stage .node')[9].dispatchEvent(new MouseEvent('click',{bubbles:true}))");pg.wait_for_timeout(200)
        ok('confronto universi mostrato',pg.locator('text=Confronto tra universi').count()==1 and pg.locator('text=Controparti dichiarate').count()+pg.locator('text=Controparte dichiarata').count()>=0)
        pg.click('text=Chiudi confronto')
        # esplora dentro
        pg.evaluate("document.querySelectorAll('#v .stage .node')[0].dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        pg.click('text=Esplora l’universo');pg.wait_for_timeout(300)
        n=pg.evaluate("document.querySelectorAll('#v .stage .node').length");ok('esplorazione interna: nodi identità',n>3)
        pg.click('text=◐ Ritratti (simulati)');ok('toggle ritratti simulati',pg.evaluate("document.querySelectorAll('#v .stage .ring[fill^=\"url\"]').length")>0)
        pg.click('text=← Multiverso')
        # nexus
        pg.click('#t1');pg.wait_for_timeout(200)
        ok('nexus: nodi vicini <= cap',0<pg.evaluate("document.querySelectorAll('#v .stage .node[aria-label^=\"Ricentra\"]').length")<=20)
        pg.fill('input[type=search]','Wolverine');pg.wait_for_timeout(200)
        ok('ricerca trova risultati',pg.locator('.res button').count()>0)
        pg.locator('.res button').first.click();pg.wait_for_timeout(200)
        ok('ricentra da ricerca + cronologia',pg.locator('.trail').count()==1)
        pg.click('.trail button:has-text("indietro")');pg.wait_for_timeout(100);ok('indietro ripristina',pg.locator('.trail').count()==0)
        for t in (1,3):
            pg.click(f'.row button.chip:text-is("{t}")');
        ok('soglia 3 attiva',pg.evaluate("[...document.querySelectorAll('.row .chip[aria-pressed=true]')].some(x=>x.textContent=='3')"))
        pg.click('.chip:has-text("Co-apparizioni")');ok('filtro co-apparizioni off',pg.evaluate("[...document.querySelectorAll('.chip')].find(x=>x.textContent.includes('Co-apparizioni')).getAttribute('aria-pressed')")=='false')
        pg.evaluate("document.querySelector('#v .stage g.node[aria-label^=\"Relazione\"]')&&document.querySelector('#v .stage g.node[aria-label^=\"Relazione\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))");pg.wait_for_timeout(150)
        ok('scheda relazione con stato di verifica',pg.locator('#nxbox .pill').count()>=1)
        # percorso
        pg.click('#t2');pg.wait_for_timeout(200)
        ok('percorso trovato (misto)',pg.locator('.step').count()>=2)
        pg.click('.seg button:has-text("Narrativo")');pg.wait_for_timeout(150)
        ok('narrativo senza collegamento: nessun percorso inventato',pg.locator('text=Nessun percorso documentato').count()==1)
        pg.fill('input[aria-label=Da]','Odino');pg.locator('.res button').first.click();pg.fill('input[aria-label=A]','Loki');pg.locator('.res button').first.click();pg.wait_for_timeout(200)
        ok('narrativo: Odino→Loki via relazione documentata con stato',pg.locator('.step').count()==2 and pg.locator('.link .pill').count()==1)
        ok('nessun errore JS',not err)
        pg.close()
print('ESITO',all(R))
