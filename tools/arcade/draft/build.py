# Compone Secret Wars Draft 3.0: head/dialog da int3, payload 120 carte, core puro, engine v2, UI.
import json,re
L=open('/home/claude/arc/pk/draft_int3_backup.html').read().split('\n')
ID='20261117-1900-arcade-draft31r'
head=[x.replace('20261117-0900-arcade-int3',ID) for x in L[0:2]]
css=open('style.css').read();body=open('body.html').read();core=open('core.js').read();eng=open('engine.js').read();game=open('game.js').read()
roster=json.load(open('roster.json'))
scn={'asgard':[.3,.1,.15,.3,.15],'wakanda':[.15,.3,.1,.2,.25],'quantum':[.1,.25,.3,.1,.25],'battleworld':[.2,.2,.2,.2,.2]}
payload=json.dumps({'roster':roster,'scenarios':scn},ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
tail=[L[103],L[105],L[106],L[107],L[108]]
t="\n".join(tail)
t=t.replace("store.del(SAVE)","clearSave()").replace("$('go').onclick=battle;$('auto').onclick=()=>{assign=bestAssign(A).map;persist();render()};","$('go').onclick=battle;$('auto').onclick=()=>{assign=bestAssign(A).map;persist();rsel=null;render()};")
t=t.replace("warm(D.roster.map(c=>'../'+c.identity_card));","warm(D.roster.map(c=>c.identity_card?'../'+c.identity_card:null));")
assert 'clearSave()' in t and "c.identity_card?" in t
tail2="$('go').onclick=battle;$('auto').onclick=()=>{assign=bestAssign(A).map;persist();rsel=null;render()};\n$('recruit').onclick=recruit;\n"
js=core+"\nconst D=JSON.parse(document.querySelector('#payload').textContent),$=id=>document.getElementById(id);\n"+eng+"\nconst clearSave=()=>{store.del(SAVE);store.del(SAVE1)};\n"+game+"\n"+t+"\n"+tail2+"if(restore()){if(phase==='cinematic')phase='roles'}else phase='idle';render();\n"
out="\n".join(head)+"\n<style>\n"+css+"</style></head>\n"+body+L[56]+"\n<script id=\"payload\" type=\"application/json\">"+payload+"</script>\n<script>"+js+"</script></body></html>\n"
open('index.html','w').write(out)
open('/home/claude/arc/app/arcade/draft/index.html','w').write(out)
print(len(out))
