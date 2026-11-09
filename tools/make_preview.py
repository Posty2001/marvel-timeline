import re,os,shutil,zipfile
W='/home/claude/work'; O='/tmp/preview'
shutil.rmtree(O,ignore_errors=True); os.makedirs(O); shutil.copytree(W+'/assets',O+'/assets'); shutil.copy(W+'/sw.js',O+'/sw.js')
s=open(W+'/index.html',encoding='utf-8').read()
s,k=re.subn(r'<script src="https://www\.gstatic\.com/firebasejs/[^"]+"></script>\n?','',s); assert k==3
a=s.index('var FIREBASE_CONFIG = {'); b=s.index('};',a)+2
s=s[:a]+'var FIREBASE_CONFIG = { apiKey: "INSERISCI_QUI" };  /* PREVIEW: Firebase rimosso */'+s[b:]
m=re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(")',s); c=m.group(2).replace("https://www.gstatic.com","")
c=re.sub(r"connect-src [^;]*;","connect-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com https://image.tmdb.org;",c)
s=s[:m.start(2)]+c+s[m.end(2):]
bid=re.search(r'name="tva-build" content="([^"]+)"',s).group(1)
badge='<div id="tvaPreviewBadge" role="note" style="position:fixed;left:max(8px,env(safe-area-inset-left,0px));bottom:calc(max(8px,env(safe-area-inset-bottom,0px)) + 74px);max-width:calc(100vw - 16px - env(safe-area-inset-left,0px) - env(safe-area-inset-right,0px));box-sizing:border-box;z-index:2147483000;pointer-events:none;font:600 10px/1.25 -apple-system,BlinkMacSystemFont,Roboto,Arial,sans-serif;letter-spacing:.02em;color:#fff;background:rgba(143,29,42,.92);padding:3px 8px;border-radius:8px;white-space:normal;overflow-wrap:anywhere">PREVIEW · build BID<br>dati demo · Firebase disattivato</div>'.replace('BID',bid)
s=s.replace('</body>',badge+'\n</body>',1)
open(O+'/index.html','w',encoding='utf-8').write(s)
open(O+'/_headers','w').write("/*\n  X-Robots-Tag: noindex, nofollow\n  Referrer-Policy: no-referrer\n  Cache-Control: no-cache\n")
z=zipfile.ZipFile('/home/claude/outputs/tva-preview-td2.zip','w',zipfile.ZIP_DEFLATED)
for r,d,f in os.walk(O):
    for n in f: p=os.path.join(r,n); z.write(p,os.path.relpath(p,O))
z.close(); print(bid)
