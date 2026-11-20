import json,csv,statistics as st
GN={'A':('Avengers e alleati','avengers-e-alleati'),'X':('X-Men e mutanti','x-men-e-mutanti'),'S':('Spider-Verse e simbionti','spider-verse-e-simbionti'),'C':('Cosmici e altri','cosmici-e-altri')}
BASE={'phoenix':'jean-grey','zarathos':'ghost-rider','rune-king-thor':'thor'}
ST_K=['power','intelligence','speed','durability','versatility'];SN=['Potenza','Intelligenza','Velocità','Resistenza','Versatilità']
SC={'asgard':[.3,.1,.15,.3,.15],'wakanda':[.15,.3,.1,.2,.25],'quantum':[.1,.25,.3,.1,.25],'battleworld':[.2]*5}
old=json.load(open('/home/claude/arc/tools/roster_ids.json'))
oldfull={c['id']:c for c in __import__('json').loads(__import__('re').search(r'<script[^>]*id="payload"[^>]*>(.*?)</script>',open('/home/claude/arc/pk/draft_int3_backup.html').read(),__import__('re').S).group(1))['roster']}
R=[];csvrows=[]
for l in open('roster_data.txt'):
    if not l.strip() or l.startswith('#'):continue
    i,n,g,v,s,cap,lim=l.rstrip('\n').split('|');s=[int(x) for x in s.split(',')];assert len(s)==5 and all(30<=x<=99 for x in s),i
    g_name,g_tag=GN[g];stats=dict(zip(ST_K,s));best=SN[s.index(max(s))];worst=SN[s.index(min(s))]
    nota='Picco %s %d, punto debole %s %d. Valori di gioco assegnati con la scala v3 (vedi CRITERI_VALORI.md), non misure canoniche.'%(best,max(s),worst,min(s))
    e=dict(id=i,name=n,group=g_name,continuity='Marvel Comics / Terra-616 (interpretazione ludica; verificare eccezioni)',portrait=None,stats=stats,tags=[g_tag],synergies=[],status='playable_game_balance_v3',balance_version='v3.0-gameplay',version=v,base=BASE.get(i),cap=cap,lim=lim,nota=nota,
      identity_card=oldfull[i]['identity_card'] if i in oldfull else None,identity_card_kind='typographic_placeholder_not_character_portrait' if i in oldfull else None,origin='roster_v1' if i in oldfull else 'roster_v3')
    R.append(e)
assert len(R)==120 and len({e['id'] for e in R})==120 and all(i in {e['id'] for e in R} for i in old)
json.dump(R,open('roster.json','w'),ensure_ascii=False,indent=0)
json.dump([e['id'] for e in R],open('roster_ids.json','w'))
# statistiche
def val(e,w):return sum(e['stats'][k]*w[j] for j,k in enumerate(ST_K))
ideal=lambda e:max(range(5),key=lambda j:(e['stats'][ST_K[j]],-j))
from collections import Counter
print('ruoli ideali',Counter(['avanguardia','stratega','ricognitore','difensore','specialista'][ideal(e)] for e in R))
for k,w in SC.items():
    v=sorted(val(e,w) for e in R);print(k,'min %.1f p10 %.1f med %.1f p90 %.1f max %.1f'%(v[0],v[12],st.median(v),v[108],v[-1]))
print('top neutro',[(e['name'],round(val(e,SC['battleworld']))) for e in sorted(R,key=lambda e:-val(e,SC['battleworld']))[:12]])
print('bottom',[(e['name'],round(val(e,SC['battleworld']))) for e in sorted(R,key=lambda e:val(e,SC['battleworld']))[:8]])
