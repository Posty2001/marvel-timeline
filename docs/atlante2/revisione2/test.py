import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':430,'height':900},device_scale_factor=2)
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/atl2r2/index.html');await pg.wait_for_timeout(1200)
        R={}
        await pg.click('#vseg button[data-v=l]');R['list']=await pg.eval_on_selector('#vl','e=>getComputedStyle(e).display')
        await pg.click('#dtabs .chip[data-s=s3]');await pg.click('#dtabs .chip[data-s=s2]');R['prog']=await pg.inner_text('#dprog')
        R['hub']=await pg.inner_text('#hn')
        await pg.click('.nn[data-n=Thor]');R['nexus']=await pg.eval_on_selector('#nx','e=>e.querySelector("text:last-of-type").textContent')
        await pg.click('.mn[data-n="SSU Sony"]',force=True);R['map']=await pg.inner_text('#mt')
        await pg.fill('#q','th');R['search']=await pg.eval_on_selector_all('#sr b','es=>es.map(e=>e.textContent)')
        await pg.click('#pseg button[data-p=l]');R['pl']=await pg.eval_on_selector('.pp[data-p=l]','e=>getComputedStyle(e).display')
        await pg.click('#zi');
        print(R,errs)
        # cmp
        el=pg.locator('#cmp');await el.scroll_into_view_if_needed();await pg.wait_for_timeout(800)
        await pg.screenshot(path='/tmp/r2/cmp.png');await b.close()
asyncio.run(main())
