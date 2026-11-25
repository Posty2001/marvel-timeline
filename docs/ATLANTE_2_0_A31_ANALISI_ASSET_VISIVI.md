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

---

# Seconda valutazione (25/11/2026) — scene TMDB e illustrazioni AI

Fissati dalla tua risposta: niente archetipi condivisi/ricolorati né locandine come ritratti; ogni identità riconoscibile e distinta dalle varianti; progetto personale, gratuito, non commerciale; foto attori solo nelle schede interpreti. **Nessuna implementazione, A4 non avviata.** Limite di questa analisi: dalla sandbox non posso scaricare né vedere immagini TMDB; le stime di copertura sono quindi da misurare con un pilota.

## 6. Strada 1 — Scene TMDB scelte per personaggio

**Condizioni d'uso (verificate):**
- L'API TMDB è per uso non commerciale con attribuzione, ma TMDB non concede diritti sulle immagini: lo staff dichiara di non avere documenti di copyright o d'uso dei marchi per gli utenti API; il copyright resta degli studi (Marvel/Disney/Sony). Le immagini sono caricate dagli utenti e rimosse su notifica DMCA.
- Qualità: i backdrop includono duplicati, screencap a bassa qualità e immagini errate.
- Tecnicamente: `/movie|tv/{id}/images` (backdrop con lingua null) e `/person/{id}/tagged_images`, che è per **attore**, non per personaggio.

**Fattibilità tecnica:**
- Nessun tag per personaggio: la scelta per identità richiede **verifica visiva** (una scena in cui il personaggio è chiaramente riconoscibile, in quella continuità).
- Varianti con attori diversi (Peter Raimi/Garfield/MCU, Xavier Fox/MCU) sono separabili per titolo+attore; varianti con lo stesso attore nello stesso titolo (più Peter in *No Way Home*) o personaggi mascherati (Venom, Ghost Rider) richiedono selezione manuale.
- Formato: i backdrop sono orizzontali 16:9; il ritratto verticale 3:4 richiede ritaglio centrato sul volto/soggetto (rischio di tagli errati, da controllare a vista).
- Identità senza scena adatta: personaggi marginali, animazione con pochi still, eventi/luoghi/artefatti (spesso nessuna scena dedicata).

**Rischio giuridico:** si tratta di fotogrammi coperti da copyright dello studio. «Personale e non commerciale» riduce l'esposizione ma **non** crea una licenza, soprattutto se l'app è raggiungibile da un URL pubblico (Netlify). Hotlink via CDN TMDB (CSP già consentita) significa non ospitare i file; copiarli nel repository/ZIP equivale a distribuirli. Non è un parere legale.

**Copertura realistica:** non stimabile onestamente senza pilota. Ipotesi di lavoro da verificare: buona per i protagonisti MCU/Sony/Fox con titolo proprio, parziale per secondari e animazione, scarsa per non-personaggi.

**Costo:** 0 € (chiave TMDB gratuita; serve una chiave API tua e la tua autorizzazione).

## 7. Strada 2 — Illustrazioni generate con AI

**Giuridico:**
- Una raffigurazione AI di un personaggio Marvel è comunque una raffigurazione di un personaggio protetto: Disney e Universal hanno citato Midjourney proprio per immagini generate di personaggi (esempi: Iron Man, Deadpool e Wolverine), sostenendo che «piracy is piracy» anche se l'immagine è prodotta con l'AI. La causa riguarda gli output, il caso più vicino al tuo.
- L'uso personale non commerciale non elimina il rischio se le immagini sono pubblicate online. Non è un parere legale.
- Molti servizi online rifiutano o deformano personaggi con copyright (da verificare sul servizio scelto).

**Economico (0 €):**
- Il tier gratuito dell'API Gemini non include i modelli di immagine: risposta dello staff Google («not available for use on the Free Tier») ed errori `limit: 0`. Blog di terzi che parlano di 500 richieste al giorno gratuite contraddicono la documentazione e non sono verificati.
- A pagamento: circa 0,039 $ per immagine (2.5 Flash Image) e circa 0,067 $ per immagine 1K (3.1 Flash Image): ~12–20 $ per 295 identità a un solo tentativo, molto di più con i tentativi di scarto. **Viola la regola dei 0 € senza tua autorizzazione.**
- Generazione locale gratuita: possibile solo con una GPU adeguata sul tuo PC (hardware non noto) e modelli open con licenze da verificare; qualità sui personaggi Marvel specifici inferiore e meno controllabile.

**Tecnico:**
- Stile uniforme: richiede prompt/riferimento di stile fissi e controllo a vista di ogni immagine.
- Riconoscibilità: dipende da quanto il modello «conosce» ciascuna variante; varianti molto simili (tre Peter Parker) tendono a collassare in una sola; rischio di tratti errati.
- Non-personaggi (eventi, luoghi, artefatti): più facili da generare come illustrazioni originali.
- Titolarità: un output puramente AI ha tutela autorale debole o assente (non ancora verificato in questa analisi).

## 8. Confronto

| | Scene TMDB | Illustrazioni AI |
|---|---|---|
| Riconoscibilità | Alta (è il vero personaggio) | Variabile; varianti simili si confondono |
| Distinzione varianti | Buona (attore+titolo); manuale se stesso attore | Debole senza riferimenti |
| Uniformità | Bassa (scene eterogenee, crop) | Alta se lo stile è fissato |
| Rischio giuridico | Fotogrammi dello studio | Opere derivate di personaggi protetti |
| Costo | 0 € | 0 € solo in locale con GPU; altrimenti ~0,04–0,07 $/immagine |
| Lavoro | Selezione e ritaglio manuali | Prompt, rigenerazioni, controllo a vista |
| Non-personaggi | Scarso | Buono |

## 9. Architettura invariata (valida per entrambe)
- Registro `data/atlante/assets.json` (campi come in §4, più `metodo`: tmdb-scena | ai | originale, e `modello/prompt` per le AI; `sha256` univoco per identità+continuità).
- WebP verticale 3:4, due risoluzioni, lazy loading con segnaposto sfocato, `srcset`, cache SW, fallback.
- **Modalità «immagini private»:** gli asset protetti restano sul tuo dispositivo (IndexedDB, importati da te) o per hotlink TMDB, **fuori da repository, ZIP e Netlify**; il deploy pubblico non contiene opere protette. Riduce l'esposizione, non la elimina; l'iPhone è l'unico dispositivo, quindi le immagini andrebbero caricate da lì o recuperate a runtime.
- Foto attori: solo nelle schede interpreti, campo `tipo=attore`, mai associate a un'identità-personaggio.

## 10. Decisioni richieste
1. **Pilota misurato (consigliato prima di scegliere):** 10 identità reali (mix MCU/Sony/Fox/animazione/non-personaggio) con scene TMDB, per misurare quante hanno una scena valida e come viene il ritaglio verticale. Richiede una tua chiave TMDB gratuita e la tua autorizzazione ad accedere dal tuo PC.
2. **Diffusione:** accetti la modalità «immagini private/locali» (nessuna opera protetta nel deploy pubblico)?
3. **AI:** vuoi un campione di 5 illustrazioni in locale (serve conoscere la tua GPU) oppure autorizzi una spesa massima (es. 15 €) per un campione a pagamento? Oppure escludere l'AI per i personaggi e usarla solo per universi/luoghi/artefatti/eventi?
4. **Ibrido (proposta):** scene TMDB per i personaggi; illustrazioni originali AI uniformi per universi, luoghi, artefatti, eventi.

Sources: [TMDB API Terms of Use](https://themoviedb.org:443/api-terms-of-use) · [TMDB support – nessun diritto sulle immagini](https://www.themoviedb.org/talk/530525ae9251413488038dc4) · [Gemini – free tier immagini](https://discuss.ai.google.dev/t/free-tier-api-image-generation/177423) · [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing?authuser=6) · [Disney/Universal v. Midjourney](https://www.yahoo.com/news/disney-universal-file-first-major-152734187.html)
