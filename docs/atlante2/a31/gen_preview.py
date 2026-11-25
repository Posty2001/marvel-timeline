#!/usr/bin/env python3
"""A3.1 anteprima: 21 identita' con (a) illustrazione ORIGINALE archetipica derivata dai dati, (b) locandina del titolo da TMDB (hotlink, gia' autorizzata nel progetto).
Nessuna foto di attori, nessun ritratto Marvel. Esito: docs/atlante2/a31/anteprima.html (autonomo; le locandine TMDB si vedono solo con rete)."""
import json, base64, io, hashlib, html, re, colorsys
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFilter
R='/home/claude/marvel-timeline/'
idx=json.load(open(R+'atlante2/data/index.json')); BY={v['i']:v for v in idx['voci']}
tm=json.load(open(R+'data/atlante/blob/tmdbMap.json'))['voci']
sh={}
def dos(i):
    n=BY[i]['sh']
    if n not in sh: sh[n]=json.load(open(R+'atlante2/data/d/%03d.json'%n))
    return sh[n][i]
PICK=['id-iron-man','id-thor','id-wanda-maximoff','id-loki','id-hela','id-groot-successore','id-peter-parker-mcu','id-peter-parker-raimi','id-peter-parker-garfield','id-eddie-brock-venom','id-michael-morbius','id-johnny-blaze-ghost-rider','id-miles-morales','id-peter-b-parker','id-a-bomb','id-charles-xavier-fox','id-wolverine','id-magneto','id-wade-wilson-deadpool','id-jean-grey-fenice','id-johnny-storm-human-torch']
FAM={'sony':('Sony',(111,179,217)),'fox':('Fox',(240,149,74)),'mcu':('MCU',(245,154,35)),'anim':('Animazione',(180,138,224))}
def fam(u):
    if 'mcu' in u: return 'mcu'
    if any(k in u for k in ('fox','daredevil','earth-121698','blade','hulk-2003')): return 'fox'
    if any(k in u for k in ('animat','spider-verse','noir')): return 'anim'
    return 'sony'
TECH=r'armatur|tecnolog|cyber|robot|gadget|arma|scudo|lanciaragnatele|intelligenza'; MIS=r'magi|mistic|incant|stregon|illusion|sortileg|dimension'; COS=r'cosmic|energia|dio|asgard|telecin|fenice|realt|potere'
def arche(v,d):
    p=' '.join(''.join(x for x in f['t'] if isinstance(x,str)) for f in d['sec'].get('poteri',[])).lower()
    if v['k'] in ('v','c') or fam(v['u'])=='anim': return 'variante'
    if re.search(MIS,p): return 'mistico'
    if re.search(COS,p): return 'astratto'
    if re.search(TECH,p): return 'tecnologico'
    if 'forza' in p or 'rigener' in p or 'agil' in p: return 'agente'
    return 'cronista'
def art(v,d):
    a=arche(v,d); f=fam(v['u']); col=FAM[f][1]; seed=int(hashlib.sha256(v['i'].encode()).hexdigest(),16)
    im=Image.open(R+'docs/atlante2/revisione2/img/av_%s.webp'%a).convert('RGB')
    w,h=im.size; cw=int(w*(0.80+0.12*((seed>>3)%4)/3)); ch=int(cw*4/3)
    if ch>h: ch=h; cw=int(ch*3/4)
    x0=((seed>>8)%max(1,w-cw+1)); y0=((seed>>16)%max(1,h-ch+1)); im=im.crop((x0,y0,x0+cw,y0+ch)).resize((360,480),Image.LANCZOS)
    if (seed>>2)&1: im=ImageOps.mirror(im)
    g=ImageOps.grayscale(im); tint=ImageOps.colorize(g,black=(8,6,4),mid=tuple(int(c*0.55) for c in col),white=tuple(min(255,int(c*1.25)) for c in col))
    im=Image.blend(im,tint,0.52)
    bar=Image.new('RGB',(360,480),(0,0,0)); m=Image.linear_gradient('L').resize((360,480)); im=Image.composite(bar,im,m.point(lambda p:int(max(0,p-110)*0.9)))
    dr=ImageDraw.Draw(im); dr.rectangle([0,0,359,6],fill=col)
    b=io.BytesIO(); im.save(b,'WEBP',quality=74,method=6); return a,f,b.getvalue()
cards=[]; tot=0
for i in PICK:
    v=BY[i]; d=dos(i); a,f,by=art(v,d); tot+=len(by)
    ns=[x for x in d.get('app',[])]; first=next(((n,t) for n,t in ns if n in tm),None)
    poster=('https://image.tmdb.org/t/p/w185'+tm[first[0]]['p']) if first else None
    cards.append(dict(i=i,n=v['n'],u=idx['meta']['universi'].get(v['u'],{}).get('n',''),f=f,a=a,img='data:image/webp;base64,'+base64.b64encode(by).decode(),poster=poster,pt=(first[1] if first else ''),pn=(first[0] if first else ''),kind=v['k'],napp=len(ns)))
H=['<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>A3.1 Anteprima asset visivi</title><style>',
':root{color-scheme:dark}body{margin:0;background:#0e0b08;color:#ede0c0;font:14px/1.45 Inter,system-ui,sans-serif;padding:16px max(16px,env(safe-area-inset-left))}h1{font:700 26px Spectral,Georgia,serif;margin:0 0 6px;color:#f6ecd2}p{color:#b8a888;margin:6px 0}',
'.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(172px,1fr));gap:14px;margin-top:14px}.c{border:1px solid #4a3f2f;border-radius:16px;overflow:hidden;background:#17120c}.c .p{position:relative;aspect-ratio:3/4}.c img{display:block;width:100%;height:100%;object-fit:cover}',
'.c .t{padding:8px 10px}.c b{font:700 15px Spectral,Georgia,serif;color:#fff;display:block}.c small{color:#b8a888;display:block}.b{position:absolute;left:8px;bottom:8px;font-size:10px;padding:2px 8px;border-radius:10px;background:rgba(14,11,8,.82);border:1px solid var(--k);color:var(--k)}',
'.poster{display:flex;gap:8px;align-items:center;padding:8px 10px;border-top:1px solid #2f2619}.poster img{width:36px;height:54px;border-radius:4px;background:#2a2218;flex:none;object-fit:cover}.poster span{font-size:11px;color:#b8a888}.nob{font-size:11px;color:#b8a888;padding:8px 10px;border-top:1px solid #2f2619}.n{border:1px solid #6a5636;border-radius:14px;padding:12px;background:#1c1812;margin:12px 0}</style></head><body>',
'<h1>A3.1 · Anteprima asset visivi</h1><p>21 identità · MCU, Sony (Raimi, Garfield, SSU, Ghost Rider), Fox, animazione. <b>Sopra:</b> illustrazione <u>originale</u> verticale 3:4 (WebP ~%d KB cad.), archetipo derivato dai poteri dichiarati, colore = continuità. <b>Sotto:</b> locandina del primo titolo (TMDB, già in uso nel progetto).</p>'%(tot//len(PICK)//1024),
'<div class="n"><b>Cosa è e cosa non è.</b> Le illustrazioni sono <u>archetipiche</u>: non raffigurano il personaggio (nessun ritratto Marvel, nessuna foto di attore). Distinguono la <u>continuità</u> (colore) e un archetipo dai poteri, ma <b>non</b> l\'individuo: con 8 archetipi di base più identità condividono lo stesso soggetto (es. Iron Man e Thor). Questo è il limite che l\'anteprima vuole mostrare, non nascondere. Le locandine compaiono solo con connessione e solo per i titoli in cui il personaggio appare.</div><div class="g">']
for c in cards:
    k='rgb(%d,%d,%d)'%FAM[c['f']][1]
    H.append('<div class="c" style="--k:%s"><div class="p"><img alt="" src="%s"><span class="b">%s · %s</span></div><div class="t"><b>%s</b><small>%s</small></div>'%(k,c['img'],FAM[c['f']][0],c['a'],html.escape(c['n']),html.escape(c['u'])))
    H.append(('<div class="poster"><img alt="" loading="lazy" src="%s"><span>N°%s · %s<br>Locandina del titolo — TMDB</span></div>'%(c['poster'],c['pn'],html.escape(c['pt']))) if c['poster'] else '<div class="nob">Nessuna apparizione con locandina disponibile: solo illustrazione archetipica.</div>')
    H.append('</div>')
H.append('</div><p style="margin-top:18px">This product uses the TMDB API but is not endorsed or certified by TMDB.</p></body></html>')
open(R+'docs/atlante2/a31/anteprima.html','w',encoding='utf-8').write(''.join(H)); print(len(cards),'carte',tot//1024,'KB immagini totali', len(''.join(H))//1024,'KB html')
