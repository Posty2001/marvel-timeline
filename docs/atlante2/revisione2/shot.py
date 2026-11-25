import asyncio,sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={'width':430,'height':900},device_scale_factor=2)
        errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        await pg.goto('file:///home/claude/atl2r2/index.html?static');await pg.wait_for_timeout(1500)
        for i in range(1,15):
            el=pg.locator('#f%d .phone'%i);await el.scroll_into_view_if_needed();await pg.wait_for_timeout(500)
            await el.screenshot(path='/tmp/r2/r2_%d.png'%i)
        print(errs)
        await b.close()
asyncio.run(main())
