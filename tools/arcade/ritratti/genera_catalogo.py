import json,csv,statistics as S
ro=json.load(open('d3/roster.json'));ro=ro['roster'] if isinstance(ro,dict) else ro
SC={'asgard':[.3,.1,.15,.3,.15],'wakanda':[.15,.3,.1,.2,.25],'quantum':[.1,.25,.3,.1,.25],'battleworld':[.2]*5}
ST=['power','intelligence','speed','durability','versatility']
RL=['Avanguardia','Stratega','Ricognitore','Difensore','Specialista']
G={'A':'Avengers e alleati','X':'X-Men e mutanti','S':'Spider-Verse e simbionti','C':'Cosmici, mistici e cattivi'}
ids=[r['id'] for r in ro]
# manifest
mp='app/arcade/assets/draft_portraits/manifest.json';m=json.load(open(mp))
for r in ro:
    m['portraits'].setdefault(r['id'],{'name':r['name'],'file':None,'status':'missing','license':None,'source_url':None,'author':None,'rights_holder':None,'verified_on':None,'verified_by':None,'rights_confirmed':False,'sha256':None,'notes':''})
for k in list(m['portraits']):
    if k not in ids:del m['portraits'][k]
json.dump(m,open(mp,'w'),ensure_ascii=False,indent=1)
json.dump(ids,open('tools/roster_ids.json','w'))
# registro asset
with open('deliver/REGISTRO_ASSET.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f,delimiter=';');w.writerow(['ID','Nome','Versione','Percorso_previsto','Ritratto_attuale','Fonte','Stato_diritti','Fallback'])
    for r in ro:
        e=m['portraits'][r['id']];w.writerow([r['id'],r['name'],r['version'],'arcade/assets/draft_portraits/%s.webp'%r['id'],'nessuno' if not e['file'] else e['file'],'—','missing (nessuna immagine con diritti verificati)','segnaposto SVG originale generato dal codice'])
# catalogo
rows=[]
with open('deliver/CATALOGO_PERSONAGGI.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f,delimiter=';');w.writerow(['ID','Nome','Gruppo','Versione','Base','Potenza','Intelligenza','Velocità','Resistenza','Versatilità','Ruolo ideale','Valore Asgard','Valore Wakanda','Valore Quantico','Valore Battleworld','Capacità','Limiti'])
    for r in ro:
        s=[r['stats'][k] for k in ST];ideal=RL[s.index(max(s))]
        vals=[round(sum(a*b for a,b in zip(s,SC[k])),1) for k in('asgard','wakanda','quantum','battleworld')]
        w.writerow([r['id'],r['name'],r['group'],r['version'],r.get('base') or '',*s,ideal,*vals,r['cap'],r['lim']]);rows.append((r,s,ideal,vals))
bw=[v[3][3] for v in rows]
print('valore BW: min %.1f mediana %.1f max %.1f'%(min(bw),S.median(bw),max(bw)))
md=['# Catalogo personaggi — Secret Wars Draft 3.0 (120 carte)\n','Valori di **gioco**, non canonici: scala 1–100 per carta/statistica, assegnata con la rubrica di `CRITERI_VALORI.md`. Le varianti significative sono carte separate.\n','| ID | Nome | Gruppo | Versione | P | I | V | R | Vs | Ruolo ideale | Val. BW |','|---|---|---|---|--:|--:|--:|--:|--:|---|--:|']
for r,s,i,v in rows:md.append('| %s | %s | %s | %s | %d | %d | %d | %d | %d | %s | %.1f |'%(r['id'],r['name'],r['group'],r['version'],*s,i,v[3]))
md.append('\nCapacità e limiti di ogni carta: `CATALOGO_PERSONAGGI.csv`.')
open('deliver/CATALOGO_PERSONAGGI.md','w').write('\n'.join(md))
from collections import Counter
print(Counter(r['group'] for r in ro),Counter(x[2] for x in rows))
