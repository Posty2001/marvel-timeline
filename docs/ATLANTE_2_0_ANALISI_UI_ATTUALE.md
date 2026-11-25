# Atlante attuale — analisi dell'interfaccia (base di partenza di Atlante 2.0)

Misurato sull'app reale (Playwright 390 px, build `20261125-0100-mm6`). Screenshot di riferimento mostrati nel confronto «prima/dopo» della Revisione 2.

## Struttura reale
- **Shell «TVA ARCHIVES» propria**: intestazione con tasto indietro, titolo della sezione, ricerca, pillola «App Marvel»; **nessuna barra a tab in basso**; linguetta ambra di Miss Minutes sul bordo destro.
- **Capitoli con portale illustrato** (`.hm-p`): Personaggi, Universi, Eventi, Cronologie, Artefatti/Reliquiario, Organizzazioni, Luoghi, Relazioni, Multiverso, Classifica dei Poteri, Entità Cosmiche, Specie e Civiltà, Arti Mistiche.
- **Mappa del Multiverso (3B)** con nodi reali (27 universi), famiglie colorate, pan/pinch, nature («Continuità principale», «Universo autonomo», «Diramazione», «Luogo narrativo»).
- **Relazioni**: Grafo, Alberi, Kang e la TVA, Varianti. **Classifica dei Poteri**: 159 personaggi in 7 fasce editoriali (non statistiche canoniche).
- **Pagine già esistenti** (correzione di una mia analisi precedente): Entità Cosmiche **26** (6 apparse sullo schermo, 20 mai apparse), Specie e Civiltà **8**, Arti Mistiche **3**. Non «0».

## Punti di forza da conservare
palette nero caldo + oro/ambra; titoli Spectral; portali illustrati; animazioni lente (respiro, deriva, scintillio, impulso dei nodi); linguetta di Miss Minutes; mappa 3B e relative nature degli universi; distinzione schermo/fumetti nelle entità; tutti gli ID e i collegamenti esistenti.

## Debolezze da migliorare
schede personaggio senza ritratto (solo 8 avatar generici); dossier come elenco di righe chiave/valore; poche gerarchie visive (molti rettangoli scuri uguali); ricerca e filtri poco immediati; categorie senza identità cromatica propria; relazioni raggiungibili solo da tab; poca integrazione tra personaggi, universi, eventi e Miss Minutes; progressione dell'esplorazione assente.

## Cosa fa la Revisione 2
Parte dalla stessa shell e dagli stessi asset; aggiunge immagine a tutta altezza, accento cromatico per sala, dossier a sezioni con ritratto, mappa e Nexus manipolabili (dati reali dei nodi), ricerca per tipo, collezioni illustrate, progressione onesta. Fonte: `docs/atlante2/revisione2/` (generatore + sorgente HTML + immagini). Le immagini sono **dimostrative** (illustrazioni dell'app e avatar-archetipo), non ritratti finali.
