#!/usr/bin/env python3
"""Atlante 2.0 - A2: normalizzazione delle identita' (livello registro, NON interfaccia).

Uso:  python3 tools/atlante_identita.py --scrivi | --verifica
Produce data/atlante/identita.json (strato aggiuntivo) a partire da data/atlante/*.json (estratti in A1).
Non modifica index.html, personaggi.json, i blob, la Tessera, gli XP, i preferiti. Nessun id viene rimosso: ogni pagina
`char-*` resta valida e viene mappata in `redirect` (ruolo: canonica | alias | pagina-hub | pagina-storica | sospesa).
Modello: docs/ATLANTE_2_0_MODELLO_IDENTITA.md; decisioni: docs/ATLANTE_2_0_DECISIONI_IDENTITA.md (Esito).
"""
import json, os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'atlante')
OUT = os.path.join(D, 'identita.json')
def jl(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
PERS = {e['id']: e for e in jl('personaggi.json')['voci']}
ATLAS = json.load(open(os.path.join(D, 'blob', 'atlasData.json'), encoding='utf-8'))
MV = json.load(open(os.path.join(D, 'blob', 'mvMapData.json'), encoding='utf-8'))['universi']
GRAFO = json.load(open(os.path.join(D, 'blob', 'relationshipGraphData.json'), encoding='utf-8'))
CONTA = {p['id']: p['conta'] for p in ATLAS['personaggi']}
APPART = {p['id']: p['appartenenza'] for p in ATLAS['personaggi']}

def apps(pid):
    """N° delle apparizioni dichiarate dalla scheda (PRIMA/ULTIMA/ALTRE), ordinate, senza duplicati."""
    s = set()
    for c in PERS[pid]['campi']:
        if c['k'] in ('PRIMA APP.', 'ULTIMA APP.', 'ALTRE APP.'):
            s.update(re.findall(r'N°(\d{3})', c['testo']))
    return sorted(s)
def titoli(uni): return set(MV[uni]['titoliIds'])

# ---- FONTI (consultate il 25/11/2026; testi NON copiati: servono a stabilire i fatti) ----
F = {
 'int-identita': 'atlasData.identita (guida, livello identita\' gia\' verificato) + schede del registro',
 'int-mv': 'mvMapData (titoliIds per universo)',
 'w-coulson': 'https://en.wikipedia.org/wiki/Phil_Coulson',
 'mc-lmd': 'https://marvel.com/articles/tv-shows/ydk-agents-of-shield-and-lmds',
 'w-ross': 'https://en.wikipedia.org/wiki/Thaddeus_Ross_(Marvel_Cinematic_Universe)',
 'w-mj-raimi': 'https://en.wikipedia.org/wiki/Mary_Jane_Watson_(2002_film_series_character)',
 'w-mj-mcu': 'https://en.wikipedia.org/wiki/MJ_(Marvel_Cinematic_Universe)',
 'w-xavier': 'https://en.wikipedia.org/wiki/Charles_Xavier_(film_character)',
 'w-xavier-altri': 'https://www.wikipedia.com/wiki/Professor_X_in_other_media',
 'w-fisk': 'https://en.wikipedia.org/wiki/Kingpin_(character)',
 'w-murdock-mcu': 'https://en.wikipedia.org/wiki/Matt_Murdock_(Marvel_Cinematic_Universe)',
 'w-daredevil-film': 'https://en.wikipedia.org/wiki/Daredevil_(film)',
 'sy-fisk': 'https://www.syfy.com/syfy-wire/hawkeye-and-daredevil-same-kingpin',
 'g-groot': 'https://www.gamesradar.com/uk/guardians-of-the-galaxy-2s-baby-groot-isnt-the-original-groot-but-a-new-groot-confused-so-are-groot ; https://gameinformer.com/b/news/archive/2018/02/27/guardians-of-the-galaxy-director-confirms-baby-groot-is-groots-son-again.aspx',
 'w-ravonna': 'https://www.denofgeek.com/tv/loki-season-2-who-is-ravonna-renslayer-and-whats-her-relationship-with-kang/',
 'gr-ghost': 'https://www.rollingstone.com/tv-movies/tv-movie-news/marvel-ryan-gosling-ghost-rider-david-jonsson-black-panther-1235598892/',
}
VER = 'verificata (fonti secondarie affidabili + dati interni; pagine Marvel.com/Marvel Database non consultate una per una)'
def ident(id, nome, tipo, uni, pagine, principale, interpreti=None, fonte=(), verifica=VER, conta=True, apparizioni=None, note='', incarnazioni=None, extra=None):
    d = {'id': id, 'nome': nome, 'tipo': tipo, 'categorie': ['personaggio'], 'conta_come_personaggio': conta, 'universo': uni,
         'pagine': pagine, 'pagina_principale': principale, 'interpreti': interpreti or [],
         'apparizioni': apparizioni if apparizioni is not None else sorted(set(sum([apps(p) for p in pagine], []))),
         'incarnazioni': incarnazioni or [], 'alias': sorted({PERS[p]['nome'] for p in pagine if p in PERS} - {nome}),
         'fonte': [F[x] for x in fonte], 'verifica': verifica, 'nota': note}
    if extra: d.update(extra)
    return d

def costruisci():
    I = []; HUB = []; MAN = []; SEG = []; REL = []; RED = {}; SOSP = []; APERTE = []
    def rel(da, a, tipo, inv, narr, fonte, ver, nota=''):
        REL.append({'da': da, 'a': a, 'tipo': tipo, 'inverso': inv, 'narrativa': narr, 'fonte': [F[x] for x in fonte], 'verifica': ver, 'nota': nota})
    def red(page, ruolo, target, nota=''):
        RED[page] = {'ruolo': ruolo, 'verso': target if isinstance(target, list) else [target], 'nota': nota}
    ap = lambda page, uni: sorted(set(apps(page)) & titoli(uni))
    # 1 Peter Parker: hub ----------------------------------------------------------------
    pp = 'char-peter-parker'
    pm = ident('id-peter-parker-mcu', 'Peter Parker (MCU)', 'identita', 'uni-earth-199999-mcu', ['char-peter-parker', 'char-peter-parker-holland-maguire-garfield', 'char-spider-man'], 'char-peter-parker', ['Tom Holland'], ['int-identita', 'int-mv'],
               apparizioni=ap(pp, 'uni-earth-199999-mcu'), note="Solo le apparizioni MCU della pagina multi-continuita'; char-spider-man e' redirect gia' dichiarato in atlasData (prima apparizione nel ruolo MCU = N°067).")
    pr = ident('id-peter-parker-raimi', 'Peter Parker (Raimi-Verse)', 'identita', 'uni-earth-96283-raimi-verse', [pp, 'char-peter-parker-holland-maguire-garfield'], pp, ['Tobey Maguire'], ['int-identita', 'int-mv'], apparizioni=ap(pp, 'uni-earth-96283-raimi-verse'), note="N°099: ricompare nel MCU come variante (naturaNota dell'universo).")
    pg = ident('id-peter-parker-garfield', 'Peter Parker (Garfield-Verse)', 'identita', 'uni-earth-120703-garfield-verse', [pp, 'char-peter-parker-holland-maguire-garfield'], pp, ['Andrew Garfield'], ['int-identita', 'int-mv'], apparizioni=ap(pp, 'uni-earth-120703-garfield-verse'))
    py = ident('id-peter-parker-ynfsm', 'Peter Parker (Your Friendly Neighborhood Spider-Man)', 'identita', 'uni-your-friendly-neighborhood-spider-man-verse', [pp], pp, [], ['int-identita', 'int-mv'], apparizioni=ap(pp, 'uni-your-friendly-neighborhood-spider-man-verse'), note="Interprete/voce non registrato nelle schede: non inserito.")
    pb = ident('id-peter-b-parker', 'Peter B. Parker', 'variante_multiversale', 'uni-spider-verse-sony-animato', ['char-peter-b-parker'], 'char-peter-b-parker', [], ['int-mv'], note="Variante animata (Spider-Verse), non unificata con alcun Parker live-action. Anche il campo UNIVERSI della scheda lo dichiara non canonico MCU.")
    I += [pm, pr, pg, py, pb]
    SEG.append({'id': 'seg-peter-parker-616', 'nome': 'Peter Parker (Terra-616, fumetti)', 'categorie': ['personaggio'], 'conta_come_personaggio': False, 'universo': None, 'pagine': [], 'verifica': 'segnaposto: nessuna scheda e nessun dato verificato; da compilare solo da fonti autorizzate', 'nota': "Previsto dall'utente (decisione 1). Non conta come personaggio finche' non ha dati."})
    HUB.append({'id': 'hub-peter-parker', 'nome': 'Peter Parker / Spider-Man', 'tipo': 'hub_multiversale', 'conta_come_personaggio': False,
                'membri': ['seg-peter-parker-616', 'id-peter-parker-mcu', 'id-peter-parker-raimi', 'id-peter-parker-garfield', 'id-peter-parker-ynfsm', 'id-peter-b-parker'],
                'esclusi': {'char-peter': "Peter (franchise Deadpool): altro personaggio, creato per il film Deadpool 2 (2018)", 'char-peter-quill-star-lord': 'Peter Quill: altro personaggio (omonimia del nome di battesimo)'},
                'pagine_hub': [pp, 'char-peter-parker-holland-maguire-garfield'], 'nota': 'L\'hub elenca identita\' autonome (biografia, poteri, apparizioni, relazioni e continuita\' propri); non ha biografia propria.', 'fonte': [F['int-identita']], 'verifica': VER})
    red(pp, 'pagina-hub', ['hub-peter-parker', 'id-peter-parker-mcu', 'id-peter-parker-raimi', 'id-peter-parker-garfield', 'id-peter-parker-ynfsm'], 'pagina multi-continuita\': i link entranti vanno classificati per continuita\' (vedi collegamenti_da_classificare)')
    red('char-peter-parker-holland-maguire-garfield', 'pagina-hub', ['hub-peter-parker', 'id-peter-parker-mcu', 'id-peter-parker-raimi', 'id-peter-parker-garfield'], 'pagina aggregata (No Way Home)')
    red('char-spider-man', 'alias', 'id-peter-parker-mcu', 'redirect gia\' dichiarato in atlasData.identita')
    red('char-peter-b-parker', 'canonica', 'id-peter-b-parker')
    for pid, why in (('char-peter', 'Peter (franchise Deadpool)'), ('char-peter-quill-star-lord', 'Peter Quill')): red(pid, 'canonica', 'id-' + pid[5:], why + ': identita\' distinta, fuori dall\'hub')
    I.append(ident('id-peter', 'Peter (franchise Deadpool)', 'identita', None, ['char-peter'], 'char-peter', [], ['int-mv'], note="Personaggio creato per il film Deadpool 2 (2018), senza controparte nei fumetti (campo NEI FUMETTI della scheda). Alias di visualizzazione: «Peter (Deadpool)»."))
    I.append(ident('id-peter-quill-star-lord', 'Peter Quill/Star-Lord', 'identita', 'uni-earth-199999-mcu', ['char-peter-quill-star-lord'], 'char-peter-quill-star-lord', [], ['int-mv']))
    # 2 Charles Xavier --------------------------------------------------------------------
    cx = ['char-charles-xavier', 'char-xavier', 'char-xavier-giovane-e-anziano']
    all_x = sorted(set(sum([apps(p) for p in cx], [])))
    I.append(ident('id-charles-xavier-fox', 'Charles Xavier (Fox-Verse)', 'identita', 'uni-earth-10005-fox-verse', cx, 'char-charles-xavier', ['James McAvoy', 'Patrick Stewart'], ['int-identita', 'w-xavier', 'w-xavier-altri'],
        apparizioni=all_x, incarnazioni=[
          {'id': 'inc-xavier-giovane', 'etichetta': 'giovane', 'interprete': 'James McAvoy', 'apparizioni': ['012', '018', '019', '020'], 'tipo': 'incarnazione', 'fonte': [F['w-xavier-altri']]},
          {'id': 'inc-xavier-anziano', 'etichetta': 'anziano', 'interprete': 'Patrick Stewart', 'apparizioni': ['014', '015', '016', '018', '023'], 'tipo': 'incarnazione', 'fonte': [F['w-xavier-altri']]}],
        note="Giovane e anziano nella stessa identita' perche' Days of Future Past (N°018) li mostra come lo stesso individuo in due fasi della vita. Cambio di interprete = incarnazione, non variante. APERTO: l'ordine delle timeline prima/dopo DOFP non e' verificato (naturaNota Fox-Verse: «non una linea unica e continua»)."))
    for p in cx: red(p, 'canonica' if p == 'char-charles-xavier' else 'alias', 'id-charles-xavier-fox')
    I.append(ident('id-professor-x-terra-838', 'Professor X (Terra-838)', 'variante_multiversale', 'uni-earth-838', ['char-professor-x-terra-838'], 'char-professor-x-terra-838', ['Patrick Stewart'], ['w-xavier'], verifica='da verificare: le fonti lo dicono «variante di Charles Xavier» senza indicare di quale identita\''))
    red('char-professor-x-terra-838', 'canonica', 'id-professor-x-terra-838')
    rel('id-professor-x-terra-838', 'id-charles-xavier-fox', 'controparte_altra_continuita', 'controparte_altra_continuita', True, ['w-xavier'], 'da verificare', "NON e' una relazione di identita'; non si afferma che sia variante proprio dell'Xavier Fox.")
    # 3 Coulson ----------------------------------------------------------------------------
    I.append(ident('id-phil-coulson', 'Phil Coulson', 'identita', 'uni-earth-199999-mcu', ['char-phil-coulson', 'char-coulson'], 'char-phil-coulson', ['Clark Gregg'], ['w-coulson', 'int-mv'],
        note="Stesso personaggio (Clark Gregg) dai One-Shot ad Agents of S.H.I.E.L.D. APERTO: N°091 su char-coulson (S6, dopo la morte di Coulson) puo' riferirsi a Sarge/LMD/flashback; apparizione conservata e segnata «da verificare»."))
    I[-1]['apparizioni_da_verificare'] = ['091']
    I.append(ident('id-coulson-lmd', 'Coulson (LMD)', 'copia_artificiale', 'uni-earth-199999-mcu', ['char-coulson-lmd'], 'char-coulson-lmd', ['Clark Gregg'], ['w-coulson', 'mc-lmd'], note="Life Model Decoy creato dalla copia della coscienza di Coulson: personaggio con narrazione propria, distinguibile dall'originale."))
    red('char-phil-coulson', 'canonica', 'id-phil-coulson'); red('char-coulson', 'alias', 'id-phil-coulson'); red('char-coulson-lmd', 'canonica', 'id-coulson-lmd')
    rel('id-coulson-lmd', 'id-phil-coulson', 'copia_di', 'originale_di', True, ['w-coulson', 'mc-lmd'], VER)
    # 4 Groot ---------------------------------------------------------------------------
    gp = apps('char-groot')
    I.append(ident('id-groot-originale', 'Groot (originale)', 'identita', 'uni-earth-199999-mcu', ['char-groot'], 'char-groot', ['Vin Diesel'] if False else [], ['g-groot'], apparizioni=['058'], verifica="dichiarazione d'autore (James Gunn); non esplicito nei film", note="Muore in Guardians of the Galaxy (N°058). Pagina storica char-groot mescola entrambi."))
    I.append(ident('id-groot-successore', 'Groot (successore)', 'identita', 'uni-earth-199999-mcu', ['char-groot', 'char-groot-piccolo'], 'char-groot-piccolo', [], ['g-groot'], apparizioni=sorted(set(gp) - {'058'} | set(apps('char-groot-piccolo'))), verifica="dichiarazione d'autore (James Gunn): non e' il Groot originale ma un personaggio senza i suoi ricordi, definito «figlio»",
        incarnazioni=[{'id': 'inc-groot-piccolo', 'etichetta': 'piccolo', 'pagina': 'char-groot-piccolo', 'apparizioni': apps('char-groot-piccolo'), 'tipo': 'incarnazione', 'verifica': 'da verificare: etichetta presa dalla scheda'}]))
    red('char-groot', 'pagina-storica', ['id-groot-originale', 'id-groot-successore'], 'apparizioni separate: 058 originale; 059, 084, 089, 115 successore'); red('char-groot-piccolo', 'canonica', 'id-groot-successore', 'incarnazione piccolo')
    rel('id-groot-successore', 'id-groot-originale', 'discendente_di', 'antenato_di', True, ['g-groot'], "dichiarazione d'autore", 'relazione familiare (figlio) dichiarata dal regista, non esplicita nei film')
    # 5 Capitan America: mantello ---------------------------------------------------------
    for pid in ('char-steve-rogers-capitan-america', 'char-sam-wilson-capitan-america'):
        I.append(ident('id-' + pid[5:], PERS[pid]['nome'], 'identita', 'uni-earth-199999-mcu', [pid], pid, [], ['int-mv'])); red(pid, 'canonica', 'id-' + pid[5:])
    MAN.append({'id': 'man-capitan-america', 'nome': 'Capitan America', 'tipo': 'mantello', 'conta_come_personaggio': False, 'universo': 'uni-earth-199999-mcu',
                'titolari': [{'ordine': 1, 'identita': 'id-steve-rogers-capitan-america'}, {'ordine': 2, 'identita': 'id-sam-wilson-capitan-america'}], 'fonte': [F['int-mv']], 'verifica': 'verificata (schede interne: Sam Wilson compare in N°094 The Falcon and the Winter Soldier e N°121 Brave New World)',
                'nota': "Altri titolari del mantello nell'MCU non sono registrati: non aggiunti. Nessuna unione tra Steve e Sam."})
    rel('id-sam-wilson-capitan-america', 'id-steve-rogers-capitan-america', 'erede_del_mantello', 'cede_il_mantello_a', True, ['int-mv'], 'verificata (interna)')
    # 6 Ross ---------------------------------------------------------------------------------
    I.append(ident('id-thaddeus-ross-mcu', 'Thaddeus Ross (MCU)', 'identita', 'uni-earth-199999-mcu', ['char-thaddeus-ross', 'char-generale-ross'], 'char-thaddeus-ross', ['William Hurt', 'Harrison Ford'], ['w-ross'],
        incarnazioni=[{'id': 'inc-ross-hurt', 'etichetta': 'interprete William Hurt', 'tipo': 'cambio_attore', 'apparizioni': apps('char-generale-ross')}, {'id': 'inc-ross-ford', 'etichetta': 'interprete Harrison Ford', 'tipo': 'cambio_attore', 'apparizioni': apps('char-thaddeus-ross')}],
        note="Cambio di attore (Hurt → Ford dopo la morte di Hurt, 2022): stesso personaggio, NON variante."))
    I.append(ident('id-ross-hulk-2003', 'Thaddeus Ross (Hulk 2003)', 'identita', 'uni-hulk-2003-verse', ['char-generale-thaddeus-ross'], 'char-generale-thaddeus-ross', ['Sam Elliott'], ['w-ross'], note="Altra continuita' (film Hulk 2003, non MCU): identita' distinta."))
    I.append(ident('id-everett-ross', 'Everett Ross', 'identita', 'uni-earth-199999-mcu', ['char-everett-ross'], 'char-everett-ross', [], ['int-mv']))
    red('char-thaddeus-ross', 'canonica', 'id-thaddeus-ross-mcu'); red('char-generale-ross', 'alias', 'id-thaddeus-ross-mcu'); red('char-generale-thaddeus-ross', 'canonica', 'id-ross-hulk-2003'); red('char-everett-ross', 'canonica', 'id-everett-ross')
    rel('id-ross-hulk-2003', 'id-thaddeus-ross-mcu', 'controparte_altra_continuita', 'controparte_altra_continuita', True, ['w-ross'], VER)
    # 7 Ghost / Ghost Rider ------------------------------------------------------------
    for pid in ('char-ghost', 'char-johnny-blaze-ghost-rider', 'char-robbie-reyes-ghost-rider'):
        I.append(ident('id-' + pid[5:], PERS[pid]['nome'], 'identita', (APPART[pid] or [None])[0], [pid], pid, [], ['int-mv'])); red(pid, 'canonica', 'id-' + pid[5:])
    MAN.append({'id': 'man-ghost-rider', 'nome': 'Ghost Rider (Spirito della Vendetta)', 'tipo': 'mantello', 'conta_come_personaggio': False, 'universo': None,
                'titolari': [{'identita': 'id-johnny-blaze-ghost-rider', 'continuita': 'uni-ghost-rider-verse'}, {'identita': 'id-robbie-reyes-ghost-rider', 'continuita': 'uni-earth-199999-mcu'}],
                'ordine': 'per continuita\', non cronologico', 'fonte': [F['gr-ghost']], 'verifica': VER, 'nota': 'Ghost (Ava Starr) non e\' collegata: nome in comune, nessun legame (Ant-Man and the Wasp).'})
    # 8 Mary Jane ---------------------------------------------------------------------
    I.append(ident('id-mary-jane-watson-raimi', 'Mary Jane Watson (Raimi-Verse)', 'identita', 'uni-earth-96283-raimi-verse', ['char-mary-jane-watson', 'char-mary-jane'], 'char-mary-jane-watson', ['Kirsten Dunst'], ['w-mj-raimi', 'int-mv']))
    I.append(ident('id-michelle-jones-watson-mcu', 'MJ (Michelle Jones-Watson, MCU)', 'identita', 'uni-earth-199999-mcu', ['char-mj'], 'char-mj', ['Zendaya'], ['w-mj-mcu'], note="Personaggio originale dell'MCU, non Mary Jane Watson (fonte: nome completo Michelle Jones-Watson; interprete: «100% Michelle»)."))
    red('char-mary-jane-watson', 'canonica', 'id-mary-jane-watson-raimi'); red('char-mary-jane', 'alias', 'id-mary-jane-watson-raimi'); red('char-mj', 'canonica', 'id-michelle-jones-watson-mcu')
    rel('id-michelle-jones-watson-mcu', 'id-mary-jane-watson-raimi', 'ispirato_a', 'ispirazione_di', False, ['w-mj-mcu'], VER, 'relazione editoriale (omaggio), NON narrativa e NON di identita\'')
    # 9 e 10 sospesi --------------------------------------------------------------------
    for pid in ('char-bishop', 'char-kate-bishop', 'char-janet', 'char-janet-van-dyne'):
        I.append(ident('id-' + pid[5:], PERS[pid]['nome'], 'identita', (APPART[pid] or [None])[0], [pid], pid, [], ['int-mv'], verifica='sospesa (decisioni 9/10 rimandate dall\'utente)', extra={'sospesa': True})); red(pid, 'sospesa', 'id-' + pid[5:], 'nessuna modifica: in attesa di verifica documentata')
        SOSP.append(pid)
    # 11 Wilson Fisk: hub --------------------------------------------------------------
    fk = 'char-wilson-fisk-kingpin'
    I.append(ident('id-fisk-fox-2003', 'Wilson Fisk (Daredevil 2003)', 'identita', 'uni-daredevil-elektra-verse', [fk], fk, ['Michael Clarke Duncan'], ['w-fisk', 'int-mv'], apparizioni=ap(fk, 'uni-daredevil-elektra-verse')))
    I.append(ident('id-fisk-mcu', 'Wilson Fisk (MCU, ex Netflix)', 'identita', 'uni-earth-199999-mcu', [fk], fk, ["Vincent D'Onofrio"], ['w-fisk', 'sy-fisk', 'int-mv'], apparizioni=sorted(set(apps(fk)) - set(ap(fk, 'uni-daredevil-elektra-verse'))),
        note="Stesso individuo nelle serie Netflix (Daredevil) e in Hawkeye/Echo/Born Again (dichiarazione dell'interprete: «no multiverse»): un'unica identita'. Il campo UNIVERSI della scheda distingue «MCU (Netflix)» e «MCU»: la scheda resta invariata."))
    I.append(ident('id-kingpin-spider-verse', 'Kingpin (Spider-Verse)', 'variante_multiversale', 'uni-spider-verse-sony-animato', ['char-kingpin'], 'char-kingpin', ['Liev Schreiber'], ['w-fisk', 'int-mv'], note='Versione animata Sony, non canonica MCU; identita\' autonoma dell\'hub.'))
    SEG.append({'id': 'seg-wilson-fisk-616', 'nome': 'Wilson Fisk (Terra-616, fumetti)', 'categorie': ['personaggio'], 'conta_come_personaggio': False, 'universo': None, 'pagine': [], 'verifica': 'segnaposto: nessun dato verificato', 'nota': 'Non mescolare fumetti, MCU, animazione e altre versioni (decisione 11).'})
    HUB.append({'id': 'hub-wilson-fisk', 'nome': 'Wilson Fisk / Kingpin', 'tipo': 'hub_multiversale', 'conta_come_personaggio': False, 'membri': ['seg-wilson-fisk-616', 'id-fisk-fox-2003', 'id-fisk-mcu', 'id-kingpin-spider-verse'], 'esclusi': {}, 'pagine_hub': [fk], 'nota': 'Una identita\' per continuita\'; nessun testo mescolato.', 'fonte': [F['w-fisk']], 'verifica': VER})
    red(fk, 'pagina-hub', ['hub-wilson-fisk', 'id-fisk-fox-2003', 'id-fisk-mcu']); red('char-kingpin', 'canonica', 'id-kingpin-spider-verse')
    # 12 Miles Morales ----------------------------------------------------------------
    I.append(ident('id-miles-morales', 'Miles Morales', 'identita', 'uni-spider-verse-sony-animato', ['char-miles-morales'], 'char-miles-morales', [], ['int-mv'])); red('char-miles-morales', 'canonica', 'id-miles-morales')
    SEG.append({'id': 'seg-miles-morales-e-altri', 'nome': 'Miles Morales e altri (Beyond the Spider-Verse)', 'categorie': ['personaggio'], 'conta_come_personaggio': False, 'universo': 'uni-spider-verse-sony-animato', 'pagine': ['char-miles-morales-e-altri'], 'verifica': 'segnaposto: voce aggregata di film senza correlati ne\' apparizioni verificate', 'nota': 'Cast del film da verificare (Marvel.com/TMDB) prima di creare identita\'. Non conta come personaggio.'})
    red('char-miles-morales-e-altri', 'segnaposto', 'seg-miles-morales-e-altri', 'non conteggiato'); rel('seg-miles-morales-e-altri', 'id-miles-morales', 'segnaposto_collegato_a', 'ha_segnaposto', False, ['int-mv'], 'da verificare')
    # 13 Ravonna ------------------------------------------------------------------------
    I.append(ident('id-ravonna-renslayer', 'Ravonna Renslayer', 'identita', 'uni-tva-fuori-dal-tempo', ['char-ravonna-renslayer', 'char-renslayer'], 'char-ravonna-renslayer', ['Gugu Mbatha-Raw'], ['w-ravonna', 'int-mv'], note="Stessa persona (stessa interprete) in Loki S1 e S2; nella S2 e' chiamata «Renslayer»."))
    red('char-ravonna-renslayer', 'canonica', 'id-ravonna-renslayer'); red('char-renslayer', 'alias', 'id-ravonna-renslayer')
    # ---- tutte le altre pagine: identita' individuale invariata (1 pagina = 1 identita') ----
    for pid, e in PERS.items():
        if pid in RED: continue
        if not CONTA[pid]:
            SEG.append({'id': 'seg-' + pid[5:], 'nome': e['nome'], 'categorie': ['personaggio'], 'conta_come_personaggio': False, 'universo': None, 'pagine': [pid], 'verifica': 'segnaposto gia\' escluso dai conteggi (atlasData)', 'nota': ''})
            red(pid, 'segnaposto', 'seg-' + pid[5:]); continue
        I.append({'id': 'id-' + pid[5:], 'nome': e['nome'], 'tipo': 'identita', 'categorie': ['personaggio'], 'conta_come_personaggio': True, 'universo': (APPART[pid] or [None])[0], 'pagine': [pid], 'pagina_principale': pid, 'interpreti': [], 'apparizioni': apps(pid), 'incarnazioni': [], 'alias': [], 'fonte': [F['int-identita']], 'verifica': 'invariata (nessuna decisione di identita\' applicata)', 'nota': ''})
        red(pid, 'canonica', 'id-' + pid[5:])
    # 14 Wolverine: Fox-Verse e X-Men '97 (decisione dell'utente, 25/11/2026) --------------------------------------------
    # La scheda char-wolverine dichiara «Fox-Verse · Animato, continuita' propria»; N°131 (X-Men '97 S2) e' in uni-x-men-97-verse (mvMapData).
    # Nessun ID, apparizione o collegamento va perso: id-wolverine resta (stesso ID, stessa pagina canonica); N°131 passa all'identita' animata
    # e resta tracciato in id-wolverine.apparizioni_spostate. La pagina char-wolverine resta canonica verso id-wolverine (i link entranti non cambiano).
    wv = next(i for i in I if i['id'] == 'id-wolverine'); assert '131' in wv['apparizioni'] and '131' in titoli('uni-x-men-97-verse')
    wv['apparizioni'] = [n for n in wv['apparizioni'] if n != '131']; wv['apparizioni_spostate'] = {'131': 'id-wolverine-x-men-97'}
    wv['nota'] = "N°131 (X-Men '97 S2) appartiene alla continuita' animata: spostato in id-wolverine-x-men-97 (decisione dell'utente 25/11/2026)."
    I.append(ident('id-wolverine-x-men-97', "Logan/Wolverine (X-Men '97)", 'identita', 'uni-x-men-97-verse', ['char-wolverine'], 'char-wolverine', [], ['int-identita', 'int-mv'], apparizioni=['131'],
                   verifica="parziale: continuita' dichiarata dalla scheda Atlante (Fox-Verse · Animato, continuita' propria) e da mvMapData (N°131 in uni-x-men-97-verse); nessun dato biografico specifico attribuito",
                   note="Separato da id-wolverine (Fox-Verse) per decisione dell'utente (25/11/2026). La scheda char-wolverine descrive insieme le due continuita': i suoi campi restano attribuiti a id-wolverine e non a questa identita'."))
    rel('id-wolverine', 'id-wolverine-x-men-97', 'stessa_scheda_atlante', 'stessa_scheda_atlante', False, ['int-identita', 'int-mv'], "dati interni: la scheda char-wolverine copre entrambe le continuita'; nessuna parentela narrativa dichiarata", "Continuita' distinte (Fox-Verse / X-Men '97-verse): identita' distinte, non unificate.")
    # 15 Harry Osborn: Raimi-Verse e Webb (Garfield-Verse) in due identita' autonome (decisione dell'utente, 25/11/2026) ------------------
    # Stesso schema di Wolverine: nessun ID, apparizione o collegamento va perso. id-harry-osborn-green-goblin resta (stesso ID, stessa pagina canonica,
    # ritratti e preferiti invariati) e diventa «Raimi»; N°005 (The Amazing Spider-Man 2, Earth-120703) passa a id-harry-osborn-webb e resta tracciato in
    # apparizioni_spostate. N°120 (YFNSM) e' poi passato a id-harry-osborn-ynfsm (v. sotto).
    hr = next(i for i in I if i['id'] == 'id-harry-osborn-green-goblin'); assert '005' in hr['apparizioni'] and '005' in titoli('uni-earth-120703-garfield-verse')
    hr['apparizioni'] = [n for n in hr['apparizioni'] if n != '005']; hr['apparizioni_spostate'] = {'005': 'id-harry-osborn-webb'}; hr['alias'] = sorted(set(hr['alias']) | {hr['nome']}); hr['nome'] = 'Harry Osborn/Green Goblin (Raimi)'
    hr['nota'] = "N°005 (The Amazing Spider-Man 2) appartiene alla continuita' Webb: spostato in id-harry-osborn-webb (decisione dell'utente 25/11/2026). N°120 (serie animata) e' poi passato a id-harry-osborn-ynfsm."
    I.append(ident('id-harry-osborn-webb', 'Harry Osborn/Green Goblin (Webb)', 'identita', 'uni-earth-120703-garfield-verse', ['char-harry-osborn-green-goblin'], 'char-harry-osborn-green-goblin', [], ['int-identita', 'int-mv'], apparizioni=['005'],
                   verifica="parziale: continuita' dichiarata da mvMapData (N°005 in uni-earth-120703-garfield-verse) e dalla scheda Atlante (UNIVERSI: Earth-96283 · Earth-120703 · YFNSM); nessun dato biografico specifico attribuito",
                   note="Separato da id-harry-osborn-green-goblin (Raimi) per decisione dell'utente (25/11/2026). La scheda char-harry-osborn-green-goblin descrive insieme piu' continuita': i suoi campi restano attribuiti all'identita' Raimi e non a questa."))
    rel('id-harry-osborn-green-goblin', 'id-harry-osborn-webb', 'stessa_scheda_atlante', 'stessa_scheda_atlante', False, ['int-identita', 'int-mv'], "dati interni: la scheda char-harry-osborn-green-goblin copre piu' continuita'; nessuna parentela narrativa dichiarata", "Continuita' distinte (Raimi-Verse / Garfield-Verse): identita' distinte, non unificate.")
    # Harry Osborn YFNSM (decisione dell'utente, 25/11/2026 sera): N°120 passa a id-harry-osborn-ynfsm; Raimi resta con 001-003.
    hr['apparizioni'] = [n for n in hr['apparizioni'] if n != '120']; hr['apparizioni_spostate'] = {'005': 'id-harry-osborn-webb', '120': 'id-harry-osborn-ynfsm'}
    hr['nota'] = "N°005 (Webb) e N°120 (Your Friendly Neighborhood Spider-Man) appartengono ad altre continuita': spostati in id-harry-osborn-webb e id-harry-osborn-ynfsm (decisioni dell'utente 25/11/2026). Raimi mantiene N°001-003."
    assert '120' in titoli('uni-your-friendly-neighborhood-spider-man-verse')
    I.append(ident('id-harry-osborn-ynfsm', 'Harry Osborn/Green Goblin (Your Friendly Neighborhood Spider-Man)', 'identita', 'uni-your-friendly-neighborhood-spider-man-verse', ['char-harry-osborn-green-goblin'], 'char-harry-osborn-green-goblin', [], ['int-identita', 'int-mv'], apparizioni=['120'],
                   verifica="parziale: continuita' dichiarata da mvMapData (N°120 in uni-your-friendly-neighborhood-spider-man-verse) e dalla scheda Atlante (UNIVERSI); nessun dato biografico specifico attribuito",
                   note="Separato dalle identita' Raimi e Webb per decisione dell'utente (25/11/2026). I campi della scheda condivisa restano attribuiti all'identita' Raimi."))
    rel('id-harry-osborn-green-goblin', 'id-harry-osborn-ynfsm', 'stessa_scheda_atlante', 'stessa_scheda_atlante', False, ['int-identita', 'int-mv'], "dati interni: la scheda char-harry-osborn-green-goblin copre piu' continuita'; nessuna parentela narrativa dichiarata", "Continuita' distinte: identita' distinte, non unificate.")
    rel('id-harry-osborn-webb', 'id-harry-osborn-ynfsm', 'stessa_scheda_atlante', 'stessa_scheda_atlante', False, ['int-identita', 'int-mv'], "dati interni: la scheda char-harry-osborn-green-goblin copre piu' continuita'; nessuna parentela narrativa dichiarata", "Continuita' distinte: identita' distinte, non unificate.")
    # Matt Murdock: Ben Affleck (Daredevil 2003) e Charlie Cox (MCU: Netflix + Marvel Studios) in due identita' (richiesta dell'utente, 26/11/2026).
    # Stesso schema di Wolverine/Harry: id-matt-murdock-daredevil resta (stesso ID, stessa pagina canonica; le immagini candidate e gli eventuali ritratti salvati
    # sono legati a questo ID e alla sola N°035) e rappresenta la continuita' del film 2003; le apparizioni MCU passano a id-matt-murdock-mcu, tracciate in apparizioni_spostate.
    # Fonte: Wikipedia (Matt Murdock (MCU): «implied» incarnazione di Affleck nel MCU ma mai dichiarata) -> nessuna unificazione.
    md = next(i for i in I if i['id'] == 'id-matt-murdock-daredevil'); mcu_t = titoli('uni-earth-199999-mcu'); mv_ap = [n for n in md['apparizioni'] if n in mcu_t]
    assert mv_ap == ['060', '065', '082', '105', '122', '128'] and '035' in titoli('uni-daredevil-elektra-verse')
    md['apparizioni'] = [n for n in md['apparizioni'] if n not in mcu_t]; md['apparizioni_spostate'] = {n: 'id-matt-murdock-mcu' for n in mv_ap}
    md['nome'] = 'Matt Murdock/Daredevil (2003)'; md['alias'] = sorted(set(md['alias']) | {'Matt Murdock/Daredevil'}); md['interpreti'] = ['Ben Affleck']
    md['fonte'] = (md.get('fonte') or []) + [F['w-daredevil-film']]
    md['nota'] = "Continuita' del film Daredevil (2003): interprete Ben Affleck (N°035). Le apparizioni MCU (Netflix, She-Hulk, Born Again) sono in id-matt-murdock-mcu (interprete Charlie Cox). Per Wikipedia la versione MCU e' solo «implicitamente» l'incarnazione di Affleck, mai dichiarata: identita' distinte, non unificate."
    I.append(ident('id-matt-murdock-mcu', 'Matt Murdock/Daredevil (MCU)', 'identita', 'uni-earth-199999-mcu', ['char-matt-murdock-daredevil'], 'char-matt-murdock-daredevil', ['Charlie Cox'], ['w-murdock-mcu', 'int-mv'], apparizioni=mv_ap,
                   verifica="verificata sulle fonti consultate il 26/11/2026 (Wikipedia: Matt Murdock (MCU), Daredevil in other media): Charlie Cox interpreta Matt Murdock nel MCU (Daredevil, The Defenders, She-Hulk, Echo, Born Again); apparizioni dalla scheda Atlante e da mvMapData",
                   note="Separato da id-matt-murdock-daredevil (film 2003, Ben Affleck) su richiesta dell'utente (26/11/2026). I campi della scheda condivisa restano attribuiti all'identita' esistente per non perdere riferimenti."))
    rel('id-matt-murdock-daredevil', 'id-matt-murdock-mcu', 'stessa_scheda_atlante', 'stessa_scheda_atlante', False, ['w-murdock-mcu', 'int-mv'], "dati interni: la scheda char-matt-murdock-daredevil copre due continuita'; nessuna parentela narrativa dichiarata", "Continuita' distinte (Daredevil 2003 / MCU): identita' distinte, non unificate.")
    # Laufey: dossier autonomo (richiesta dell'utente, 26/11/2026). Nessuna scheda nell'Atlante classico (la scheda di Loki lo cita solo come testo: «Padre biologico: Laufey»):
    # identita' nuova nell'MCU, con i soli dati verificati su fonti pubbliche (interprete e film). Nessun campo biografico inventato.
    lf = ident('id-laufey', 'Laufey', 'identita', 'uni-earth-199999-mcu', [], None, ['Colm Feore'], ['int-identita'], apparizioni=['050'],
               verifica="verificata sulle fonti consultate il 26/11/2026 (Wikipedia: Thor (film)): re dei Giganti di Ghiaccio di Jotunheim, padre biologico di Loki, interpretato da Colm Feore, appare in Thor (N°050); nessun altro dato attribuito",
               note="Dossier autonomo: nessuna scheda nell'Atlante classico (citato solo come testo nel campo RELAZIONI della scheda di Loki). Apparizione limitata a Thor (2011) secondo la fonte consultata.")
    lf['fonte'] = ['https://en.wikipedia.org/wiki/Thor_(film)', 'https://en.wikipedia.org/wiki/Laufey_(Marvel_Comics)']
    lf['senza_scheda_classica'] = True
    I.append(lf)
    # Peter (franchise Deadpool): continuita' Fox-Verse (Earth-10005), come Wade Wilson (stesse apparizioni 024/117 nella guida).
    # Fonti consultate il 25/11/2026: Marvel Movies Wiki (Peter Wisdom: «Earth-10005», Deadpool 2 prima apparizione, Deadpool & Wolverine), Marvel Cinematic Universe Wiki (D&W: Earth-10005), GamesRadar (riappare in D&W nello stesso concessionario di Wade).
    pt = next(i for i in I if i['id'] == 'id-peter'); pt['universo'] = 'uni-earth-10005-fox-verse'
    pt['verifica'] = "verificata sulle fonti consultate il 25/11/2026 (Marvel Movies Wiki, Marvel Cinematic Universe Wiki, GamesRadar, SlashFilm): personaggio originale di Earth-10005, prima apparizione Deadpool 2 (2018), riappare in Deadpool & Wolverine nella stessa Earth-10005; nota: alcune fonti lo identificano con Pete Wisdom, l'attore lo ha smentito (SlashFilm) -> nessuna identificazione applicata"
    pt['fonte'] = pt['fonte'] + ['https://marvel-movies.fandom.com/wiki/Peter_Wisdom', 'https://marvelcinematicuniverse.fandom.com/wiki/2020s/Earth-10005', 'https://slashfilm.com/2306570/deadpool-2-rob-delaney-debunk-x-men-fan-theory-peter']
    # collegamenti da classificare (solo pagine divise in piu' identita')
    DIVISE = {k: v['verso'] for k, v in RED.items() if v['ruolo'] in ('pagina-hub', 'pagina-storica')}
    IDX = {i['id']: i for i in I}
    cl = []
    def proposta(src, targets):
        uni = set(APPART.get(src, []))
        m = [t for t in targets if t in IDX and IDX[t]['universo'] in uni]
        return (m[0], 'proposta automatica: continuita\' della scheda sorgente') if len(m) == 1 else (None, 'da decidere: continuita\' ambigua o assente')
    tutte = {e['id']: e for f in ('personaggi', 'universi', 'organizzazioni', 'artefatti', 'luoghi', 'pianeti', 'eventi', 'battaglie', 'attori') for e in jl(f + '.json')['voci']}
    for src, e in tutte.items():
        for l in e['collegamenti']:
            if l['a'] in DIVISE:
                t, w = proposta(src, DIVISE[l['a']]); cl.append({'da': src, 'a_pagina': l['a'], 'origine': 'link scheda', 'identita_proposta': t, 'stato': w})
    for src, v in GRAFO.items():
        for c in v['conns']:
            if c['id'] in DIVISE:
                t, w = proposta(src, DIVISE[c['id']]); cl.append({'da': src, 'a_pagina': c['id'], 'origine': 'grafo (%s)' % c.get('rtype'), 'identita_proposta': t, 'stato': w})
    return {'versione': 1, 'modello': 'docs/ATLANTE_2_0_MODELLO_IDENTITA.md', 'identita': I, 'hub': HUB, 'mantelli': MAN, 'segnaposto': SEG, 'relazioni': REL,
            'redirect': RED, 'sospese': SOSP, 'collegamenti_da_classificare': cl,
            'aperte': ["Xavier: ordine delle timeline pre/post Days of Future Past non verificato", "Coulson: N°091 su char-coulson da verificare (Sarge/LMD/flashback)", "Groot: relazione originale/successore e' dichiarazione d'autore, non esplicita nei film", "Professor X Terra-838: di quale identita' sia variante non e' indicato dalle fonti", "Peter B. Parker, Kingpin animato: identita' collegata all'hub senza relazione di variante verificata verso un'identita' specifica", "Terra-616 (Peter, Fisk): segnaposto senza dati", "Link entranti verso pagine divise (Peter Parker, Groot, Wilson Fisk): vedi collegamenti_da_classificare", "Bishop e Janet: sospese"]}

def conteggi(r):
    ident = r['identita']
    return {'pagine_char': len(PERS), 'pagine_che_contavano': sum(CONTA.values()), 'identita_totali': len(ident), 'identita_che_contano': sum(1 for i in ident if i['conta_come_personaggio']),
            'hub': len(r['hub']), 'mantelli': len(r['mantelli']), 'segnaposto': len(r['segnaposto']), 'relazioni_narrative': sum(1 for x in r['relazioni'] if x['narrativa']), 'relazioni_non_narrative': sum(1 for x in r['relazioni'] if not x['narrativa']),
            'collegamenti_da_classificare': len(r['collegamenti_da_classificare']), 'di_cui_proposta_automatica': sum(1 for c in r['collegamenti_da_classificare'] if c['identita_proposta'])}

def scrivi():
    r = costruisci(); r['conteggi'] = conteggi(r)
    json.dump(r, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print(json.dumps(r['conteggi'], ensure_ascii=False, indent=1))

def verifica():
    ok = True
    def chk(n, c, d=''):
        nonlocal ok
        print(('PASS ' if c else 'FAIL ') + n + (' ' + str(d) if (d and not c) else '')); ok &= bool(c)
    r = json.load(open(OUT, encoding='utf-8')); fresh = costruisci(); fresh['conteggi'] = conteggi(fresh)
    chk('identita.json = ricostruzione deterministica', r == json.loads(json.dumps(fresh, ensure_ascii=False)))
    chk('ogni pagina char-* ha una voce in redirect (0 id persi)', set(r['redirect']) == set(PERS), set(PERS) ^ set(r['redirect']))
    IDS = {i['id'] for i in r['identita']} | {h['id'] for h in r['hub']} | {m['id'] for m in r['mantelli']} | {s['id'] for s in r['segnaposto']}
    chk('ogni redirect punta a entita\' esistenti', all(t in IDS for v in r['redirect'].values() for t in v['verso']))
    chk('id entita\' univoci', len(IDS) == len(r['identita']) + len(r['hub']) + len(r['mantelli']) + len(r['segnaposto']))
    chk('pagine_principali esistono come schede', all(i['pagina_principale'] in PERS for i in r['identita'] if not i.get('senza_scheda_classica')))
    chk('hub, mantelli e segnaposto NON contano come personaggi', all(not x['conta_come_personaggio'] for x in r['hub'] + r['mantelli'] + r['segnaposto']))
    chk('membri degli hub esistono', all(m in IDS for h in r['hub'] for m in h['membri']))
    chk('hub Peter: 6 membri dichiarati = 6 identita\' elencate', len(next(h for h in r['hub'] if h['id'] == 'hub-peter-parker')['membri']) == 6)
    chk('relazioni: estremi esistenti', all(x['da'] in IDS and x['a'] in IDS for x in r['relazioni']))
    chk('nessuna co-apparizione tra le relazioni narrative', all(x['tipo'] not in ('co_apparizione', 'stesso_universo', 'stesso_attore') for x in r['relazioni']))
    chk('ogni entita\' ha fonte e verifica', all(i.get('fonte') and i.get('verifica') for i in r['identita']) and all(h.get('verifica') for h in r['hub'] + r['segnaposto']))
    chk('Bishop/Kate Bishop/Janet/Janet van Dyne sospese e senza relazioni', set(r['sospese']) == {'char-bishop', 'char-kate-bishop', 'char-janet', 'char-janet-van-dyne'} and all(r['redirect'][p]['ruolo'] == 'sospesa' for p in r['sospese']) and not any(x['da'] in {'id-bishop', 'id-kate-bishop', 'id-janet', 'id-janet-van-dyne'} or x['a'] in {'id-bishop', 'id-kate-bishop', 'id-janet', 'id-janet-van-dyne'} for x in r['relazioni']))
    chk('cambio di attore non e\' variante (Ross, Xavier)', all(x['tipo'] in ('cambio_attore', 'incarnazione') for i in r['identita'] if i['id'] in ('id-thaddeus-ross-mcu', 'id-charles-xavier-fox') for x in i['incarnazioni']))
    chk('nessuna unificazione tra persone distinte (Steve/Sam, Johnny/Robbie, Everett/Thaddeus, MJ/Mary Jane, Peter/Quill)', all(len(set(r['redirect'][p]['verso']) & set(r['redirect'][q]['verso'])) == 0 for p, q in (('char-steve-rogers-capitan-america', 'char-sam-wilson-capitan-america'), ('char-johnny-blaze-ghost-rider', 'char-robbie-reyes-ghost-rider'), ('char-everett-ross', 'char-thaddeus-ross'), ('char-mj', 'char-mary-jane-watson'), ('char-peter', 'char-peter-quill-star-lord'), ('char-generale-thaddeus-ross', 'char-generale-ross'), ('char-groot-piccolo', 'char-peter-b-parker'))))
    OPERE = {o['id'] for o in ATLAS['opere']}
    chk('apparizioni delle identita\' = N° esistenti nel registro opere', all(n in OPERE for i in r['identita'] for n in i['apparizioni']))
    chk('apparizioni dell\'identita\' sono sottoinsieme di quelle delle sue pagine (nessun dato inventato)', all(set(i['apparizioni']) <= set(sum([apps(p) for p in i['pagine']], [])) for i in r['identita'] if i['pagine']))
    chk('Peter: ogni apparizione assegnata a un solo universo di continuita\' o dichiarata condivisa (099)', all(set(a['apparizioni']) & set(b['apparizioni']) <= {'099'} for a in r['identita'] if a['id'].startswith('id-peter-parker') for b in r['identita'] if b['id'].startswith('id-peter-parker') and a['id'] < b['id']))
    # Invarianti dei dati esistenti (nessuna modifica a A1/baseline)
    m = json.load(open(os.path.join(D, 'baseline_A0.json'), encoding='utf-8'))
    import hashlib
    s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read(); sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import atlante_estrai as A
    mm = A.misure(s, A.estrai(s))
    for k in ('conteggi', 'ids_sha256', 'html_sha256', 'blob', 'link_mvNavigate', 'link_rotti'): chk('baseline A0 invariata: %s' % k, m[k] == mm[k])
    chk('Tessera: blob id/poteri/livelli invariati', all(m['blob'][b] == mm['blob'][b] for b in ('tesseraCharIdsData', 'tesseraCharPowersData', 'tesseraCharLevelsData')))
    chk('Miss Minutes: blob letti dall\'host invariati', all(m['blob'][b] == mm['blob'][b] for b in m['blob']))
    wv = {i['id']: i for i in r['identita']}
    chk("Wolverine: N°131 solo nell'identita' X-Men '97; nessuna apparizione persa (unione = originale)", '131' not in wv['id-wolverine']['apparizioni'] and wv['id-wolverine-x-men-97']['apparizioni'] == ['131'] and set(wv['id-wolverine']['apparizioni']) | {'131'} == {'013', '014', '015', '016', '017', '018', '023', '117', '131'})
    chk("Wolverine: char-wolverine resta canonica verso id-wolverine (link entranti invariati); universi distinti", r['redirect']['char-wolverine'] == {'ruolo': 'canonica', 'verso': ['id-wolverine'], 'nota': ''} and wv['id-wolverine']['universo'] == 'uni-earth-10005-fox-verse' and wv['id-wolverine-x-men-97']['universo'] == 'uni-x-men-97-verse')
    hh = {i['id']: i for i in r['identita']}
    chk("Harry Osborn: N°005 solo in Webb, N°120 solo in YFNSM, nessuna apparizione persa, ID e pagina canonica invariati", '005' not in hh['id-harry-osborn-green-goblin']['apparizioni'] and '120' not in hh['id-harry-osborn-green-goblin']['apparizioni'] and hh['id-harry-osborn-webb']['apparizioni'] == ['005'] and hh['id-harry-osborn-ynfsm']['apparizioni'] == ['120'] and set(hh['id-harry-osborn-green-goblin']['apparizioni']) | {'005', '120'} == {'001', '002', '003', '005', '120'} and r['redirect']['char-harry-osborn-green-goblin']['verso'] == ['id-harry-osborn-green-goblin'] and hh['id-harry-osborn-ynfsm']['universo'] == 'uni-your-friendly-neighborhood-spider-man-verse')
    chk("Peter (Deadpool): assegnato a Fox-Verse con fonti, come Wade Wilson", hh['id-peter']['universo'] == 'uni-earth-10005-fox-verse' and set(hh['id-peter']['apparizioni']) <= set(hh['id-wade-wilson-deadpool']['apparizioni']))
    mm_ = {i['id']: i for i in r['identita']}
    chk("Matt Murdock: 035 solo nel 2003 (Affleck), 060-128 solo nell'MCU (Cox); nessuna apparizione persa; ID e pagina canonica invariati", mm_['id-matt-murdock-daredevil']['apparizioni'] == ['035'] and mm_['id-matt-murdock-mcu']['apparizioni'] == ['060', '065', '082', '105', '122', '128'] and mm_['id-matt-murdock-daredevil']['pagina_principale'] == 'char-matt-murdock-daredevil' and r['redirect']['char-matt-murdock-daredevil']['verso'] == ['id-matt-murdock-daredevil'])
    c = r['conteggi']
    chk('conteggio identita\' coerente (che contano = totali - non contanti)', c['identita_che_contano'] == sum(1 for i in r['identita'] if i['conta_come_personaggio']))
    print('ESITO:', 'OK' if ok else 'FALLITO'); return 0 if ok else 1
if __name__ == '__main__':
    if '--scrivi' in sys.argv: scrivi()
    if '--verifica' in sys.argv: sys.exit(verifica())
