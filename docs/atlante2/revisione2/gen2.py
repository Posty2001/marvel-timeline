# -*- coding: utf-8 -*-
from gen1 import *
def hubcard(n,a,c,sub,actor):
    return '<div class="pt hid" style="width:auto;height:200px;background-image:%s;border-color:%s88"><span class="badge" style="position:absolute;left:10px;top:10px;z-index:3;color:%s;background:rgba(10,8,5,.6)">%s</span><div class="t"><b style="font-size:15px">%s</b><span>%s</span></div></div>'%(I(a),c,c,sub,n,actor)
def f_hub():
    ids=[('Peter Parker','av_agente','#ff5c5f','FUMETTI · TERRA-616','Identità originale'),('Peter Parker','av_esploratore','#4fa8ff','MCU','Tom Holland'),('Peter Parker','av_sentinella','#e6b25a','TRILOGIA RAIMI','Tobey Maguire'),('Peter Parker','av_tecnologico','#4fd0ff','THE AMAZING','Andrew Garfield'),('Peter Parker','av_cronista','#f0a63a','ANIMAZIONE','Your Friendly Neighborhood'),('Peter B. Parker','av_astratto','#d46aff','SPIDER-VERSE','Variante animata')]
    cards=''.join(hubcard(*x) for x in ids)
    return '''
<div class="hero" style="height:300px"><div class="bgi kb" style="background-image:%s;background-position:center 35%%;opacity:.8"></div><div class="fade"></div>
<svg style="position:absolute;inset:0" width="390" height="300"><g stroke="#ff5c5f" stroke-opacity=".5" fill="none"><circle cx="195" cy="160" r="60"/><circle cx="195" cy="160" r="95" stroke-dasharray="4 8"/></g></svg>
<div style="position:absolute;left:16px;right:16px;bottom:16px"><span class="badge" style="color:#ff8a8c">HUB MULTIVERSALE</span><h1 class="h-serif" style="font-size:34px;margin:6px 0 2px">Peter Parker</h1>
<div style="color:#e5d6b4"><b id="hn" style="color:#ff8a8c">6</b> identità distinte · un solo hub</div></div></div>
<div class="pad" style="margin-top:12px"><div class="note">L'hub non è un personaggio in più: raccoglie le identità, ognuna con la propria continuità. Il numero si calcola dai dati.</div></div>
<div class="pad" style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px">%s</div>
<div class="pad" style="margin:18px 0 30px"><div class="card" style="padding:14px;border-style:dashed"><span class="badge" style="color:#f0a63a">FUORI DALL'HUB</span><div class="note" style="margin-top:8px">Schede collegate ma non identità di Peter: <b>Deadpool & Wolverine</b> (apparizione), <b>Quill</b> (omonimo, altro personaggio).</div></div></div>
'''%(I('universi'),cards)

def f_compare():
    rows=[('Origine dei poteri','Siero del supersoldato','Esoscheletro EXO-7 Falcon e addestramento'),('Equipaggiamento','Scudo','Ali, scudo (dopo il passaggio del mantello)'),('Punti di forza','Tattica, resistenza, leadership','Mobilità aerea, adattabilità'),('Debolezze','Bozza da validare','Bozza da validare')]
    tr=''.join('<tr><th colspan=2>%s</th></tr><tr><td>%s</td><td>%s</td></tr>'%r for r in rows)
    return '''
<div style="display:grid;grid-template-columns:1fr 1fr;height:340px;position:relative;margin-top:0">
<div style="background:%s center top/cover;position:relative"><div class="fade"></div><div style="position:absolute;left:12px;bottom:12px"><span class="badge" style="color:#e6b25a">AGENTE</span><br><b class="h-serif" style="font-size:22px">Steve<br>Rogers</b></div></div>
<div style="background:%s center top/cover;position:relative"><div class="fade"></div><div style="position:absolute;left:12px;bottom:12px"><span class="badge" style="color:#6fb3d9">ESPLORATORE</span><br><b class="h-serif" style="font-size:22px">Sam<br>Wilson</b></div></div>
<div style="position:absolute;left:50%%;top:0;bottom:0;width:2px;background:linear-gradient(#e6b25a,#6fb3d9)"></div>
<div class="glow" style="position:absolute;left:50%%;top:50%%;margin:-22px;width:44px;height:44px;border-radius:50%%;background:#1a1208;border:2px solid var(--acc);display:flex;align-items:center;justify-content:center;font-weight:700;color:var(--acc)">VS</div></div>
<div class="pad" style="padding-bottom:30px"><div class="note" style="margin:12px 0">Confronto narrativo: nessuna statistica numerica presentata come canonica.</div>
<table class="cp"><tr><th style="color:#e6b25a">Steve</th><th style="color:#6fb3d9">Sam</th></tr>%s</table>
<div class="kick" style="margin-top:20px">Differenze chiave</div><div class="card" style="padding:14px;margin-top:8px"><div>Steve incarna il mantello; Sam lo eredita. Stessi simboli, strumenti e percorsi diversi.</div></div>
<div class="kick" style="margin-top:20px">Apparizioni condivise</div><div class="note" style="margin-top:6px">Elenco dalle schede del registro, ordinato per uscita.</div></div>
'''%(I('av_agente'),I('av_esploratore'),tr)

NODES=[('MCU · Earth-199999',190,205,26,'#4fd0ff','Continuità principale','Linea di riferimento di questa guida.',93,202),
('Raimi-Verse',70,150,15,'#e6b25a','Universo autonomo','Continuità cinematografica propria; ricompare nel MCU come variante.',4,9),
('Garfield-Verse',70,255,15,'#e6b25a','Universo autonomo','Continuità cinematografica propria; ricompare nel MCU come variante.',3,7),
('SSU Sony',130,60,17,'#e6b25a','Universo autonomo','Il legame con l\'MCU non è mai stato chiarito del tutto.',6,18),
('Fox-Verse',300,70,20,'#ff6a5c','Universo autonomo','Continuità propria dei film Fox, non una linea unica e continua.',14,40),
('Earth-828',320,170,13,'#4fa89e','Diramazione','Universo alternativo del multiverso MCU, separato dalla linea principale.',1,6),
('Earth-838',335,260,12,'#4fa89e','Diramazione','Universo alternativo del multiverso MCU, separato dalla linea principale.',0,1),
('What If…?',260,330,16,'#4fa89e','Diramazione','Linee temporali distinte, ciascuna nata da un evento divergente da Earth-199999.',3,5),
('X-Men \'97',290,135,13,'#ff6a5c','Universo autonomo','Continua X-Men: The Animated Series; nessun collegamento confermato con il MCU.',3,5),
('Your Friendly…',140,330,13,'#4fa89e','Diramazione','Linea alternativa del multiverso MCU; collegamenti con la principale non dimostrati.',2,3),
('Spider-Verse',50,335,16,'#d46aff','Universo autonomo','Dichiarato non canonico rispetto al MCU live-action.',3,9),
('Daredevil/Elektra',62,60,12,'#b48ae0','Universo autonomo','Continuità propria dei due film.',2,7),
('TVA · fuori dal tempo',195,360,17,'#F59A23','Luogo narrativo (non un universo)','Luogo fuori dal multiverso: non è una linea temporale.',2,7)]
def f_multi():
    nodes=''.join('<g class="mn" data-n="%s" data-k="%s" data-d="%s" data-t="%d" data-p="%d" transform="translate(%d %d)"><circle r="%d" fill="%s" opacity=".18"><animate attributeName="r" values="%d;%d;%d" dur="3s" repeatCount="indefinite"/></circle><circle r="%d" fill="#0e0b08" stroke="%s" stroke-width="2"/><circle r="%d" fill="%s" opacity=".85"/><text y="%d" text-anchor="middle" fill="#ede0c0" font-size="10.5" font-family="Inter">%s</text></g>'%(n,k,d,t,p,x,y,r+8,c,r+6,r+14,r+6,r,c,r//2,c,r+17,n) for n,x,y,r,c,k,d,t,p in NODES)
    lines=''.join('<line x1="190" y1="205" x2="%d" y2="%d" stroke="%s" stroke-opacity=".3" stroke-dasharray="3 6"/>'%(x,y,c) for n,x,y,r,c,k,d,t,p in NODES[1:])
    return '''
<div id="mapw" style="position:absolute;inset:0;background:radial-gradient(circle at 50%% 45%%,#2a1d38 0%%,#0e0b08 70%%);overflow:hidden;touch-action:none"><div class="bgi" style="background-image:%s;opacity:.35"></div><div class="tw"></div>
<svg id="msvg" viewBox="0 0 390 420" width="390" height="420" style="position:absolute;left:0;top:110px;transform-origin:195px 210px"><g id="mg">%s%s</g></svg></div>
<div style="position:absolute;right:12px;top:80px;z-index:20;display:flex;flex-direction:column;gap:8px"><button class="rb" id="zi">%s</button><button class="rb" id="zo">%s</button></div>
<div style="position:absolute;left:16px;top:80px;z-index:20"><div class="kick">Mappa del Multiverso</div><div class="note">Trascina · pizzica · tocca un nodo<br>Nodi, nature e conteggi dal registro reale (selezione)</div></div>
<div id="msheet" class="card" style="position:absolute;left:12px;right:12px;bottom:14px;z-index:25;padding:14px;border-color:var(--acc);background:rgba(16,12,8,.94)">
<div class="kick" id="mk">Universo</div><b class="h-serif" id="mt" style="font-size:24px;display:block;margin:4px 0">Seleziona un nodo</b><div class="note" id="md">Ogni nodo apre l'universo con i suoi personaggi, eventi e opere.</div>
<div style="display:flex;gap:8px;margin-top:12px"><span class="btn fill" style="height:40px">Apri universo</span><span class="btn" style="height:40px">Personaggi</span></div></div>

'''%(I('multiverso'),lines,nodes,ICON['plus'],ICON['minus'])

def f_nexus():
    return '''
<div style="position:absolute;inset:0;background:radial-gradient(circle at 50%% 45%%,#1d2a3a 0%%,#0e0b08 70%%)"><div class="bgi" style="background-image:%s;opacity:.4"></div><div class="tw"></div>
<svg id="nx" viewBox="0 0 390 600" width="390" height="600" style="position:absolute;left:0;top:90px"></svg></div>
<div style="position:absolute;left:16px;top:80px;z-index:20"><div class="kick">Nexus delle relazioni</div><div class="note">Tocca un volto per renderlo il centro</div></div>
<div class="chips" style="position:absolute;left:0;right:0;bottom:84px;z-index:20"><span class="chip"><i class="dotc" style="background:#e0707a"></i>Famiglia</span><span class="chip"><i class="dotc" style="background:#4fd0ff"></i>Alleato</span><span class="chip"><i class="dotc" style="background:#ff6a5c"></i>Avversario</span><span class="chip"><i class="dotc" style="background:#b48ae0"></i>Variante</span><span class="chip"><i class="dotc" style="background:#E3C79B"></i>Correlato</span></div>
<div class="card" style="position:absolute;left:12px;right:12px;bottom:14px;z-index:20;padding:12px"><span class="badge" style="color:#f0a63a">DIAGNOSTICA DATI</span> <span class="note">Le relazioni non verificate restano qui, non nel grafo.</span></div>
'''%I('relazioni')

EV=[('Battaglia di New York','2012','eventi','center 30%','Avengers, Chitauri, Loki','Nasce il team; il Tesseract torna sotto controllo di Asgard.'),('Battaglia di Sokovia','2015','universi','center','Avengers, Ultron','La città è distrutta; i Vendicatori si riformano.'),('Scontro all\'aeroporto','2016','multiverso','left','Team Cap, Team Iron Man','Gli Accordi di Sokovia dividono il gruppo.'),('Lo Schiocco','2018','entita_cosmiche','center','Thanos, Guardiani, Avengers','Metà della vita nell\'universo svanisce.'),('Battaglia finale','2023','eventi','right','Avengers, Thanos','L\'inversione dello Schiocco e la caduta di Thanos.')]
def f_events():
    ev=''.join('<div class="rev" style="position:relative;margin-bottom:18px"><i style="position:absolute;left:-27px;top:8px;width:14px;height:14px;border-radius:50%%;background:var(--acc);box-shadow:0 0 12px var(--acc)"></i><div class="card" style="height:150px;background:%s %s/cover"><div class="fade" style="background:linear-gradient(180deg,transparent 20%%,rgba(10,8,5,.95))"></div><div style="position:absolute;left:14px;right:14px;bottom:12px"><span class="kick">%s</span><br><b class="h-serif" style="font-size:20px">%s</b></div></div><div class="note" style="margin:8px 2px 2px"><b style="color:#e5d6b4">Protagonisti:</b> %s<br><b style="color:#e5d6b4">Conseguenze:</b> %s</div></div>'%(I(i),p,y,n,pr,c) for n,y,i,p,pr,c in EV)
    return '''
<div class="hero" style="height:230px"><div class="bgi kb" style="background-image:%s"></div><div class="fade"></div><div style="position:absolute;left:16px;bottom:14px"><div class="kick">Saghe, eventi e battaglie</div><h1 class="h-serif" style="font-size:28px;margin:4px 0">Cronologia narrativa</h1><div class="note">Ordine interno dell'universo · date dichiarate nelle opere</div></div></div>
<div class="chips" style="margin:10px 0"><span class="chip on">Eventi</span><span class="chip">Saghe</span><span class="chip">Battaglie</span></div>
<div class="pad" style="padding-left:38px;padding-bottom:40px"><div style="border-left:2px solid #7a3a2a;padding-left:0;margin-left:-14px;padding-left:14px">%s</div></div>
'''%(I('cronologie'),ev)

def tile(n,img,pos,sub,c,h=170):
    return '<div class="pt z" style="width:auto;height:%dpx;background-image:%s;background-position:%s;border-color:%s77"><div class="t"><b style="font-size:16px">%s</b><span>%s</span></div></div>'%(h,I(img),pos,c,n,sub)
def f_art():
    return '''
<div class="hero" style="height:300px"><div class="bgi kb" style="background-image:%s;background-position:center 40%%"></div><div class="fade"></div><div style="position:absolute;left:16px;bottom:14px"><div class="kick">Reliquiario</div><h1 class="h-serif" style="font-size:30px;margin:4px 0">Artefatti e armi</h1><div class="note">Ogni oggetto ha la sua luce, il suo portatore, la sua storia</div></div></div>
<div class="chips" style="margin:10px 0"><span class="chip on">Tutti</span><span class="chip">Gemme</span><span class="chip">Armi</span><span class="chip">Reliquie magiche</span></div>
<div class="pad rev" style="display:grid;grid-template-columns:1fr 1fr;gap:12px;padding-bottom:36px">
%s%s%s%s%s%s</div>
'''%(I('reliquiario'),tile('Gemme dell\'Infinito','reliquiario','50% 70%','Sei gemme · sei poteri','#d46aff',210),tile('Guanto dell\'Infinito','artefatti','40% 20%','Thanos, Stark','#e6b25a',210),tile('Mjolnir','arti_mistiche','80% 70%','Thor, Asgard','#6fb3d9'),tile('Scudo di Capitan America','organizzazioni','55% 55%','Steve, Sam','#ff6a5c'),tile('Tesseract','reliquiario','50% 25%','Gemma dello Spazio','#4fd0ff'),tile('Darkhold','arti_mistiche','30% 60%','Libro maledetto','#b0304a'))

def f_places():
    return '''
<div class="hero" style="height:260px"><div class="bgi kb" style="background-image:%s"></div><div class="fade"></div><div style="position:absolute;left:16px;bottom:14px"><div class="kick">Organizzazioni · Luoghi · Pianeti</div><h1 class="h-serif" style="font-size:28px;margin:4px 0">Mondi e potenze</h1></div></div>
<div class="seg" id="pseg" style="margin:12px 16px"><button class="on" data-p="o">Organizzazioni</button><button data-p="l">Luoghi</button><button data-p="p">Pianeti</button></div>
<div class="pad" style="padding-bottom:36px">
<div class="pp" data-p="o" style="display:grid;gap:12px">%s%s%s</div>
<div class="pp" data-p="l" style="display:none;gap:12px">%s%s%s</div>
<div class="pp" data-p="p" style="display:none;gap:12px">%s%s%s</div></div>
'''%(I('luoghi'),
 tile('TVA','organizzazioni','12% 40%','Autorità sulle linee temporali','#F59A23',150),tile('Avengers','organizzazioni','55% 60%','Team di eroi','#4fd0ff',150),tile('S.H.I.E.L.D.','organizzazioni','95% 50%','Agenzia di spionaggio','#6fb3d9',150),
 tile('Asgard','luoghi','50% 15%','Regno degli dèi','#E3C79B',150),tile('Wakanda','luoghi','10% 70%','Nazione tecnologica','#b48ae0',150),tile('Sanctum Sanctorum','arti_mistiche','70% 40%','New York','#d46aff',150),
 tile('Titano','universi','8% 30%','Mondo di Thanos','#ff6a5c',150),tile('Knowhere','entita_cosmiche','80% 60%','Avamposto cosmico','#4fa89e',150),tile('Xandar','universi','92% 80%','Pianeta dei Nova','#6fb3d9',150))

def f_cosmic():
    return '''
<div class="hero" style="height:300px"><div class="bgi kb" style="background-image:%s"></div><div class="tw"></div><div class="fade"></div><div style="position:absolute;left:16px;bottom:14px"><div class="kick" style="color:#9fe0d4">Specie e civiltà · Entità cosmiche</div><h1 class="h-serif" style="font-size:28px;margin:4px 0">Oltre i mondi</h1></div></div>
<div class="pad" style="padding-bottom:36px">
<div class="kick" style="color:#9fe0d4;margin-top:12px">Entità cosmiche</div>
<div class="rail" style="padding:8px 0">%s%s<div class="card" style="width:150px;height:200px;padding:14px;border-style:dashed"><b>Altre entità</b><div class="note" style="margin-top:6px">Alcune sono apparse sullo schermo, altre solo nei fumetti: il badge lo distingue.</div></div></div>
<div class="card" style="padding:12px;margin:8px 0 0;border-color:#4fa89e"><b>Perché Thanos non è qui</b><div class="note" style="margin-top:4px">Essere potente non basta: Thanos è un personaggio. Un record può avere più categorie quando le fonti lo giustificano.</div></div>
<div class="kick" style="color:#9fe0d4;margin-top:22px">Specie e civiltà</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px">%s%s%s%s</div></div>
'''%(I('entita_cosmiche'),
 '<div class="pt" style="width:150px;height:200px;background-image:%s;background-position:center;border-color:#d46aff"><span class="badge" style="position:absolute;left:10px;top:10px;color:#e9c6ff;z-index:3;background:rgba(10,8,5,.6)">CELESTIALE</span><div class="t"><b>Arishem</b><span>Sullo schermo · il Giudice</span></div></div>'%I('entita_cosmiche'),
 '<div class="pt" style="width:150px;height:200px;background-image:%s;background-position:left;border-color:#d46aff"><span class="badge" style="position:absolute;left:10px;top:10px;color:#e9c6ff;z-index:3;background:rgba(10,8,5,.6)">CELESTIALE</span><div class="t"><b>Ego</b><span>Sullo schermo · pianeta vivente</span></div></div>'%I('entita_cosmiche'),
 tile('Asgardiani','specie_civilta','10% 40%','Popolo di Asgard','#E3C79B',150),tile('Kree','specie_civilta','50% 30%','Impero guerriero','#4fa8ff',150),tile('Skrull','specie_civilta','92% 60%','Mutaforma','#6fd09a',150),tile('Chitauri','specie_civilta','60% 90%','Esercito invasore','#b48ae0',150))
