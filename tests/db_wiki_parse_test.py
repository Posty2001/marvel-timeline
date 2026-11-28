import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent/'tools'))
import db_wiki_parse as P
ok = fail = 0
def t(m, c, d=''): chk(c, m + ' ' + str(d))
def chk(c, m):
    global ok, fail
    if c: ok += 1
    else: fail += 1; print('FAIL', m)
WT = """{{Character Infobox
| title1 = Zaxx the Wanderer
| Portrayed by = [[Jane Actor]]<ref>cit</ref>
| Species = [[Human]]; [[Kree]]
| Status = Alive
| Affiliation = [[Kree Collective|The Collective]]<br>[[Avengers]]
| First appearance = ''[[Test Film]]''
}}
'''Zaxx''' is a long prose paragraph that must never be stored.
== Powers and Abilities ==
* '''Super Strength''': can lift things.
* [[Energy Projection]] - blasts
== Equipment ==
; Ancient Blade
; [[Hidden Vault|Vault Key]]
== Weaknesses ==
Only prose here with no list.
[[Category:Characters]]
[[Category:Kree]]"""
ib = P.infobox(WT); chk(ib.get('portrayedby') == 'Jane Actor', 'infobox portrayedby ripulito dai ref'); chk(ib.get('affiliation') == 'The Collective; Avengers', 'link con alias + br')
chk(ib.get('firstappearance') == 'Test Film' and ib.get('species') == 'Human; Kree', 'campi')
s = P.sezioni(WT); chk(s.get('poteri') == ['Super Strength', 'Energy Projection'], s); chk(s.get('equipaggiamento') == ['Ancient Blade', 'Vault Key'], s); chk('debolezze' not in s or s['debolezze'] == [], 'prosa non estratta')
chk(P.categorie_wikitext(WT) == ['Characters', 'Kree'], 'categorie')
chk(all(len(v) <= 400 for v in ib.values()), 'lunghezza massima'); chk('long prose' not in str(ib) + str(s), 'nessuna prosa conservata')
chk(P.infobox('{{Marvel Database:Character Template\n|CurrentAlias=Thing\n|Gender=Male\n}}').get('currentalias') == 'Thing', 'template Marvel Database')
chk(P.infobox('niente template') == {}, 'assenza')
wt2 = """{{Quote|a|b}}
{{Character
|name = Arnim Zola
|actor = [[Toby Jones]]<ref name="AEVFX">[https://x.com a|b]</ref>
|first = ''[[Captain America]]''<!-- c|d -->
|status = Deceased
}}"""
ib2 = P.infobox(wt2)
t('infobox con nome di modello non standard (euristica) e note con | e =', ib2.get('name') == 'Arnim Zola' and ib2.get('actor') == 'Toby Jones' and ib2.get('status') == 'Deceased', ib2)
t('chiave non valida scartata', 'x' not in P.infobox('{{Foo infobox|name=A|bad text = x = y|status=Alive}}') and P.infobox('{{Foo infobox|name=A|status=Alive}}').get('status') == 'Alive')
t('modelli(): nomi dei primi modelli', P.modelli(wt2) == ['Quote', 'Character'], P.modelli(wt2))
print(f'db_wiki_parse_test: {ok} ok, {fail} fail'); sys.exit(1 if fail else 0)
