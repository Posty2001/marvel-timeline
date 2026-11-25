# Atlante 2.0 — Modello generale delle identità (approvato nei principi, 25/11/2026)

> Solo specifica. Applicabile a **tutto** il database futuro, non solo ai 13 casi. Nessun codice, nessuna modifica ai dati. Subordinato alla verifica delle fonti e alla conservazione di ID e collegamenti esistenti.

## 1. Tipi di entità/identità

| Tipo | Significato | Conta come personaggio? | Esempio |
|---|---|---|---|
| **Identità individuale** | Una persona/entità narrativa in una continuità, con biografia propria | **Sì** | Loki (MCU) |
| **Variante multiversale** | Versione della stessa persona in altro universo/linea temporale, con dati autonomi | **Sì** (identità propria, collegata) | Peter B. Parker rispetto a Peter Parker |
| **Incarnazione** | Stessa persona, stessa continuità, fase/età/aspetto diversi (se la continuità lo giustifica) | No (è una *vista* dell'identità) | Xavier giovane/anziano nella stessa linea temporale |
| **Mantello** | Ruolo/titolo ereditabile da persone diverse | **No** | Capitan America, Spider-Man, Thor, Black Panther, Ghost Rider |
| **Alias / soprannome** | Altro nome della stessa identità; apre l'identità canonica | No | «MJ» come ricerca per Mary Jane |
| **Hub multiversale** | Raggruppatore di identità autonome dello stesso archetipo | **No** (esplicito) | Peter Parker, Wilson Fisk |
| **Relazione familiare** | Legame tipizzato e orientato tra identità | — | Groot → Baby Groot (figlio) |
| **Clone / copia / duplicato artificiale** | Replica con identità narrativa propria o parziale (LMD, cloni, androidi) | Sì se ha coscienza/narrazione propria; altrimenti no | Coulson LMD |
| **Cambio di attore** | Stesso personaggio, interprete diverso | No variante | Thaddeus Ross (Hurt → Ford) |
| **Segnaposto** | Voce non verificata o aggregata | **No** (mai nei conteggi) | «Miles Morales e altri» |

**Regole fondanti**
1. **Un'identità = una scheda.** Un'entità può avere più `categorie[]` (es. personaggio + entità cosmica) **senza schede duplicate**.
2. **Hub ≠ personaggio:** non ha biografia propria, non compare nei conteggi «personaggi»; elenca le identità membre con la loro continuità.
3. **Continuità sempre esplicita:** ogni dato (biografia, poteri, apparizioni, relazioni) appartiene a **una** continuità (MCU/Terra-199999, Terra-616 fumetti, Raimi, Garfield, Fox, animazione Sony, ecc.). **Mai mescolare** fumetti, MCU, animazione e altre versioni in un campo.
4. **Cambio di attore ≠ variante.** Variante solo se la narrazione dichiara un individuo diverso/universo diverso.
5. **Incarnazioni nella stessa identità solo se la continuità lo giustifica**; universi o linee temporali diverse restano distinguibili (variante o identità separata collegata).
6. **Alias e redirect conservano gli ID esistenti** (`char-…` non vengono mai eliminati).
7. **Provenienza e verifica** su ogni dato: `fonte[]` e `verifica` ∈ {verificata, da verificare, ipotesi, voce}.

## 2. Relazioni

- **Relazioni narrative significative** (famiglia, mentore/allievo, alleanza, rivalità, successione di mantello, variante di, copia di, creato da, membro di…): tipizzate, **orientate** (con inverso esplicito), con `fonte` e `verifica`. Solo queste contano per l'obiettivo «10.000+ relazioni significative».
- **Co-apparizioni** (stesso titolo) e legami «stesso universo/attore»: **collegamenti di tipo separato**, derivati dalle apparizioni, **non conteggiati come relazioni narrative** (nel grafo attuale sono 1.522+692+106+98 su 2.454 archi). Nel Nexus sono disattivabili e disattivati di default.
- Dati sospetti oggi (es. «variante» Loki ↔ Jane Foster) restano marcati «da verificare» finché non confermati.

## 3. Campi per tipologia (schema estensibile, id stabili)
Personaggio/identità: identità, alias, biografia, origini, storia, poteri, debolezze, equipaggiamento, affiliazioni, relazioni, varianti/incarnazioni, apparizioni, eventi, riferimenti bibliografici, fonti, categorie[], continuità, verifica. Hub: archetipo, identità membre, note di disambiguazione. Mantello: titolari in ordine, continuità, origine del titolo. Altre tipologie (universo, evento, battaglia, organizzazione, artefatto, luogo/pianeta, specie/entità): campi dedicati, tutti con `fonte` e `verifica`.

## 4. Impatto sui 13 casi
Hub: **Peter Parker** (Terra-616, MCU/Holland, Raimi/Maguire, Garfield, Your Friendly Neighborhood Spider-Man, Peter B. Parker animato; `char-peter` Deadpool & Wolverine e Quill fuori dall'hub), **Wilson Fisk** (una identità per continuità). Mantelli: Capitan America, Ghost Rider, (riutilizzabile per Spider-Man, Thor, Black Panther…). Sospesi: Bishop, Janet.
