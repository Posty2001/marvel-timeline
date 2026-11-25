# -*- coding: utf-8 -*-
import json,re,base64,sys
from gen2 import *
SR=[('Loki','Personaggio · Variante','#b48ae0'),('Thor','Personaggio','#6fb3d9'),('Thanos','Personaggio','#ff6a5c'),('Mjolnir','Artefatto','#e6b25a'),('Tesseract','Artefatto','#4fd0ff'),('Lo Schiocco','Evento','#ff8a3c'),('Battaglia di New York','Evento','#ff8a3c'),('Asgard','Luogo','#E3C79B'),('Arishem','Entità cosmica','#d46aff'),('TVA','Organizzazione','#F59A23'),('Sacra Timeline','Universo','#F59A23'),('Steve Rogers','Personaggio','#e6b25a'),('Sam Wilson','Personaggio','#6fb3d9')]
def f_search():
    return '''
<div class="pad" style="padding-top:84px;padding-bottom:30px">
<div class="card" style="display:flex;align-items:center;gap:10px;padding:0 14px;height:54px;border-color:var(--acc)"><span style="color:var(--acc);width:22px">%s</span><input id="q" value="o" autocomplete="off" style="flex:1;background:none;border:0;outline:0;color:#fff;font:500 17px Inter,sans-serif;min-width:0"></div>
<div class="chips" style="padding:12px 0 6px" id="sf"><span class="chip on" data-t="">Tutto</span><span class="chip" data-t="Personaggio">Personaggi</span><span class="chip" data-t="Evento">Eventi</span><span class="chip" data-t="Artefatto">Artefatti</span><span class="chip" data-t="Luogo">Luoghi</span></div>
<div class="note" style="margin:8px 0">Recenti: <b>Mjolnir</b> · <b>Sacra Timeline</b></div>
<div id="sr"></div></div>
'''%ICON['search']

def f_coll():
    col=lambda t,s,img,pos,c,p:'<div class="card" style="height:170px;background:%s %s/cover;border-color:%s88"><div class="fade" style="background:linear-gradient(180deg,transparent 30%%,rgba(10,8,5,.95))"></div><div style="position:absolute;left:14px;right:14px;bottom:12px"><b class="h-serif" style="font-size:20px">%s</b><div class="note">%s</div><div style="height:6px;border-radius:3px;background:#2c2318;margin-top:8px"><div style="height:100%%;width:%d%%;border-radius:3px;background:%s;box-shadow:0 0 8px %s"></div></div></div></div>'%(I(img),pos,c,t,s,p,c,c)
    return '''
<div class="pad" style="padding-top:84px;padding-bottom:36px">
<div class="kick" style="color:#e9a0a6">I tuoi preferiti</div>
<div class="rail" style="padding:10px 0;margin:0 -16px;padding-left:16px">
%s%s%s</div>
<div class="kick" style="color:#e9a0a6;margin-top:20px">Collezioni</div>
<div style="display:grid;gap:12px;margin-top:10px">
%s%s%s
<div class="card" style="padding:16px;border-style:dashed;display:flex;align-items:center;gap:10px;justify-content:center;color:var(--acc)">%s Nuova collezione</div></div>
<div class="note" style="margin-top:14px">Titoli e progressi di esempio: nell'app sono le collezioni dell'utente, salvate in locale.</div></div>
'''%(tile('Loki','av_variante','center top','Dossier','#b48ae0',150).replace('width:auto','width:120px'),tile('Mjolnir','artefatti','left','Artefatto','#e6b25a',150).replace('width:auto','width:120px'),tile('Asgard','luoghi','center','Luogo','#E3C79B',150).replace('width:auto','width:120px'),
 col('Fratelli e rivali','4 dossier su 6','personaggi','center','#e0707a',66),col('Stregoneria','2 dossier su 8','arti_mistiche','center','#d46aff',25),col('Da rivedere','Aggiornata oggi','cronologie','center','#6fb3d9',40),ICON['plus'])

BADGES=[('Esploratore','25 dossier esplorati','ok'),('Archivista','100 dossier esplorati','ok'),('Cartografo','10 universi completati','wait:servono i collegamenti personaggio→universo'),('Cacciatore di varianti','3 hub completati','wait:oggi 1 hub confermato'),('Custode degli artefatti','25 artefatti','wait:nel registro ce ne sono meno di 25'),('Storico del Multiverso','25 eventi','wait:nel registro ce ne sono meno di 25'),('Maestro del Nexus','100 relazioni narrative distinte','wait:le relazioni verificate sono ancora poche'),('Custode del Multiverso','500 dossier esplorati','wait:nel registro ci sono meno di 500 dossier')]
def f_prog():
    b=''.join('<div class="card" style="padding:12px;display:flex;gap:12px;align-items:center;%s"><div style="width:44px;height:44px;border-radius:50%%;display:flex;align-items:center;justify-content:center;flex:none;border:2px solid %s;color:%s;%s"><span style="width:22px">%s</span></div><div style="flex:1;min-width:0"><b style="font-family:Spectral,serif;font-size:16px">%s</b><div class="note">%s</div>%s</div><span class="badge" style="color:%s">%s XP</span></div>'%(
      '' if s=='ok' else 'opacity:.78','#F59A23' if s=='ok' else '#6a5a40','#F59A23' if s=='ok' else '#8a7a5a','box-shadow:0 0 14px rgba(245,154,35,.5)' if s=='ok' else '',ICON['star'] if s=='ok' else ICON['lock'],n,r,'' if s=='ok' else '<div class="note" style="color:#d9a35a;margin-top:2px">Non ancora ottenibile: '+s[5:]+'</div>','#F59A23' if s=='ok' else '#8a7a5a','+40') for n,r,s in BADGES)
    return '''
<div class="pad" style="padding-top:84px;padding-bottom:36px">
<div class="card rev in" style="padding:18px;display:flex;gap:16px;align-items:center;border-color:var(--acc)">
<svg width="104" height="104" viewBox="0 0 104 104"><circle cx="52" cy="52" r="44" stroke="#2c2318" stroke-width="9" fill="none"/><circle id="pr" cx="52" cy="52" r="44" stroke="#F59A23" stroke-width="9" fill="none" stroke-linecap="round" stroke-dasharray="276.5" stroke-dashoffset="276.5" transform="rotate(-90 52 52)" style="transition:stroke-dashoffset 1.4s;filter:drop-shadow(0 0 6px #F59A23)"/><text x="52" y="57" text-anchor="middle" fill="#fff" font-size="22" font-family="Spectral" font-weight="700">18</text></svg>
<div><div class="kick">Esplorazione di oggi</div><b class="h-serif" style="font-size:20px">18 / 30 XP</b><div class="note" style="margin-top:4px">Oltre il tetto giornaliero gli XP non si perdono: restano in coda e vengono accreditati nei giorni successivi.</div></div></div>
<div class="card" style="padding:14px;margin-top:12px"><div class="kick">Quando un dossier è «esplorato»</div><div class="note" style="margin-top:6px;font-size:12.5px;color:#d9c9a6">Resti almeno 10 secondi, scorri almeno il 60%% e consulti almeno 2 sezioni, nella stessa apertura. Una sola volta per scheda; alias, segnaposto e duplicati non contano.</div></div>
<div class="kick" style="margin-top:20px">Badge di esplorazione</div><div style="display:grid;gap:10px;margin-top:10px">%s</div>
<div class="note" style="margin-top:14px">I traguardi già ottenuti non vengono mai revocati se il registro cresce. I valori sono dimostrativi.</div></div>
'''%b

FRAMES=[
 (1,'Home Atlante','#F59A23',f_home,'Portale animato, dossier in primo piano, categorie illustrate, ripresa dell\'esplorazione.'),
 (2,'Catalogo personaggi','#E3C79B',f_catalog,'Griglia illustrata a due colonne e modalità elenco (tocca per cambiare).'),
 (3,'Dossier personaggio','#b48ae0',f_dossier,'Identità cromatica viola/oro, sezioni navigabili, relazioni colorate. Scorri.'),
 (4,'Hub varianti · Peter Parker','#ff5c5f',f_hub,'Il numero di identità è calcolato dai dati: 6 mostrate, 6 dichiarate.'),
 (5,'Confronto personaggi','#e6b25a',f_compare,'Ritratti affiancati, differenze narrative, nessuna statistica inventata.'),
 (6,'Multiverso','#4fd0ff',f_multi,'Mappa interattiva: trascina, zoom, tocca un nodo.'),
 (7,'Nexus delle relazioni','#4fd0ff',f_nexus,'Tocca un volto per cambiare il centro; relazioni colorate per tipo.'),
 (8,'Eventi, saghe e battaglie','#ff8a3c',f_events,'Copertine, cronologia interna, protagonisti e conseguenze.'),
 (9,'Artefatti e armi','#d46aff',f_art,'Schede con luce e carattere propri per ogni oggetto.'),
 (10,'Organizzazioni, luoghi, pianeti','#6fb3d9',f_places,'Tre sezioni in un\'unica sala (tocca i tab).'),
 (11,'Specie ed entità cosmiche','#9fe0d4',f_cosmic,'Celestiali con badge «sullo schermo / solo fumetti»; Thanos resta personaggio.'),
 (12,'Ricerca globale','#E3C79B',f_search,'Risultati per tipo mentre scrivi (prova a digitare).'),
 (13,'Preferiti e collezioni','#e9a0a6',f_coll,'Copertine e progressione delle collezioni.'),
 (14,'Progressione dell\'esplorazione','#F59A23',f_prog,'XP con tetto giornaliero, badge reali e stato di disponibilità.'),
]
SOLID={6:False,7:False,12:True,13:True,14:True}
BG={6:'',}
def build(mode):
    SH={'Home Atlante': 'Atlante', 'Catalogo personaggi': 'Catalogo', 'Dossier personaggio': 'Dossier', 'Hub varianti · Peter Parker': 'Hub varianti', 'Confronto personaggi': 'Confronto', 'Nexus delle relazioni': 'Nexus', 'Eventi, saghe e battaglie': 'Eventi e saghe', 'Artefatti e armi': 'Artefatti', 'Organizzazioni, luoghi, pianeti': 'Mondi e potenze', 'Specie ed entità cosmiche': 'Entità cosmiche', 'Ricerca globale': 'Ricerca', 'Preferiti e collezioni': 'Collezioni', "Progressione dell\\'esplorazione": 'Progressione'}
    fr=''.join(frame(i,n,a,f(),note,title=SH.get(n,n)) for i,n,a,f,note in FRAMES)
    idx=''.join('<a href="#f%d">%d</a>'%(i,i) for i,*_ in FRAMES)
    CMP=[('Home','cur_01_atlante.jpg','r2_1.jpg'),('Personaggi','cur_p_Personaggi.jpg','r2_2.jpg'),('Dossier','cur_d1.jpg','r2_3.jpg'),('Multiverso','cur_p_Multiverso.jpg','r2_6.jpg'),('Relazioni','cur_p_Relazioni.jpg','r2_7.jpg'),('Entità cosmiche','cur_p_Entita_Cosmiche.jpg','r2_11.jpg')]
    cm=''.join('<div class="sec"><h2>%s</h2></div><div class="cmp" data-i="%d"><img src="img/%s" alt="Atlante attuale"><img class="after" src="img/%s" alt="Atlante 2.0"><span class="tag" style="left:10px">ATTUALE</span><span class="tag" style="right:10px;background:#F59A23;color:#1a1208">2.0</span><div class="hnd"><i>↔</i></div></div>'%(t,k,a,b) for k,(t,a,b) in enumerate(CMP))
    keep='''<div class="card" style="padding:16px;margin-top:10px"><div class="kick">Cosa conserviamo</div><p>Shell «TVA Archives» con titolo e tasto indietro · pillola «App Marvel» · linguetta ambra di Miss Minutes · palette nero caldo + oro/ambra · titoli Spectral · portali illustrati per capitolo · animazioni lente di respiro e scintillio · tutti gli ID e i link esistenti.</p><div class="kick" style="margin-top:12px">Cosa cambia</div><p>Più immagine e meno rettangoli · ogni sala ha un colore e una personalità · schede con ritratto · mappa e Nexus manipolabili · ricerca che risponde mentre scrivi · progressione visibile e onesta sui badge non ancora ottenibili.</p></div>'''
    html='''<!DOCTYPE html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Atlante 2.0 Revisione 2</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Spectral:wght@500;700&display=swap">
<style>'''+open('style.css').read()+'''</style>
<div class="pg"><div class="top"><div class="lab">TVA Archives · Anteprima di design</div><h1>Atlante 2.0<br>Revisione 2</h1><p>14 schermate vive con le immagini dell'app. Prima il confronto con l'Atlante attuale, poi le schermate. Nessuna implementazione.</p></div>
<div class="idx"><a href="#cmp">Confronto</a>'''+idx+'''</div>
<div id="cmp"><div class="sec"><h2>Atlante attuale ↔ Atlante 2.0</h2><p>Trascina la maniglia ambra.</p></div>'''+cm+keep+'''</div>'''+fr+'''</div><script>window.__SR='''+json.dumps(SR,ensure_ascii=False)+''';window.__AV='''+json.dumps({k:'img/av_%s.webp'%k for k in ['variante','esploratore','sentinella','mistico','cronista','astratto','agente','tecnologico']})+''';'''+open('app.js').read()+'''</script>'''
    if mode=='inline':
        def r(m):
            p=m.group(1);ext=p.rsplit('.',1)[1];mt={'webp':'image/webp','jpg':'image/jpeg'}[ext]
            try: d=base64.b64encode(open('img/'+p,'rb').read()).decode()
            except FileNotFoundError: return m.group(0)
            return 'data:%s;base64,%s'%(mt,d)
        html=re.sub(r'(?<=url\()img/([\w\-]+\.\w+)(?=\))',lambda m:r(m),html)
        html=re.sub(r'"(img/av_\w+\.webp)"',lambda m:'"'+r(type('M',(),{'group':lambda self,i=0:m.group(1)[4:]})())+'"',html)
        html=re.sub(r'(?<=src=")img/([\w\-]+\.\w+)(?=")',lambda m:r(m),html)
    return html
if __name__=='__main__':
    m=sys.argv[1] if len(sys.argv)>1 else 'repo'
    open('index.html' if m=='repo' else 'inline.html','w').write(build(m))
