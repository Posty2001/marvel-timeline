# -*- coding: utf-8 -*-
I=lambda n:"url(img/%s.webp)"%n
ICON={
'back':'<svg class="ic" viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg>',
'search':'<svg class="ic" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4-4"/></svg>',
'mm':'<svg class="ic" viewBox="0 0 24 24"><circle cx="12" cy="13" r="7"/><path d="M12 9v4l3 2M9 3h6"/></svg>',
'app':'<svg class="ic" viewBox="0 0 24 24"><rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/></svg>',
'grid':'<svg class="ic" viewBox="0 0 24 24"><rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/></svg>',
'list':'<svg class="ic" viewBox="0 0 24 24"><path d="M5 7h14M5 12h14M5 17h14"/></svg>',
'star':'<svg class="ic" viewBox="0 0 24 24"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/></svg>',
'x':'<svg class="ic" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>',
'plus':'<svg class="ic" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
'minus':'<svg class="ic" viewBox="0 0 24 24"><path d="M5 12h14"/></svg>',
'lock':'<svg class="ic" viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/></svg>',
'check':'<svg class="ic" viewBox="0 0 24 24"><path d="M5 13l4 4 10-10"/></svg>',
}
def hdr(title,solid=False,kick='TVA ARCHIVES'):
    return ('<div class="hdr%s"><button class="rb">%s</button><div class="ttl"><small>%s</small><b>%s</b></div>'
            '<button class="rb">%s</button><button class="pillb">%s App Marvel</button></div>'
            '<div class="mmtab">%s</div>')%(' solid' if solid else '',ICON['back'],kick,title,ICON['search'],ICON['app'],ICON['mm'])
def frame(i,name,acc,body,note,extra='',solid=True,title=None,bgcss=''):
    return ('<section class="fr" id="f%d"><div class="sec"><h2>%02d · %s</h2><p>%s</p></div>'
            '<div class="phone" style="--acc:%s;%s">%s<div class="scr">%s</div><span class="demo">immagini dimostrative · non asset finali</span></div></section>')%(
            i,i,name,note,acc,bgcss,hdr(title or name,solid),body)

def f_home():
    return '''
<div class="hero" style="height:520px"><div class="bgi kb" style="background-image:%s;background-position:center 30%%"></div>
<div class="tw"></div><div class="fade"></div>
<div class="ring spin" style="width:250px;height:250px;left:70px;top:130px;border-style:dashed"></div>
<div class="ring" style="width:170px;height:170px;left:110px;top:170px;animation:pls 3s infinite"></div>
<div class="ring spin" style="width:330px;height:330px;left:30px;top:90px;opacity:.35;animation-direction:reverse"></div>
<div style="position:absolute;left:16px;right:16px;bottom:22px">
<div class="kick">Portale del Multiverso</div>
<h1 class="h-serif" style="font-size:36px;line-height:1.02;margin:6px 0 8px">Entra negli<br>Archivi della TVA</h1>
<p style="margin:0 0 14px;color:#e5d6b4;font-size:14px">Personaggi, universi, eventi e artefatti: ogni voce è un dossier collegato a tutte le altre.</p>
<div style="display:flex;gap:10px"><span class="btn fill">Apri il Multiverso</span><span class="btn">Cerca</span></div></div></div>
<div class="pad rev" style="margin-top:6px"><div class="card" style="display:flex;gap:12px;padding:12px;align-items:center;border-color:var(--acc)">
<div style="width:56px;height:56px;border-radius:14px;background:%s center/cover"></div>
<div style="flex:1;min-width:0"><div class="kick" style="font-size:9.5px">Riprendi l'esplorazione</div><b style="font-family:Spectral,serif;font-size:16px">Loki · Dossier</b><div class="note">Eri alla sezione «Relazioni»</div></div>
<div class="btn fill" style="height:38px;padding:0 14px">Riprendi</div></div></div>
<div class="pad rev" style="margin-top:20px"><div class="kick">Dossier in primo piano</div>
<div class="card" style="margin-top:8px;height:210px;background:%s center 20%%/cover;border-color:#6b4aa0">
<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(14,11,8,.92) 30%%,rgba(14,11,8,0) 80%%)"></div>
<div style="position:absolute;left:16px;top:16px;bottom:16px;width:58%%;display:flex;flex-direction:column;justify-content:flex-end">
<span class="badge" style="color:#c9a8f0;align-self:flex-start;margin-bottom:8px">VARIANTE · SACRA TIMELINE</span>
<b class="h-serif" style="font-size:26px">Loki</b><div class="note" style="margin:4px 0 10px">Dio dell'inganno, ospite del TVA, variante di sé stesso.</div>
<span class="btn" style="height:38px;align-self:flex-start;border-color:#c9a8f0;color:#c9a8f0">Apri dossier</span></div></div></div>
<div class="pad rev" style="margin-top:22px;display:flex;justify-content:space-between;align-items:end"><div><div class="kick">Esplora per categoria</div><h2 class="h-serif" style="font-size:20px;margin-top:2px">Le sale degli Archivi</h2></div></div>
<div class="rail rev" id="hrail">
<div class="pt" style="background-image:%s;--acc:#E3C79B"><div class="t"><b>Personaggi</b><span>Dossier e varianti</span></div></div>
<div class="pt" style="background-image:%s"><div class="t"><b>Universi</b><span>Mappa del Multiverso</span></div></div>
<div class="pt" style="background-image:%s"><div class="t"><b>Eventi</b><span>Saghe e battaglie</span></div></div>
<div class="pt" style="background-image:%s"><div class="t"><b>Artefatti</b><span>Reliquiario</span></div></div>
<div class="pt" style="background-image:%s"><div class="t"><b>Entità Cosmiche</b><span>Specie e civiltà</span></div></div>
<div class="pt" style="background-image:%s"><div class="t"><b>Nexus</b><span>Rete delle relazioni</span></div></div></div>
<div class="pad rev" style="margin:10px 0 28px"><div class="card" style="padding:14px;display:flex;gap:12px;align-items:center;border-color:#8a6a2a">
<div class="mmtab" style="position:static;border-radius:50%%;width:44px;height:44px;flex:none">%s</div>
<div style="flex:1"><b style="font-family:Spectral,serif">Chiedi a Miss Minutes</b><div class="note">Spiega un dossier, trova un legame, suggerisce dove andare.</div></div></div></div>
'''%(I('home_hero'),I('av_variante'),I('av_variante'),I('personaggi'),I('universi'),I('eventi'),I('artefatti'),I('entita_cosmiche'),I('relazioni'),ICON['mm'])

CH=[('Loki','av_variante','Variante','#b48ae0'),('Wanda Maximoff','av_mistico','Mistica','#d46aff'),('Doctor Strange','av_cronista','Cronista','#E3C79B'),('Tony Stark','av_tecnologico','Tecnologico','#4fd0ff'),('Steve Rogers','av_agente','Agente','#e6b25a'),('Sam Wilson','av_esploratore','Esploratore','#6fb3d9'),('Kang','av_astratto','Astratto','#f0a63a'),('Nick Fury','av_sentinella','Sentinella','#ff6a5c')]
def f_catalog():
    cards=''.join('<div class="pt ch" data-n="%s" style="width:auto;height:228px;background-image:%s;--acc:%s;border-color:%s66"><span class="badge" style="position:absolute;left:10px;top:10px;color:%s;z-index:3;background:rgba(10,8,5,.6)">%s</span><div class="t"><b>%s</b><span>%s</span></div></div>'%(n,I(a),c,c,c,r.upper(),n,'Apparizioni nel registro') for n,a,r,c in CH)
    rows=''.join('<div class="card lr" data-n="%s" style="display:flex;gap:12px;padding:10px;align-items:center;margin-bottom:8px"><div style="width:52px;height:52px;border-radius:12px;background:%s center top/cover;border:1px solid %s"></div><div style="flex:1"><b style="font-family:Spectral,serif;font-size:16px">%s</b><div class="note">%s</div></div><span class="dotc" style="background:%s"></span></div>'%(n,I(a),c,n,r,c) for n,a,r,c in CH)
    return '''
<div style="height:150px;position:relative;margin-top:0"><div class="bgi" style="background-image:%s;background-position:center 40%%;opacity:.7"></div><div class="fade"></div>
<div style="position:absolute;left:16px;bottom:10px"><div class="kick">Sala dei Personaggi</div><h1 class="h-serif" style="font-size:28px;margin:2px 0">Catalogo</h1></div></div>
<div class="chips" style="margin:10px 0 4px"><span class="chip on">Tutti</span><span class="chip"><i class="dotc" style="background:#b48ae0"></i>Varianti</span><span class="chip"><i class="dotc" style="background:#4fd0ff"></i>Eroi</span><span class="chip"><i class="dotc" style="background:#ff6a5c"></i>Antagonisti</span><span class="chip">Mistici</span></div>
<div class="seg" id="vseg" style="margin:10px 16px"><button class="on" data-v="g">%s Griglia illustrata</button><button data-v="l">%s Elenco</button></div>
<div class="pad" id="vg" style="display:grid;grid-template-columns:1fr 1fr;gap:12px;padding-bottom:30px">%s</div>
<div class="pad" id="vl" style="display:none;padding-bottom:30px">%s</div>
<div class="pad note" style="padding-bottom:30px">Ritratti dimostrativi: nell'app finale ogni scheda usa il ritratto autorizzato o resta un segnaposto dichiarato.</div>
'''%(I('personaggi'),ICON['grid'],ICON['list'],cards,rows)

def f_dossier():
    return '''
<div class="hero" style="height:470px"><div class="bgi" id="dparx" style="background-image:%s;background-position:center 20%%;filter:saturate(1.15)"></div><div class="tw"></div><div class="fade"></div>
<div style="position:absolute;left:16px;right:16px;bottom:18px"><span class="badge" style="color:#c9a8f0">VARIANTE · SACRA TIMELINE</span>
<h1 class="h-serif" style="font-size:44px;margin:8px 0 2px;text-shadow:0 2px 20px #000">Loki</h1><div style="color:#e5d6b4;font-size:14px">Dio dell'inganno · Principe di Asgard</div>
<div style="display:flex;gap:8px;margin-top:12px"><span class="btn fill" style="height:40px;padding:0 14px">%s Preferito</span><span class="btn" style="height:40px;padding:0 14px">Confronta</span><span class="btn" style="height:40px;padding:0 14px">Nexus</span></div></div></div>
<div class="chips" id="dtabs" style="position:sticky;top:62px;z-index:20;background:linear-gradient(var(--ink) 70%%,transparent);padding:10px 16px 12px">
<span class="chip on" data-s="s1">Biografia</span><span class="chip" data-s="s2">Poteri</span><span class="chip" data-s="s3">Apparizioni</span><span class="chip" data-s="s4">Relazioni</span><span class="chip" data-s="s5">Bozza da validare</span></div>
<div class="pad" style="padding-bottom:40px">
<div id="s1" class="rev"><div class="kick">Biografia · Origini</div><p style="font-family:Spectral,serif;font-size:17px;line-height:1.5;margin:8px 0">Nato Jotun e cresciuto da Odino come principe di Asgard, Loki vive all'ombra del fratello Thor e sceglie la via dell'inganno. Prelevato dalla TVA, scopre le proprie linee temporali.</p><div class="note">Testo editoriale originale · fonte: schede del registro</div></div>
<div id="s2" class="rev" style="margin-top:24px"><div class="kick">Poteri e abilità</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
<div class="card" style="padding:12px"><b>Illusioni</b><div class="note">Proiezioni e inganni</div></div><div class="card" style="padding:12px"><b>Magia asgardiana</b><div class="note">Incantesimi e teletrasporto</div></div>
<div class="card" style="padding:12px"><b>Metamorfosi</b><div class="note">Cambia aspetto</div></div><div class="card" style="padding:12px"><b>Combattimento</b><div class="note">Pugnali, tattica</div></div></div></div>
<div id="s3" class="rev" style="margin-top:24px"><div class="kick">Apparizioni · dal registro</div>
<div style="position:relative;margin:12px 0 0 8px;padding-left:20px;border-left:2px solid #6b4aa0">
%s</div></div>
<div id="s4" class="rev" style="margin-top:24px"><div class="kick">Relazioni narrative</div>
<div style="display:flex;gap:10px;margin-top:10px;overflow-x:auto" class="rail" >
<div class="card" style="width:140px;padding:12px;border-color:#e0707a"><span class="badge" style="color:#e0707a">FAMIGLIA</span><br><b style="font-family:Spectral,serif;font-size:17px;line-height:2">Thor</b><div class="note">Fratello</div></div>
<div class="card" style="width:140px;padding:12px;border-color:#e0707a"><span class="badge" style="color:#e0707a">FAMIGLIA</span><br><b style="font-family:Spectral,serif;font-size:17px;line-height:2">Odino</b><div class="note">Padre adottivo</div></div>
<div class="card" style="width:140px;padding:12px;border-color:#e0707a"><span class="badge" style="color:#e0707a">FAMIGLIA</span><br><b style="font-family:Spectral,serif;font-size:17px;line-height:2">Laufey</b><div class="note">Padre biologico</div></div></div></div>
<div id="s5" class="rev" style="margin-top:24px"><div class="kick">Debolezze · Trasformazioni</div><div class="card" style="padding:12px;margin-top:8px;border-style:dashed"><span class="badge" style="color:#f0a63a">BOZZA DA VALIDARE</span><div class="note" style="margin-top:8px">Sezioni previste dalla scheda estesa: vengono mostrate solo quando i dati sono verificati. Nessun valore numerico o dato inventato.</div></div></div>
<div class="note" style="margin-top:22px">Esplorazione del dossier: <b id="dprog" style="color:var(--acc)">1/3</b> sezioni consultate</div>
</div>'''%(I('av_variante'),ICON['star'],''.join('<div style="margin-bottom:14px;position:relative"><i style="position:absolute;left:-27px;top:5px;width:12px;height:12px;border-radius:50%%;background:#b48ae0;box-shadow:0 0 10px #b48ae0"></i><b>%s</b><div class="note">%s</div></div>'%(a,b) for a,b in [('N°050 · Thor','prima apparizione · 2011'),('N°051 · The Avengers','2012'),('N°055 · Thor: The Dark World','2013'),('N°076 · Thor: Ragnarok','2017'),('N°095 · Loki · stagione 1','2021'),('N°112 · Loki · stagione 2','ultima apparizione · 2023')]))

