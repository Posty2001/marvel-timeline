"""Liste di opere per le ondate W3 (serie TV e film live-action non MCU) e W4 (animazione): gruppo -> [(titolo inglese su Wikidata, anno)].
I titoli non trovati NON si inventano: il raccoglitore li registra tra le anomalie. Il gruppo determina la continuita' solo se mappato in db_w1_build.py (GRP_UNI)."""
W3 = {
 'netflix-mcu': [('Daredevil', 2015), ('Jessica Jones', 2015), ('Luke Cage', 2016), ('Iron Fist', 2017), ('The Defenders', 2017), ('The Punisher', 2017)],
 'agents-of-shield': [("Agents of S.H.I.E.L.D.", 2013), ('Agent Carter', 2015)],
 'marvel-tv-mcu': [('Inhumans', 2017), ('Runaways', 2017), ('Cloak & Dagger', 2018), ('Helstrom', 2020)],
 'legion': [('Legion', 2017)], 'the-gifted': [('The Gifted', 2017)],
 'marvel-tv-classico': [('The Incredible Hulk', 1977), ('The Amazing Spider-Man', 1977), ('Doctor Strange', 1978), ('Captain America', 1979), ('Generation X', 1996), ('Nick Fury: Agent of SHIELD', 1998), ('Blade: The Series', 2006), ('Mutant X', 2001)],
 'film-live-action-altri': [('Howard the Duck', 1986), ('The Punisher', 1989), ('Captain America', 1990), ('The Punisher', 2004), ('Man-Thing', 2005), ('Punisher: War Zone', 2008), ('The Incredible Hulk', 2008)],
}
W4 = {
 'what-if': [('What If...?', 2021)], 'x-men-97': [("X-Men '97", 2024)],
 'spider-verse-sony': [('Spider-Man: Into the Spider-Verse', 2018), ('Spider-Man: Across the Spider-Verse', 2023)],
 'yfnsm': [('Your Friendly Neighborhood Spider-Man', 2025)], 'marvel-zombies': [('Marvel Zombies', 2025)],
 'marvel-animation-altre': [('Hit-Monkey', 2021), ('M.O.D.O.K.', 2021), ('I Am Groot', 2022), ('Eyes of Wakanda', 2025), ('Moon Girl and Devil Dinosaur', 2023)],
 'marvel-animation-universe': [('Ultimate Spider-Man', 2012), ('Avengers Assemble', 2013), ('Hulk and the Agents of S.M.A.S.H.', 2013), ('Guardians of the Galaxy', 2015), ('Spider-Man', 2017), ('Avengers: Earth\'s Mightiest Heroes', 2010)],
 'marvel-productions-80-90': [('Spider-Man and His Amazing Friends', 1981), ('X-Men: The Animated Series', 1992), ('Spider-Man: The Animated Series', 1994), ('Iron Man', 1994), ('The Incredible Hulk', 1996), ('The Fantastic Four', 1994), ('Silver Surfer', 1998), ('Spider-Man', 1967), ('Fantastic Four', 1967)],
 'animazione-2000-2010': [('The Avengers: United They Stand', 1999), ('X-Men: Evolution', 2000), ('Wolverine and the X-Men', 2008), ('The Spectacular Spider-Man', 2008), ('Iron Man: Armored Adventures', 2008), ('The Super Hero Squad Show', 2009), ('Ultimate Avengers', 2006), ('Doctor Strange: The Sorcerer Supreme', 2007), ('Planet Hulk', 2010)],
 'marvel-anime-e-altri': [('Iron Man', 2010), ('Blade', 2011), ('Big Hero 6', 2014), ('Big Hero 6: The Series', 2017), ('Marvel Rising: Secret Warriors', 2018)],
}
