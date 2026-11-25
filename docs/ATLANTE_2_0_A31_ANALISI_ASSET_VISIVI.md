# Atlante 2.0 — A3.1 Atlante Visual Assets: analisi delle fonti (solo analisi, nessuna implementazione)

Data: 25/11/2026. Stato: **in attesa di decisione**. A4 non avviata; produzione, Miss Minutes e dati personali non toccati.
Limite di verifica: dalla sandbox le fonti non sono raggiungibili direttamente (rete bloccata); le condizioni d'uso sono state lette tramite ricerca web (pagine ufficiali TMDB, Fandom, Wikipedia/Commons, Library of Congress per i contatti Marvel). I Termini di Marvel.com non sono stati aperti nel testo integrale: vanno letti prima di qualsiasi uso.

## 1. Fonti e condizioni reali

| Fonte | Cosa offre | Condizioni verificate | Uso per i ritratti |
|---|---|---|---|
| **TMDB** (già nel progetto) | Locandine, backdrop, loghi dei titoli; foto degli **attori** | API gratuita solo per uso **non commerciale** con attribuzione (testo «This product uses the TMDB API but is not endorsed or certified by TMDB», logo approvato in «Crediti»); uso commerciale = licenza separata; immagini dal CDN `image.tmdb.org` | **Titoli sì, personaggi no.** Nessun ritratto di personaggio; le foto attore sono escluse dalla tua regola |
| **Marvel.com / Marvel Comics API** | Ritratti ufficiali dei fumetti | Contenuti © Marvel, diritti riservati; l'API per sviluppatori risulta **ritirata** (portale reindirizzato, gateway non funzionante); permessi solo da Marvel Rights & Permissions | **Non utilizzabile** senza permesso scritto; nessun accesso tecnico legittimo |
| **Marvel Database (Fandom)** | Molte immagini | Solo il **testo** è CC BY-SA; le immagini **non** lo sono (fair use, restano di terzi) | **Non riutilizzabile** |
| **Wikipedia** | Copertine e figure dei personaggi | In gran parte «non free», fair use valido **solo su Wikipedia** | **Non riutilizzabile** fuori da Wikipedia |
| **Wikimedia Commons** | Solo materiale libero | Niente copertine Marvel moderne; restano opere d'epoca di pubblico dominio (non rinnovate) caso per caso e foto di cosplay/eventi | Copertura trascurabile, status da verificare file per file |
| **Altre gratuite** (Comic Vine, API non ufficiali) | Immagini caricate dagli utenti | Diritti non garantiti | Escluse (dipendenza non autorizzata) |
| **Produzione propria** | Illustrazioni originali (copertine di sezione, 8 avatar archetipici) | Nostre; ma personaggi e fattezze restano diritto/marchio Marvel: un disegno che li **raffigura** è un derivato non autorizzato | Legittime solo se **non raffigurano** il personaggio |

**Conclusione:** tra le fonti gratuite non esiste un canale legittimo per ritratti specifici dei personaggi Marvel. «Ritratto specifico, quando disponibile e legittimo» oggi vale **0 ritratti ufficiali**.

## 2. Copertura realmente ottenibile (misurata sul registro)

295 identità; 431 voci (27 universi, 17 organizzazioni, 16 artefatti, 9 luoghi, 7 pianeti, 7 eventi/battaglie, 49 attori, 2 hub, 2 mantelli).

| Livello | Cosa mostra | Copertura | Diritti |
|---|---|---|---|
| **L1 – Ritratto ufficiale** | Il personaggio | **0 %** | Serve permesso Marvel/Disney |
| **L2 – Locandina del titolo (TMDB)** | Poster del primo titolo in cui appare | **282/295 identità (96 %)**; 13 senza | Autorizzato con attribuzione (non commerciale) |
| **L3 – Illustrazione originale archetipica** | Soggetto derivato dai poteri dichiarati, colore = continuità | **100 %** | Originale, nessun diritto di terzi sul soggetto |
| **L4 – Scena del titolo (backdrop TMDB)** | Scena scelta a mano per identità | Solo con verifica visiva titolo per titolo; non stimabile da qui | Come L2, ma serve verificare che il personaggio compaia |
| **Non-personaggi** | L2 per eventi/luoghi legati a titoli; L3 simbolico per il resto | L3 100 %; L2 parziale | Come sopra |

Specie, entità cosmiche e arti mistiche non sono tipologie distinte nel registro (sono personaggi con sottotipo): vanno modellate come categoria dell'asset.

**«100 % di ritratti» è raggiungibile solo a livello L3 (illustrazione archetipica), non come ritratto del personaggio.** Il 100 % di ritratti ufficiali non è ottenibile gratis né legittimamente.

## 3. Anteprima (21 identità)
`docs/atlante2/a31/anteprima.html` (generatore `gen_preview.py`; locandine TMDB visibili solo con rete): MCU (Iron Man, Thor, Wanda, Loki, Hela, Groot, Peter MCU), Sony (Peter Raimi/Garfield, Venom, Morbius, Ghost Rider), animazione (Miles, Peter B., A-Bomb), Fox (Xavier, Wolverine, Magneto, Deadpool, Jean Grey, Johnny Storm). Nel registro non esiste alcuna identità solo-fumetto (nessuna continuità Terra-616, solo segnaposto): i fumetti compaiono nei campi testuali.

**Difetto mostrato apertamente:** con 8 archetipi di base, identità diverse condividono lo stesso soggetto (Iron Man e Thor sono quasi uguali, solo ritagliati e ricolorati). L3 garantisce unicità di file e di continuità, non di soggetto: se la tua regola «non usare la stessa immagine per varianti differenti» va intesa come unicità visiva, serve un set molto più ampio di soggetti originali.

## 4. Architettura proposta (dopo la tua scelta)
- **Registro asset** `data/atlante/assets.json`: `asset_id`, `entita` (id identità/voce), `continuita`, `livello` (L1–L4), `fonte`, `url_origine`, `autore/attribuzione`, `licenza_o_condizioni`, `verifica` (non verificato · verificato · rifiutato, con data e verificatore), `larghezza×altezza`, `sha256`, `formato`. Un asset appartiene a **una** identità+continuità; il generatore rifiuta lo stesso `sha256` su due identità.
- File locali WebP verticali 3:4 (360×480 e 720×960, circa 25–70 KB), caricamento lazy con IntersectionObserver, `srcset`, segnaposto sfocato, cache dal service worker, fallback all'emblema.
- Locandine TMDB solo via CDN (CSP già consentita), mai copiate; attribuzione nei Crediti.
- Costo 0 €, nessuna dipendenza non autorizzata.

## 5. Decisioni richieste
1. **Linea dei ritratti:** (A) L2+L3, dichiarati non-ritratti; (B) richiesta di permesso scritto a Marvel/Disney, con A come ripiego (esito incerto, probabile rifiuto o licenza a pagamento); (C) fornisci tu immagini di cui hai i diritti, da registrare con provenienza.
2. **Unicità visiva:** produrre un grande set di soggetti originali (L3 esteso) o accettare l'archetipo condiviso con colore/continuità distinti?
3. **Foto degli attori:** confermi l'esclusione totale?
4. **TMDB:** confermi che l'app resta non commerciale?
5. **L4** (backdrop scelti a mano) solo per le identità principali, dopo verifica visiva?

Nessuna implementazione avviata finché non scegli.
