#!/usr/bin/env python3
"""Miss Minutes 2.0 – archivio di fatti documentati (cast per personaggio/continuita', alias dei titoli).
Genera miss-minutes/knowledge/fatti.json. Solo dati pubblici: nessun dato personale. Nessun fatto inventato:
- cast dalle identita' dell'Atlante (campo `interpreti`, gia' verificato nel registro);
- voci SEED verificate il 26/11/2026 su fonti consultate (URL in `fonte`).
Uso: python3 tools/mm_fatti.py --scrivi | --verifica"""
import json, re, sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, 'miss-minutes/knowledge/fatti.json')
CUES = {  # indizi testuali di continuita'/produzione per riconoscere "interprete giusto, produzione sbagliata"
 'uni-earth-121698': ['story', 'tim story', '2005', '2007', 'rise of the silver surfer', 'earth 121698'],
 'uni-fantastic-four-1994': ['1994', 'mai distribuito', 'corman'],
 'uni-earth-trn123': ['trank', '2015', 'josh trank', 'earth trn123'],
 'uni-earth-828': ['first steps', 'earth 828', 'terra 828', '2025'],
 'uni-earth-838': ['illuminati', 'terra 838', 'earth 838', 'multiverso della follia'],
 'uni-earth-199999-mcu': ['mcu', 'marvel cinematic universe', 'sacred timeline'],
 'uni-earth-96283-raimi-verse': ['raimi', 'sam raimi', 'trilogia di raimi'],
 'uni-earth-120703-garfield-verse': ['garfield', 'amazing spider man', 'webb', 'marc webb'],
 'uni-earth-10005-fox-verse': ['fox', 'x men fox', 'bryan singer'],
 'uni-daredevil-elektra-verse': ['2003', 'elektra', 'mark steven johnson'],
 'uni-hulk-2003-verse': ['hulk 2003', 'ang lee', '2003'],
}
SEED = [  # (personaggio[], attori[], universo, produzione, fonte)
 (['Tony Stark', 'Iron Man'], ['Robert Downey Jr.'], 'uni-earth-199999-mcu', 'MCU (Infinity Saga)', 'https://en.wikipedia.org/wiki/Marvel_Cinematic_Universe:_Phase_Six'),
 (['Victor von Doom', 'Doctor Doom', 'Dr. Doom', 'Doom'], ['Robert Downey Jr.'], 'uni-earth-199999-mcu', 'Avengers: Doomsday (2026, MCU)', 'https://www.marvel.com/movies/avengers-doomsday'),
 (['Steve Rogers', 'Captain America'], ['Chris Evans'], 'uni-earth-199999-mcu', 'MCU', 'https://www.themoviedb.org/movie/1003596-avengers-doomsday'),
 (['Thor', 'Thor Odinson'], ['Chris Hemsworth'], 'uni-earth-199999-mcu', 'MCU', 'https://www.themoviedb.org/movie/1003596-avengers-doomsday'),
 (['Sam Wilson'], ['Anthony Mackie'], 'uni-earth-199999-mcu', 'MCU', 'https://www.themoviedb.org/movie/1003596-avengers-doomsday'),
 (['Scott Lang', 'Ant-Man'], ['Paul Rudd'], 'uni-earth-199999-mcu', 'MCU', 'https://www.themoviedb.org/movie/1003596-avengers-doomsday'),
 (['Yelena Belova'], ['Florence Pugh'], 'uni-earth-199999-mcu', 'MCU', 'https://www.themoviedb.org/movie/1003596-avengers-doomsday'),
]
def base_names(nome):
    n = re.sub(r'\s*\([^)]*\)', '', nome)
    return [x.strip() for x in n.split('/') if x.strip()]
def costruisci():
    I = json.load(open(os.path.join(R, 'data/atlante/identita.json')))['identita']
    cast = []
    for i in I:
        if not i.get('interpreti'): continue
        cast.append({'pers': base_names(i['nome']), 'attori': i['interpreti'], 'univ': i['universo'], 'prod': i['nome'], 'cues': CUES.get(i['universo'], []), 'fonte': 'TVA Atlas (registro identita\')', 'id': i['id']})
    for p, a, u, prod, f in SEED:
        cast.append({'pers': p, 'attori': a, 'univ': u, 'prod': prod, 'cues': CUES.get(u, []), 'fonte': f, 'id': 'seed'})
    alias = {  # numero Timeline -> nomi alternativi (non ufficiali: solo per riconoscere la domanda)
        '132': ['Spider-Man 4', 'Spiderman 4', 'Brand New Day'],
        '136': ['Avengers 5', 'Avengers Doomsday', 'Doomsday'],
        '139': ['Avengers 6', 'Secret Wars'],
        '125': ['I Fantastici Quattro: Gli inizi', 'The Fantastic Four First Steps', 'Fantastici Quattro First Steps'],
        '27': ['Beyond the Spider-Verse', 'Spider-Verse 3'],
    }
    return {'versione': 1, 'generato': '2026-11-26', 'nota': 'Dati pubblici documentati; un nome assente NON e\' falso. Le voci seed riportano la fonte consultata.', 'cast': cast, 'alias_titoli': alias}
def main():
    d = costruisci()
    if '--scrivi' in sys.argv:
        json.dump(d, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':')); print('scritto', OUT, len(d['cast']), 'voci cast')
    if '--verifica' in sys.argv or '--scrivi' in sys.argv:
        cur = json.load(open(OUT)); ok = cur == d
        assert all(c['pers'] and c['attori'] for c in cur['cast']); assert ok, 'fatti.json non aggiornato (esegui --scrivi)'
        print('OK', len(cur['cast']), 'voci')
main()
