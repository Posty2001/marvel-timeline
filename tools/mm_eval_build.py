#!/usr/bin/env python3
"""Fase C - genera miss-minutes/eval/domande.json (set di valutazione di Miss Minutes 2.0).

Ogni domanda: id, cat, q, [dopo] = id della domanda precedente della stessa catena (stessa conversazione),
  tipo: 'fatto' | 'fresco' | 'incerto' | 'falsa'   (cosa si misura)
  ok:   lista di regex (basta UNA per superare) | tutti: lista di regex (servono TUTTE)
  no:   regex che, se presenti, indicano un'affermazione sbagliata (allucinazione)
  hedge: True se dichiarare incertezza e' una risposta corretta
Le attese sono criteri di valutazione AUTOMATICI e indicativi (non correzioni al sistema): il giudizio
finale resta dell'utente (eval/manuale.json). Nessun criterio e' specifico per un titolo nel codice di Miss Minutes.
"""
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, 'miss-minutes', 'eval', 'domande.json')
Q = []
SET = ['S']   # S = set di sviluppo (81 domande note), V = set di validazione (domande nuove, mai usate per sviluppare il sistema)
def q(id, cat, dom, tipo='fatto', ok=None, tutti=None, no=None, hedge=False, dopo=None, nota='', nopers=False):
    d = {'id': id, 'cat': cat, 'q': dom, 'tipo': tipo, 'set': SET[0]}
    if nopers: d['nopers'] = True
    if ok: d['ok'] = ok
    if tutti: d['tutti'] = tutti
    if no: d['no'] = no
    if hedge: d['hedge'] = True
    if dopo: d['dopo'] = dopo
    if nota: d['nota'] = nota
    Q.append(d)

# --- MCU
q('mcu01', 'MCU', 'Chi interpreta Tony Stark nell\'MCU?', ok=['Downey'])
q('mcu02', 'MCU', 'In che anno è uscito il primo Iron Man?', ok=['2008'], no=['2007|2009'])
q('mcu03', 'MCU', 'Chi ha diretto Thunderbolts*?', ok=['Schreier'])
q('mcu04', 'MCU', 'Chi è il cattivo principale di Avengers: Infinity War?', ok=['Thanos'])
q('mcu05', 'MCU', 'Quale attore interpreta Thor?', ok=['Hemsworth'])
q('mcu06', 'MCU', 'Cosa succede a Tony Stark alla fine di Avengers: Endgame?', ok=['mu[oi]r', 'sacrific', 'schiocc'])
q('mcu07', 'MCU', 'Quanti film compongono la Saga dell\'Infinito?', ok=['\\b23\\b', 'ventitré|ventitre'], hedge=True)
q('mcu08', 'MCU', 'Quando è uscita la serie Wonder Man?', 'fresco', ok=['27 gennaio', 'gennaio 2026'], hedge=True)
q('mcu09', 'MCU', 'Chi interpreta Matt Murdock in Daredevil: Rinascita?', ok=['Cox'])
q('mcu10', 'MCU', 'Chi interpreta la Strega Scarlatta?', ok=['Olsen'])
# --- Sony
q('son01', 'Sony', 'Chi interpreta Peter Parker nei film di Sam Raimi?', ok=['Maguire'], no=['Garfield|Holland'])
q('son02', 'Sony', 'Chi ha interpretato Peter Parker in The Amazing Spider-Man?', ok=['Garfield'])
q('son03', 'Sony', 'Chi ha diretto il Venom del 2018?', ok=['Fleischer'])
q('son04', 'Sony', 'Chi interpreta Morbius nel film Morbius?', ok=['Leto'])
q('son05', 'Sony', 'Chi interpreta Kraven nel film Kraven - Il cacciatore?', ok=['Taylor-Johnson'])
q('son06', 'Sony', 'Quale attrice interpreta Madame Web nel film omonimo?', ok=['Dakota Johnson'])
q('son07', 'Sony', 'Quando uscirà Spider-Man: Beyond the Spider-Verse?', 'fresco', ok=['2027'], hedge=True)
# --- Fox
q('fox01', 'Fox', 'Chi interpreta Wolverine in Logan - The Wolverine?', ok=['Jackman'])
q('fox02', 'Fox', 'Chi ha diretto X-Men: Giorni di un futuro passato?', ok=['Singer'])
q('fox03', 'Fox', 'Chi interpreta Reed Richards nei Fantastici 4 del 2005?', ok=['Gruffudd'], no=['Teller|Pascal'])
q('fox04', 'Fox', 'Chris Evans ha recitato anche nei Fantastici 4 del 2005? Con quale ruolo?', ok=['Johnny Storm|Torcia'])
q('fox05', 'Fox', 'Chi interpreta Deadpool?', ok=['Reynolds'])
q('fox06', 'Fox', 'Quando è uscito in Italia Deadpool & Wolverine?', 'fresco', ok=['24 luglio', 'luglio 2024'])
q('fox07', 'Fox', 'Chi interpreta Matt Murdock nel film Daredevil del 2003?', ok=['Affleck'])
# --- Fumetti
q('fum01', 'Fumetti', 'Chi ha creato Spider-Man nei fumetti?', ok=['Ditko'])
q('fum02', 'Fumetti', 'In quale albo appare per la prima volta Spider-Man?', ok=['Amazing Fantasy'])
q('fum03', 'Fumetti', 'Cos\'è "Brand New Day" nei fumetti di Spider-Man?', ok=['2008'], tutti=['(?i)fumett|storyline|ciclo|serie|albo'])
q('fum04', 'Fumetti', 'Chi ha creato i Fantastici Quattro?', ok=['Kirby'])
q('fum05', 'Fumetti', 'Chi ha creato Miles Morales?', ok=['Bendis', 'Pichelli'])
q('fum06', 'Fumetti', 'In quale fumetto compare per la prima volta Wolverine?', ok=['Hulk'], hedge=True)
q('fum07', 'Fumetti', 'Cos\'è la saga a fumetti Secret Wars del 1984?', ok=['1984|Shooter|Beyonder'], hedge=True)
# --- Multiverso
q('mul01', 'Multiverso', 'Cos\'è la Sacred Timeline?', ok=['Loki', 'TVA', 'Linea temporale sacra'])
q('mul02', 'Multiverso', 'Qual è il numero della Terra dell\'MCU?', ok=['199999'], hedge=True)
q('mul03', 'Multiverso', 'Cos\'è Terra-616?', ok=['616'], tutti=['(?i)fumett|principale|universo'])
q('mul04', 'Multiverso', 'Quali Spider-Man compaiono in Spider-Man: No Way Home?', tutti=['Maguire', 'Garfield', 'Holland'])
q('mul05', 'Multiverso', 'Cos\'è un evento Nexus in Loki?', ok=['ramific|variante|Sacred|Sacra|timeline|linea temporale'])
q('mul06', 'Multiverso', 'Cos\'è un\'incursione nel multiverso Marvel?', ok=['colli|scontr|distru|universi'], hedge=True)
q('mul07', 'Multiverso', 'Chi è Kang il Conquistatore?', ok=['Kang'], tutti=['(?i)Majors|varian|Conquistatore|Immortus'])
# --- Attori / cast
q('att01', 'Attori', 'Che ruolo ha Paul Rudd nell\'MCU?', ok=['Scott Lang|Ant-Man'])
q('att02', 'Attori', 'In quale ruolo Scarlett Johansson recita nell\'MCU?', ok=['Vedova Nera|Black Widow|Natasha'])
q('att03', 'Attori', 'Che personaggio interpreta Tom Hardy nei film Venom?', ok=['Eddie Brock'])
q('att04', 'Attori', 'Chi recita in Thunderbolts*?', 'fatto', ok=['Florence Pugh|Pugh|Sebastian Stan|Harbour'])
q('att05', 'Attori', 'Chi sono gli interpreti principali di Spider-Man: Brand New Day?', 'fresco', ok=['Holland'], hedge=True)
q('att06', 'Attori', 'Hugh Jackman compare in Deadpool & Wolverine?', ok=['sì|si,|Jackman'], no=['non compare|non c\'è'])
# --- Cronologia
q('cro01', 'Cronologia', 'Captain Marvel è ambientato prima o dopo Avengers: Endgame?', ok=['prima|1995'])
q('cro02', 'Cronologia', 'In che anno è ambientato Captain Marvel?', ok=['1995'])
q('cro03', 'Cronologia', 'Black Widow è ambientato prima o dopo Captain America: Civil War?', ok=['dopo'], hedge=True)
q('cro04', 'Cronologia', 'Quale film guardo subito dopo Avengers: Endgame in ordine di uscita?', ok=['Far From Home|WandaVision|Loki|Falcon'], hedge=True)
# --- Novità / uscite
q('nov01', 'Novità', 'Spider-Man: Brand New Day è già uscito? Di cosa parla?', 'fresco', ok=['29 luglio|31 luglio|luglio 2026|2026'], no=['2008', '(?i)ciclo (di )?fumett'])
q('nov02', 'Novità', 'Quando esce Avengers: Doomsday?', 'fresco', ok=['dicembre 2026|16 dicembre|18 dicembre'])
q('nov03', 'Novità', 'Avengers: Doomsday è già uscito?', 'fresco', ok=['non (è )?ancora|prossim|dicembre|uscirà'], no=['(?<!non )(?<!ancora )è (già )?uscit[oa]\\b'])
q('nov04', 'Novità', 'Quando esce Avengers: Secret Wars?', 'fresco', ok=['dicembre 2027|2027'], hedge=True)
q('nov05', 'Novità', 'Quali sono le prossime uscite Marvel al cinema?', 'fresco', ok=['Doomsday'], hedge=True)
q('nov06', 'Novità', 'Chi dirige Avengers: Doomsday?', 'fresco', ok=['Russo'], hedge=True)
q('nov07', 'Novità', 'Chi interpreta Doctor Doom in Avengers: Doomsday?', 'fresco', ok=['Downey'], hedge=True)
# --- Teorie / speculazioni (incertezza attesa)
q('teo01', 'Teorie', 'Secondo te chi sarà il cattivo finale di Secret Wars?', 'incerto', hedge=True)
q('teo02', 'Teorie', 'È confermato che Tom Holland sarà in Secret Wars?', 'incerto', hedge=True)
q('teo03', 'Teorie', 'Il Wolverine di Hugh Jackman tornerà in Avengers: Doomsday?', 'incerto', hedge=True)
q('teo04', 'Teorie', 'Cosa succederà dopo Avengers: Doomsday?', 'incerto', hedge=True)
# --- Premesse false / inesistenti (non devono essere avallate)
q('fal01', 'Falsa premessa', 'Quando è uscito il film Iron Man 7?', 'falsa', ok=['non (esiste|risulta|ci sono|è mai)|nessun'], hedge=True)
q('fal02', 'Falsa premessa', 'In che ruolo ha recitato Tom Cruise nel primo Iron Man?', 'falsa', ok=['non (ha|risulta|compare|era|recita)|nessun'], hedge=True)
q('fal03', 'Falsa premessa', 'Perché Andrew Garfield ha recitato in Spider-Man: Homecoming?', 'falsa', ok=['non (ha|risulta|compare|era|recita)|nessun'], hedge=True)
q('fal04', 'Falsa premessa', 'Quando esce il film Marvel "Spider-Man: Brand New Day 2" con Tobey Maguire?', 'falsa', ok=['non (risulta|esiste|è)|nessun|non ci sono|non ho'], hedge=True)

# --- Catene di seguiti (stessa conversazione)
q('seg01a', 'Seguiti', 'Chi ha interpretato Peter Parker in The Amazing Spider-Man?', ok=['Garfield'])
q('seg01b', 'Seguiti', 'E chi ha diretto quel film?', ok=['Webb'], dopo='seg01a')
q('seg01c', 'Seguiti', 'In che anno è uscito?', ok=['2012'], dopo='seg01b')
q('seg02a', 'Seguiti', 'Parlami di Deadpool & Wolverine.', ok=['Deadpool'], dopo=None)
q('seg02b', 'Seguiti', 'Chi sono i protagonisti?', tutti=['Reynolds', 'Jackman'], dopo='seg02a')
q('seg02c', 'Seguiti', 'E chi è il regista?', ok=['Levy'], dopo='seg02b')
q('seg03a', 'Seguiti', 'Cos\'è Brand New Day?', ok=['Brand New Day'], dopo=None, hedge=True)
q('seg03b', 'Seguiti', 'Intendevo il film, non il fumetto. Chi lo dirige?', ok=['Cretton'], dopo='seg03a', hedge=True)
q('seg03c', 'Seguiti', 'E quando esce in Italia?', 'fresco', ok=['29 luglio|luglio 2026'], dopo='seg03b', hedge=True)
q('seg04a', 'Seguiti', 'Chi interpreta Reed Richards nei Fantastici 4 del 2005?', ok=['Gruffudd'])
q('seg04b', 'Seguiti', 'E nel film del 2015?', ok=['Teller'], dopo='seg04a')
q('seg04c', 'Seguiti', 'E nell\'ultimo uscito?', ok=['Pascal'], dopo='seg04b', hedge=True)
q('seg05a', 'Seguiti', 'Parlami di Captain Marvel.', ok=['Captain Marvel|Carol'], dopo=None)
q('seg05b', 'Seguiti', 'Chi la interpreta?', ok=['Larson'], dopo='seg05a')
q('seg05c', 'Seguiti', 'È uscito prima o dopo Endgame?', ok=['prima'], dopo='seg05b')
q('seg06a', 'Seguiti', 'Chi interpreta Loki?', ok=['Hiddleston'])
q('seg06b', 'Seguiti', 'In quali serie compare?', ok=['Loki'], dopo='seg06a')
q('seg06c', 'Seguiti', 'E nel multiverso, chi è il suo avversario principale?', ok=['Kang|Colui che rimane|He Who Remains|Majors'], dopo='seg06b', hedge=True)


# ===== Set V (validazione, C.1): domande NUOVE, scritte dopo la revisione; non usate per sviluppare ne' tarare il sistema =====
SET[0] = 'V'
q('vmc01', 'MCU', 'Chi ha diretto Black Panther?', ok=['Coogler'])
q('vmc02', 'MCU', 'Chi interpreta Gamora nell\'MCU?', ok=['Saldana|Saldaña'])
q('vmc03', 'MCU', 'Chi è la cattiva principale di Thor: Ragnarok?', ok=['Hela'])
q('vmc04', 'MCU', 'Chi interpreta Doctor Strange?', ok=['Cumberbatch'])
q('vmc05', 'MCU', 'In che anno è uscito Guardiani della Galassia Vol. 3?', ok=['2023'], no=['2022|2024'])
q('vmc06', 'MCU', 'Chi ha diretto Eternals?', ok=['Zhao'])
q('vmc07', 'MCU', 'Chi interpreta Moon Knight nella serie?', ok=['Oscar Isaac|Isaac'])
q('vmc08', 'MCU', 'Chi è il protagonista di Shang-Chi e la leggenda dei Dieci Anelli?', ok=['Simu Liu|Liu'])
q('vmc09', 'MCU', 'Quanti film Marvel sono usciti al cinema nel 2025?', 'fresco', ok=['\\b\\d\\b|tre|quattro|due|cinque'], hedge=True, nopers=True, nota='domanda generale: non deve attivare le statistiche personali')
q('vmc10', 'MCU', 'Chi interpreta Bucky Barnes?', ok=['Sebastian Stan|Stan'])
q('vsp01', 'Sony', 'Chi ha diretto Venom: Let There Be Carnage?', ok=['Serkis'])
q('vsp02', 'Sony', 'Venom: The Last Dance fa parte dell\'MCU?', ok=['no|non|Sony'], tutti=['(?i)Sony'])
q('vsp03', 'Sony', 'Chi dà la voce a Miles Morales nel film Spider-Man: Un nuovo universo?', ok=['Moore'])
q('vfx01', 'Fox', 'Chi interpreta Professor X nei film X-Men di Bryan Singer?', ok=['Stewart'], no=['McAvoy come interprete principale della trilogia originale'])
q('vfx02', 'Fox', 'Chi interpreta Deadpool & Wolverine: quale attore dà vita a Wolverine?', ok=['Jackman'])
q('vfx03', 'Fox', 'Quando è uscito negli Stati Uniti Deadpool & Wolverine?', 'fresco', ok=['26 luglio|luglio 2024'], hedge=True)
q('vnw01', 'Novità', 'Fantastic Four: First Steps è già uscito?', 'fresco', ok=['già uscito|è uscito|uscito (il|nel|a)|luglio 2025|2025'], no=['(?<!non )(?<!ancora )(?<!mai )non è ancora uscito|uscirà|(?<!è )in arrivo nel 2025'], nota='caso segnalato nel collaudo reale')
q('vnw02', 'Novità', 'Chi ha diretto The Fantastic Four: First Steps?', 'fresco', ok=['Shakman'], hedge=True)
q('vnw03', 'Novità', 'Chi interpreta Reed Richards in The Fantastic Four: First Steps?', 'fresco', ok=['Pascal'], hedge=True)
q('vnw04', 'Novità', 'Quando è uscito in Italia Spider-Man: Brand New Day?', 'fresco', ok=['29 luglio'], no=['(?<!non )è ancora (in )?(arrivo|produzione)|non è ancora uscito'], hedge=True)
q('vnw05', 'Novità', 'Quando è uscito negli Stati Uniti Spider-Man: Brand New Day?', 'fresco', ok=['31 luglio'], hedge=True)
q('vnw06', 'Novità', 'Qual è la prossima serie Marvel in arrivo su Disney+?', 'fresco', hedge=True, ok=['Disney'])
q('vfu01', 'Fumetti', 'Chi ha creato Iron Man nei fumetti?', ok=['Lee|Lieber|Heck|Kirby'])
q('vfu02', 'Fumetti', 'Chi ha creato Black Panther nei fumetti?', ok=['Kirby'])
q('vfu03', 'Fumetti', 'Cos\'è Terra-1610?', ok=['Ultimate'], hedge=True)
q('vfm01', 'Formato', 'Avengers: Endgame è un film o una serie?', ok=['film'], no=['(?<!non è un )serie tv'])
q('vfm02', 'Formato', 'Loki è un film o una serie TV?', ok=['serie'])
q('vfm03', 'Formato', 'Ultimate Spider-Man è un fumetto o una serie animata?', tutti=['(?i)fumett', '(?i)animat'], nota='omonimia: entrambe le cose esistono')
q('vfm04', 'Formato', 'Quali serie animate Marvel esistono su Disney+?', ok=['X-Men \'97|X-Men 97|What If|Spider-Man'], hedge=True)
q('vcr01', 'Cronologia', 'In che periodo è ambientato Black Widow?', ok=['Civil War|2016'], hedge=True)
q('vcr02', 'Cronologia', 'In che ordine guardo i film di Spider-Man con Tom Holland?', tutti=['Homecoming', 'Far From Home', 'No Way Home'])
q('vsx01', 'Spoiler', 'Fammi uno spoiler: chi muore in Avengers: Infinity War?', ok=['Gamora|Loki|Heimdall|Vision|metà'], no=['(?i)non posso (fare|rivelare|dirti) spoiler'], nota='spoiler richiesti esplicitamente')
q('vtc01', 'Teorie', 'Secondo te Doctor Doom sarà più forte di Thanos?', 'incerto', hedge=True)
q('vfa01', 'Falsa premessa', 'In quale film Marvel recita Leonardo DiCaprio?', 'falsa', ok=['non|nessun'], hedge=True)
q('vfa02', 'Falsa premessa', 'Perché Chris Hemsworth interpreta Captain America?', 'falsa', ok=['non|Evans'], tutti=['Evans'], hedge=True)
q('vfa03', 'Falsa premessa', 'Quando esce Avengers: Endgame 2?', 'falsa', ok=['non (esiste|risulta|è)|nessun|Doomsday|Secret Wars'], hedge=True)
q('vsg01a', 'Seguiti', 'Parlami di The Marvels.', ok=['Marvels'])
q('vsg01b', 'Seguiti', 'Chi l\'ha diretto?', ok=['DaCosta'], dopo='vsg01a')
q('vsg01c', 'Seguiti', 'E quando è uscito?', 'fresco', ok=['2023|novembre'], dopo='vsg01b', hedge=True)
q('vsg02a', 'Seguiti', 'Parlami della serie Hawkeye.', ok=['Hawkeye|Occhio di Falco'])
q('vsg02b', 'Seguiti', 'Chi interpreta Kate Bishop?', ok=['Steinfeld'], dopo='vsg02a')
q('vsg02c', 'Seguiti', 'E il protagonista maschile?', ok=['Renner'], dopo='vsg02b')

ids = [x['id'] for x in Q]
assert len(ids) == len(set(ids)), 'id duplicati'
for x in Q:
    if x.get('dopo'): assert x['dopo'] in ids
if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cats = {}
    for x in Q: cats[x['cat']] = cats.get(x['cat'], 0) + 1
    if '--scrivi' in sys.argv:
        json.dump({'versione': 1, 'nota': __doc__.strip().split('\n')[0], 'domande': Q}, open(OUT, 'w'), ensure_ascii=False, indent=1)
        print('scritto', OUT)
    print(len(Q), 'domande', cats, {k: sum(1 for x in Q if x['set'] == k) for k in 'SV'})
