# Atlante 2.0 — Fase A2: Identità, varianti e incarnazioni (report)

> 25/11/2026 · branch `test/tva-archives` · **solo livello registro: nessuna modifica a `index.html`, `sw.js`, Miss Minutes, Tessera, XP, preferiti, classifiche, interfaccia.** Strato aggiunto: `data/atlante/identita.json` (generato da `tools/atlante_identita.py`, verificabile con `--verifica`).
> Le 304 schede `char-*` e i loro ID restano **intatti** (`personaggi.json` = estrazione A1 identica alla baseline). Ogni scheda ha una voce in `redirect` con ruolo: `canonica | alias | pagina-hub | pagina-storica | segnaposto | sospesa`.

## 1. Identità prima e dopo
| | Prima (A0) | Dopo (A2, strato registro) |
|---|---|---|
| Pagine `char-*` | 304 (300 «contano», 4 segnaposto) | 304 (invariate, tutte raggiungibili) |
| Identità che contano come personaggio | 300 pagine | **295 identità** |
| Hub multiversali (non contati) | 0 | **2** (Peter Parker, Wilson Fisk) |
| Mantelli (non contati) | 0 | **2** (Capitan America, Ghost Rider) |
| Segnaposto (non contati) | 4 | **7** (4 già esistenti + «Miles Morales e altri» + Terra-616 di Peter e di Fisk, senza dati) |
| Relazioni narrative tipizzate create | 0 | **5** (Groot discendente, Coulson LMD copia, Sam erede del mantello, Ross Hulk 2003 controparte, Xavier Terra-838 controparte); **2 non narrative** (MJ «ispirato a», segnaposto Miles) |

Aritmetica: 300 − 6 (unificazioni) + 1 (Peter: 3 pagine → 4 identità) + 1 (Fisk: 1 pagina → 2 identità) − 1 (Miles «e altri» → segnaposto) = **295**.

## 2. Unificazioni effettuate (solo nel registro; le pagine restano come alias)
| Identità | Pagine unite | Motivo |
|---|---|---|
| Phil Coulson | `char-phil-coulson`, `char-coulson` | stesso personaggio e interprete (Clark Gregg) |
| Charles Xavier (Fox-Verse) | `char-charles-xavier`, `char-xavier`, `char-xavier-giovane-e-anziano` | Days of Future Past li mostra come lo stesso individuo in due fasi; cambio di interprete = incarnazione |
| Thaddeus Ross (MCU) | `char-thaddeus-ross`, `char-generale-ross` | stesso personaggio, Hurt → Ford (cambio di attore, **non** variante) |
| Mary Jane Watson (Raimi) | `char-mary-jane-watson`, `char-mary-jane` | stessa Kirsten Dunst, stessa continuità, pagine divise per film |
| Ravonna Renslayer | `char-ravonna-renslayer`, `char-renslayer` | stessa persona e interprete in Loki S1/S2 |
**Non unificati** (persone distinte): Steve/Sam, Johnny Blaze/Robbie Reyes/Ghost, Everett/Thaddeus Ross/Ross di Hulk 2003, MJ (Michelle Jones-Watson)/Mary Jane, Peter (Deadpool)/Peter Quill/Peter Parker, Coulson/Coulson LMD, Groot originale/successore, Xavier Fox/Terra-838.

## 3. Varianti, incarnazioni, hub, mantelli
- **Hub Peter Parker** (non contato): Terra-616 (segnaposto), MCU (Holland), Raimi (Maguire), Garfield, Your Friendly Neighborhood Spider-Man, Peter B. Parker (variante animata) = **6 membri dichiarati = 6 elencati**; fuori hub `char-peter` e Quill. `char-peter-parker` e l'aggregata diventano «pagine-hub»; `char-spider-man` alias di Peter MCU. Apparizioni di `char-peter-parker` ripartite **dai dati di `mvMapData`**: MCU 067·075·084·089·090·099·132 · Raimi 001·002·003·099 · Garfield 004·005·099 · YNFSM 120·134 (099 è condivisa, come dichiarato dall'universo).
- **Hub Wilson Fisk** (non contato): Fox 2003 (Duncan, N°035) · MCU ex Netflix (D'Onofrio, N°060·082·100·116·122·128) · Kingpin Spider-Verse (Schreiber, variante animata) · Terra-616 (segnaposto). Nessun testo mescolato.
- **Incarnazioni:** Xavier giovane (McAvoy) / anziano (Stewart); Ross Hurt / Ford (tipo `cambio_attore`); Groot «piccolo» (etichetta della scheda, da verificare).
- **Copia artificiale:** Coulson (LMD) identità distinta, relazione «copia di».
- **Groot:** originale (N°058) e successore (059·084·089·115), relazione «discendente di» marcata *dichiarazione d'autore*.
- **Mantelli:** Capitan America (Steve → Sam), Ghost Rider (Johnny Blaze, Robbie Reyes; per continuità). Il tipo `mantello` è riutilizzabile (Spider-Man, Thor, Black Panther) ma **non sono state create istanze senza dati**.

## 4. Alias e collegamenti conservati
Tutti i 304 ID restano; **0 link `mvNavigate` rotti (1.065)**; `html_sha256`, blob e id baseline A0 identici. Link entranti verso pagine divise: **76** (Peter Parker 35, Wilson Fisk 24, Groot 11, aggregata Peter 6) → **44 con proposta automatica** (la continuità della scheda sorgente corrisponde a una sola identità), **32 «da decidere»** (continuità ambigua). Nessun link è stato riscritto: la classificazione definitiva è un passo dell'interfaccia (A3) che richiede la tua conferma sui 32 casi.

## 5. Fonti usate (consultate il 25/11/2026; testi non copiati)
Interne: `atlasData.identita`, `mvMapData`, schede del registro. Esterne: Wikipedia — Phil Coulson, MJ (MCU), Mary Jane Watson (Raimi), Thaddeus Ross (MCU), Charles Xavier (film), Professor X in other media, Kingpin; Marvel.com — «YDK Agents of S.H.I.E.L.D. and LMDs»; Syfy Wire — D'Onofrio su Kingpin; GamesRadar e Game Informer — Gunn su Baby Groot; Den of Geek — Ravonna; Rolling Stone — Ghost Rider. **Onestà:** le pagine di Marvel Database e le schede Marvel.com/TMDB dei singoli personaggi **non sono state consultate una per una**; il livello `verifica` è «verificata (fonti secondarie affidabili + dati interni)» e va completato in A7 con le fonti primarie.

## 6. Incongruenze ancora aperte
Xavier: ordine delle timeline pre/post DOFP · Coulson: N°091 su `char-coulson` (S6) da verificare · Groot: originale/successore è dichiarazione d'autore · Professor X Terra-838: di quale identità sia variante · Peter B. Parker e Kingpin animato: nessuna relazione di variante verso un'identità specifica · Terra-616: segnaposto senza dati · 32 link da decidere · Bishop e Janet sospese · Interpreti non registrati (YNFSM, Groot, Steve/Sam…) non inseriti. 

## 7. Controlli essenziali
- `python3 tools/atlante_identita.py --verifica`: **tutti PASS** (redirect per tutte le 304 pagine, hub/mantelli/segnaposto non contati, relazioni senza co-apparizioni, apparizioni ⊆ pagine, Bishop/Janet senza relazioni, nessuna unificazione di persone distinte, baseline A0/Tessera/blob Miss Minutes invariati).
- `python3 tools/atlante_estrai.py --verifica` (A1): **tutti PASS**.
- Suite UI non rieseguite: nessun file di runtime è cambiato. I FAIL/BLOCKED della baseline A0 restano documentati in `tests/KNOWN_FAILS.json` e non sono stati toccati né aggirati.
