#!/usr/bin/env python3
"""Verifica semantica delle relazioni: costrutti relazionali direzionali, non semplice compresenza di nomi."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent/'tools'))
import db_relverify as V
N = V.nomi_distintivi
CASI = [("Destiny is the mother of Nightcrawler, who is a mutant.", 'famiglia_genitore', ['Nightcrawler'], True, True),
 ("Destiny is the mother of Nightcrawler.", 'famiglia_genitore', ['Nightcrawler'], False, False),
 ("Nightcrawler is the son of Mystique.", 'famiglia_genitore', ['Mystique'], False, True),
 ("Nightcrawler is the son of Mystique.", 'famiglia_genitore', ['Mystique'], True, False),
 ("Mystique and Rogue appear in the same scene together.", 'famiglia_genitore', ['Rogue'], True, False),
 ("Peter and Mary Jane were at school; Mary Jane worked nearby.", 'partner', ['Mary Jane'], True, False),
 ("Rogue fights Mystique.", 'rivalita', ['Mystique'], True, True),
 ("Logan is a member of the X-Men.", 'appartenenza', ['X-Men'], True, True),
 ("Logan met the X-Men at a party.", 'appartenenza', ['X-Men'], True, False),
 ("Matt, his wife Elektra, lives here.", 'famiglia_coniugi', ['Elektra'], True, True)]
ok = fail = 0
for t, tipo, a, sd, atteso in CASI:
    if V.conferma(t, tipo, N(a), sd) == atteso: ok += 1
    else: fail += 1; print('FAIL', t, tipo, sd)
print('db_relverify_test: %d ok, %d fail' % (ok, fail)); sys.exit(1 if fail else 0)
