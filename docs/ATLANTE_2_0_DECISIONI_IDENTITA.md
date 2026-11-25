# Atlante 2.0 — Le 13 decisioni sulle identità dei personaggi

> Branch `test/tva-archives` · 25/11/2026 · **Solo proposta. Nessuna unificazione eseguita, nessun id modificato, nessuna relazione canonica creata.**
> **Risposta dell'utente del 25/11/2026 registrata nella sezione «Esito delle decisioni» in fondo.** Nessuna unificazione ancora eseguita.
> Base: `docs/CANDIDATI_IDENTITA_D3.md`, dati reali delle schede (`index.html`, build `20261125-0100-mm6`), identità già dichiarate in `atlasData.identita` e verifiche esterne dove indicate.

## Come leggere le schede

- **Modello adottato (non distruttivo):** *Identità* = individuo (o mantello) canonico; *Incarnazione/Variante* = sua versione in una continuità o con un altro interprete; *Alias/Redirect* = vecchia pagina che resta valida e apre l'identità. **Nessun id viene eliminato**: `char-…` esistenti restano apribili, preferiti/Tessera/Variant ID/Miss Minutes non si rompono.
- **«Collegamenti entranti»** = link `mvNavigate` da altre schede (in) · archi del grafo Relazioni (grafo) — misurati nel codice.
- **Fonti:** `interna` = schede/atlasData dell'app; `esterna` = fonte consultata il 25/11/2026 (link in fondo); *«da verificare in A2»* = va controllata su Marvel.com / Marvel Database / TMDB prima di applicare. **Non ho copiato testi**: le fonti servono a stabilire i fatti.
- **Tipi di esito:** **U** unire in un'identità (con alias) · **V** variante/incarnazione della stessa identità · **R** relazione tra identità distinte · **D** persone distinte, nessuna relazione di identità.

---

## 1. Peter (5 pagine + `char-spider-man`)
- **Schede:** `char-peter` (N°117), `char-peter-b-parker`, `char-peter-parker` (14 apparizioni), `char-peter-parker-holland-maguire-garfield` (N°… No Way Home), `char-peter-quill-star-lord`; correlata già dichiarata: `char-spider-man`.
- **Universo/continuità:** `peter`: MCU + Fox-Verse (Deadpool & Wolverine; correlati Sabretooth, Wolverine, Gambit: **non è Spider-Man**) · `peter-b-parker`: animato Sony, non canonico MCU · `peter-parker`: pagina **multi-continuità** (Raimi-Verse, Garfield-Verse, MCU, Your Friendly Neighborhood Spider-Man) · aggregata «Holland/Maguire/Garfield»: MCU + Raimi + Garfield · Quill: MCU.
- **Problema:** due pagine «contenitore» mescolano più individui di continuità diverse; `peter` e Quill hanno solo il nome di battesimo in comune; Peter B. Parker è una variante del Peter Parker animato.
- **Fonti:** interna — `atlasData.identita` **già verificata**: `peter-parker-mcu` (Holland: pagine peter-parker, aggregata, spider-man), `peter-parker-raimi` (Maguire), `peter-parker-garfield`, `peter-parker-ynfsm`.
- **Soluzione consigliata:** **U + V.** Creare 4 identità già dichiarate (MCU/Holland, Raimi/Maguire, Garfield, YNFSM) e un **hub «Peter Parker / Spider-Man»** che le raggruppa. `char-peter-parker` e l'aggregata diventano **pagine-hub con alias** (mostrano le 3–4 incarnazioni, senza testo duplicato). `char-spider-man` resta redirect a Peter Parker MCU (come già dichiarato). **D** per `peter` (Deadpool; rinomina visualizzata «Peter (Deadpool & Wolverine)» come alias) e per Quill. Peter B. Parker = **V** (variante animata) dell'hub, non unificato con nessun Parker live-action.
- **Conseguenze sui collegamenti:** `char-peter-parker` ha **16 link entranti** (da Vulture, Lizard, Venom, Sandman, MJ, Mary Jane, Electro, Ned, Norman/Harry Osborn, Doc Ock, Mysterio, Spider-Man…) e 19 archi: restano validi (alias), ma **ogni link va classificato per continuità** (es. Sandman→Raimi, Mysterio→MCU) in A2: operazione guidata da te sui casi ambigui. Tessera: poteri/livelli di `peter-parker`, aggregata, `peter-b-parker`, Quill invariati (chiavi per nome).

## 2. Charles Xavier (3 pagine)
- **Schede:** `char-charles-xavier`, `char-xavier`, `char-xavier-giovane-e-anziano`.
- **Universo/continuità:** Fox-Verse (Earth-10005). `Professor X Earth-838` (`char-professor-x-terra-838`) è un'altra identità (multiverso MCU).
- **Problema:** stesso individuo spezzato in tre pagine con interpreti diversi (McAvoy giovane, Stewart anziano); ordine delle timeline pre/post *Days of Future Past* non verificato.
- **Fonti:** interna — identità `charles-xavier` **«verificata»** nella guida; copertura sovrapposta N°018.
- **Soluzione consigliata:** **U.** Un'identità «Charles Xavier (Fox-Verse)» con due incarnazioni (giovane/McAvoy, anziano/Stewart); le 3 pagine diventano alias/redirect. Earth-838 resta distinta (relazione «variante di»).
- **Conseguenze:** link entranti 2 + 8 + 4 (grafo 8/12/5) → tutti confluiscono nell'identità; nessun link rotto; il campo «stesso individuo» sparisce dalle note. Tessera: `charles-xavier` ha poteri/livelli, le altre due no → si usa quella dell'identità.

## 3. Coulson (3 pagine)
- **Schede:** `char-coulson`, `char-coulson-lmd`, `char-phil-coulson`.
- **Universo/continuità:** MCU in tutti e tre (film/One-Shot + *Agents of S.H.I.E.L.D.*).
- **Problema:** `coulson` e `phil-coulson` sono con ogni probabilità lo stesso Phil Coulson (le correlate coincidono: May, Daisy, Ward); l'LMD è una copia robotica.
- **Fonti:** interna (stesso universo, correlati in comune); *da verificare in A2* su Marvel Database.
- **Soluzione consigliata:** **U** `coulson` + `phil-coulson` in un'identità «Phil Coulson»; **V** per `coulson-lmd` (Life Model Decoy: personaggio con coscienza propria, quindi identità distinta collegata con relazione «copia/replica di»).
- **Conseguenze:** link entranti 6 + 3 (+1 per LMD); alias per `char-coulson` e `char-phil-coulson`; la riga «prima apparizione» sarà la più antica tra le due (un'opzione da controllare: One-Shot).

## 4. Groot (2 pagine)
- **Schede:** `char-groot`, `char-groot-piccolo` (*I Am Groot*).
- **Universo:** MCU.
- **Problema:** Baby Groot è lo stesso personaggio?
- **Fonti:** esterna — il regista James Gunn ha dichiarato più volte che Baby Groot **non è** il Groot originale ma un personaggio diverso, senza i suoi ricordi, e «suo figlio»; nei film non lo si dice esplicitamente (v. fonti [G1–G3]).
- **Soluzione consigliata:** **R, non U.** Due identità: «Groot (originale, morto in *Guardians of the Galaxy*)» e «Groot (successore/Baby Groot)», con relazione «discendente di (dichiarazione del regista, non esplicita nei film)» e campo `verifica: dichiarazione d'autore`. La pagina `char-groot` oggi mescola entrambi (apparizioni dal 2014 a *Endgame*): va **separata per apparizione** (A2), `char-groot-piccolo` resta alla versione giovane/*I Am Groot*.
- **Conseguenze:** link entranti 4 + 0; i 4 link verso `char-groot` verranno rivisti uno per uno (Quill, Gamora, Drax, Rocket). Nessun id rimosso.

## 5. Sam Wilson / Steve Rogers «Capitan America»
- **Schede:** `char-sam-wilson-capitan-america`, `char-steve-rogers-capitan-america`.
- **Universo:** MCU (Steve anche Earth-199999/multiversale).
- **Problema:** appaiono come candidati solo per l'alias «Capitan America».
- **Fonti:** interna (interpreti diversi: Mackie / Evans; titoli in parte in comune).
- **Soluzione consigliata:** **D** (due persone) + nuova entità **«Capitan America (mantello)»** che elenca i titolari in ordine (Steve Rogers, Sam Wilson, …). Nessuna unione.
- **Conseguenze:** nessun link cambia; si aggiungono due archi «ha ereditato il mantello» tipizzati.

## 6. Ross (4 pagine)
- **Schede:** `char-everett-ross`, `char-generale-ross`, `char-generale-thaddeus-ross`, `char-thaddeus-ross`.
- **Universo/continuità:** Everett: MCU (*Secret Invasion*) · «generale Ross»: MCU (*L'incredibile Hulk*) · «Thaddeus Ross»: MCU (*Brave New World*) · «generale Thaddeus Ross»: **Legacy/Universal** (*Hulk* 2003, isolato).
- **Problema:** quattro pagine, tre persone.
- **Fonti:** esterna — Thaddeus «Thunderbolt» Ross è lo stesso personaggio interpretato da William Hurt e poi da Harrison Ford dopo la morte di Hurt (2022) [R1]; Everett Ross è un altro personaggio; Ross di *Hulk* 2003 è un'altra continuità (interna).
- **Soluzione consigliata:** **U** `char-generale-ross` + `char-thaddeus-ross` → «Thaddeus Ross (MCU)» con 2 interpreti (Hurt, Ford) come incarnazioni; **D** per Everett Ross; **D** (continuità diversa) per `char-generale-thaddeus-ross` (Hulk 2003), collegato come «controparte in altra continuità».
- **Conseguenze:** link entranti 1 + 1 (+3 sulla versione Legacy, invariati); le correlate di Betty Ross restano valide.

## 7. Ghost / Ghost Rider (3 pagine)
- **Schede:** `char-ghost`, `char-johnny-blaze-ghost-rider`, `char-robbie-reyes-ghost-rider`.
- **Universo:** Ghost: MCU (*Ant-Man and the Wasp*, Ava Starr) · Johnny Blaze: Legacy/Columbia-Sony (Nicolas Cage) · Robbie Reyes: MCU (*S.H.I.E.L.D.*).
- **Problema:** confronto solo per parola «Ghost»; titoli e universi diversi.
- **Fonti:** interna.
- **Soluzione consigliata:** **D** per tutte e tre. Per i due Ghost Rider: nuova entità **«Ghost Rider (mantello/Spirito della Vendetta)»** con titolari Johnny Blaze e Robbie Reyes (relazione «stesso mantello, continuità diverse»).
- **Conseguenze:** nessun link cambia.

## 8. Mary Jane (3 pagine)
- **Schede:** `char-mary-jane`, `char-mary-jane-watson`, `char-mj`.
- **Universo:** `mary-jane` e `mary-jane-watson`: Earth-96283 (Raimi-Verse) · `mj`: MCU (*Far From Home*, *Brand New Day*).
- **Problema:** `mary-jane` (SM2/SM3) e `mary-jane-watson` (SM1) sono lo stesso personaggio spezzato per film; `mj` è altra persona.
- **Fonti:** interna (universo identico, correlati in comune); documento `REPORT_relazioni_alberi_arti.md` già segnalava il duplicato; *da verificare in A2* su Marvel.com.
- **Soluzione consigliata:** **U** `mary-jane` + `mary-jane-watson` → «Mary Jane Watson (Raimi-Verse)» (Kirsten Dunst); **D** per `mj` MCU (personaggio diverso, collegato come «controparte in altra continuità»).
- **Conseguenze:** link entranti 5 + 3 → alias; sia Peter Parker sia i Goblin la citano (da riassegnare alla giusta continuità, vedi decisione 1).

## 9. Bishop / Kate Bishop (2 pagine)
- **Schede:** `char-bishop`, `char-kate-bishop`.
- **Universo:** Bishop: Fox-Verse (*Days of Future Past*) · Kate Bishop: MCU (*Hawkeye*).
- **Problema:** solo il cognome in comune.
- **Fonti:** interna (universi e correlati diversi).
- **Soluzione consigliata:** **D** (persone distinte). Nessuna relazione di identità; eventuale disambiguazione di titolo («Bishop (X-Men)» come alias di ricerca).
- **Conseguenze:** nessuna.

## 10. Janet / Janet van Dyne (2 pagine)
- **Schede:** `char-janet`, `char-janet-van-dyne`.
- **Universo:** `janet`: Legacy, Sony Pictures TV/Prime Video/MGM+, isolato (*Spider-Noir*, N°039) · Janet van Dyne: MCU.
- **Problema:** stesso nome proprio, serie e universi diversi.
- **Fonti:** interna.
- **Soluzione consigliata:** **D.** Titolo di visualizzazione «Janet (Spider-Noir)» come alias.
- **Conseguenze:** nessuna (correlati diversi: Ben Reilly/The Spider vs Scott Lang/Hope).

## 11. Kingpin (Spider-Verse) / Wilson Fisk (2 pagine)
- **Schede:** `char-kingpin`, `char-wilson-fisk-kingpin`.
- **Universo:** Kingpin: animato Sony, non canonico MCU · Wilson Fisk: **tre continuità nella stessa pagina** — Legacy/20th Century Fox (*Daredevil* 2003), MCU Netflix, MCU (*Hawkeye*).
- **Problema:** il Kingpin animato è una variante di Fisk (non lo stesso individuo); la pagina Fisk contiene più incarnazioni (interpreti diversi) senza separazione.
- **Fonti:** interna; *da verificare in A2* l'assegnazione degli interpreti per continuità su Marvel Database/TMDB.
- **Soluzione consigliata:** **V + R.** Identità «Wilson Fisk» con incarnazioni per continuità (Legacy/Fox · MCU Netflix/MCU) — la pagina `char-wilson-fisk-kingpin` resta l'hub; `char-kingpin` = incarnazione animata, collegata con «variante di».
- **Conseguenze:** Fisk ha **10 link entranti** e 14 archi, da riclassificare per continuità in A2 (Daredevil, Elektra, Bullseye, Kate Bishop…).

## 12. Miles Morales / «Miles Morales e altri» (2 pagine)
- **Schede:** `char-miles-morales`, `char-miles-morales-e-altri`.
- **Universo:** animato Sony (Spider-Verse); la seconda = *Spider-Man: Beyond the Spider-Verse*.
- **Problema:** la seconda è una voce aggregata/segnaposto di un film, senza correlati né apparizioni verificate (grafo: 1 arco).
- **Fonti:** interna; stato del film e cast *da verificare in A2* su Marvel.com/TMDB.
- **Soluzione consigliata:** **V.** Non unire: trasformare «e altri» in elenco *cast di titolo* collegato a Miles Morales (Earth-1610) e ai personaggi effettivamente confermati; fino alla verifica resta segnaposto «da verificare».
- **Conseguenze:** nessun link entrante, quindi nessun impatto.

## 13. Ravonna Renslayer / Renslayer (2 pagine)
- **Schede:** `char-ravonna-renslayer` (Loki S1), `char-renslayer` (Loki S2).
- **Universo:** MCU/TVA, stessi correlati (Loki, Mobius, Sylvie).
- **Problema:** stessa persona divisa per stagione.
- **Fonti:** esterna — la serie presenta lo stesso personaggio (Gugu Mbatha-Raw) con il nome «Renslayer» anche nella S2 [R2–R3]; interna: stessi correlati e universo.
- **Soluzione consigliata:** **U** → «Ravonna Renslayer» con alias `char-renslayer`; apparizioni S1 e S2 sommate.
- **Conseguenze:** link entranti 3 + 1 → alias; nessun link rotto.

---

## Riepilogo e cosa serve da te

| # | Gruppo | Esito proposto |
|---|---|---|
| 1 | Peter | U/V: 4 identità dichiarate + hub; `peter` e Quill D; Peter B. Parker V |
| 2 | Charles Xavier | U (3 pagine → 1 identità, 2 incarnazioni) |
| 3 | Coulson | U (Coulson + Phil Coulson); LMD identità collegata |
| 4 | Groot | R (originale e successore separati, dichiarazione del regista) |
| 5 | Capitan America | D + entità «mantello» |
| 6 | Ross | U (Ross MCU, 2 interpreti); Everett D; Hulk 2003 D |
| 7 | Ghost / Ghost Rider | D ×3 + «mantello Ghost Rider» |
| 8 | Mary Jane | U (le due Raimi); MJ MCU D |
| 9 | Bishop | D |
| 10 | Janet | D |
| 11 | Kingpin / Fisk | V + R |
| 12 | Miles Morales | V (segnaposto «e altri» da verificare) |
| 13 | Ravonna | U |

**Per ciascuna ti chiedo:** *approvo*, *modifico* (indica l'esito) o *rimando*. I casi 1, 4, 6 e 11 incidono sul maggior numero di link e richiedono la classificazione per continuità link per link.

## Cosa NON è stato fatto
Nessuna unione, nessun redirect, nessun id cambiato, nessun dato dell'utente toccato.

## Fonti esterne consultate (25/11/2026)
- [G1] GamesRadar, «Baby Groot isn't the original Groot…» (SFX, 2017) — https://www.gamesradar.com/uk/guardians-of-the-galaxy-2s-baby-groot-isnt-the-original-groot-but-a-new-groot-confused-so-are-groot
- [G2] Game Informer, «Gunn confirms Baby Groot is Groot's son» (2018) — https://gameinformer.com/b/news/archive/2018/02/27/guardians-of-the-galaxy-director-confirms-baby-groot-is-groots-son-again.aspx
- [G3] CinemaBlend, «James Gunn cleared up a misconception about Baby Groot» — https://cinemablend.com/news/2317851/james-gunn-just-cleared-up-a-misconception-about-baby-groot
- [R1] Wikipedia, «Thaddeus Ross (Marvel Cinematic Universe)» — https://en.wikipedia.org/wiki/Thaddeus_Ross_(Marvel_Cinematic_Universe)
- [R2] Den of Geek, «Loki Season 2: Who Is Ravonna Renslayer…» — https://www.denofgeek.com/tv/loki-season-2-who-is-ravonna-renslayer-and-whats-her-relationship-with-kang/
- [R3] GamesRadar, «Ravonna Lexus Renslayer: …» — https://www.gamesradar.com/ravonna-lexus-renslayer-loki-tva-time-variance-authority-marvel

*Le fonti sono testate e articoli di cronaca, non Marvel.com/Marvel Database: per i dati di scheda si useranno queste ultime (e TMDB) in A2, con testi originali.*


---

## Esito delle decisioni (risposta dell'utente, 25/11/2026 01:01)

*Tutte le decisioni sono **subordinate alla verifica delle fonti e alla conservazione dei collegamenti esistenti**. Stato attuale: **approvate/modificate/rimandate, nessuna applicata al database.***

| # | Gruppo | Esito | Precisazione dell'utente |
|---|---|---|---|
| 1 | Peter Parker | **MODIFICATA** | **Hub multiversale** che raggruppa identità autonome (biografia, poteri, apparizioni, relazioni e continuità indipendenti per ciascuna); prevedere anche **Terra-616 dei fumetti**; **l'hub non è conteggiato come personaggio**. |
| 2 | Charles Xavier | **MODIFICATA** | Giovane e anziano nella stessa identità **solo se la continuità narrativa lo giustifica**; versioni di universi o linee temporali diversi restano distinguibili. |
| 3 | Coulson | APPROVATA | LMD collegato ma distinguibile dall'originale. |
| 4 | Groot | APPROVATA | Originale e Baby Groot personaggi distinti, con relazione familiare. |
| 5 | Capitan America | APPROVATA | Concetto generale di **mantello**, riutilizzabile (Spider-Man, Thor, Black Panther, Ghost Rider, altri). |
| 6 | Ross | APPROVATA | Il cambio di attore **non è automaticamente una variante**. |
| 7 | Ghost / Ghost Rider | APPROVATA | — |
| 8 | Mary Jane | APPROVATA | — |
| 9 | Bishop | **RIMANDATA** | Fino alla verifica delle identità coinvolte. |
| 10 | Janet | **RIMANDATA** | Fino alla verifica delle identità coinvolte. |
| 11 | Kingpin | **MODIFICATA** | **Hub Wilson Fisk** con identità autonome per continuità; **non mescolare** fumetti, MCU, animazione e altre versioni. |
| 12 | Miles Morales | APPROVATA | I **segnaposto non si contano** come personaggi effettivi. |
| 13 | Ravonna | APPROVATA | — |

**Da fare in A2 (dopo verifica fonti):** gruppi 1, 11 (hub), 2 (verifica continuità), 3–8, 12, 13; **9 e 10 restano sospesi** (verifica di `char-bishop`, `char-kate-bishop`, `char-janet`, `char-janet-van-dyne` con Marvel.com/Marvel Database/TMDB prima di riproporli).
