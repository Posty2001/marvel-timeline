# Tessera TVA 2.0 — Report T0 (fondamenta, nessuna modifica visibile)

Data: 28/11/2026 · Branch `test/tva-archives` · Produzione congelata · Database Expansion db9 (commit `0209847`) congelata · Budget 0 €.
Stato: **T0 eseguita, in attesa di approvazione prima di T1.** Non dichiarata «completata». Nessun file dell'app modificato (`index.html` e moduli identici al commit `e1920d1`).

Denominazione (D1): nome visibile **Tessera TVA 3.0**; sezione **La mia Tessera**; nella Master Roadmap resta «Tessera TVA 2.0».

---

## 1. Decisioni vincolanti recepite (D1–D13)
| # | Decisione | Effetto sul progetto |
|---|---|---|
| D1 | Nome visibile / sezione / roadmap | Tessera TVA 3.0 · «La mia Tessera» · «Tessera TVA 2.0» (roadmap). La voce della barra resta «Tessera». |
| D2 | Ranghi e livelli separati | Nessun tocco a soglie, calcoli, ricompense, regole. Livelli senza nome = numerici. Test E1/E2 bloccano ogni modifica al blocco XP e a `TESSERA_TIERS`. |
| D3 | Vetrina a 6 slot | Liberamente configurabili e riordinabili; riempimento facoltativo; i 3 distintivi salvati oggi (`tessera-look.b`) restano i primi tre. |
| D4 | 12 sfondi animati | 4 subito (Sacra Linea Temporale, Terminale TVA, Multiverso, Archivio Dorato), 8 sbloccabili (Yggdrasil, Dimensione Specchio, Dimensione Oscura, Regno Quantico, Bifrost, Il Vuoto, Spider-Verse, Infinito). **Condizioni di sblocco: da approvare separatamente** (non inventate qui). SVG/CSS originali, modalità statica, disattivazione, `prefers-reduced-motion`. Si aggiungono ai 9 sfondi esistenti. |
| D5 | Titolo libero ≤ 40 caratteri | Alternativa ai 20 titoli ufficiali; distinto dal rango (campo e presentazione separati). |
| D6 | Friends | Solo predisposizione: contratto «identità condivisa v1» + controlli di visibilità; identità unica Tessera↔Friends; Firebase Realtime Database + Auth, niente Firestore; nessun collegamento reale ora. |
| D7 | Fotografia | Resta locale, esclusa da sync e backup automatici (valutazione in Friends 3.0). |
| D8 | Integrazioni future | Solo contratti dati: Arcade, Quiz, Rankings, Missioni, Evolution, Legame Nexus. Nessun XP nuovo; nessuno slot inutilizzabile in interfaccia. |
| D9 | Direzione grafica | Design system reale di TVA Archives (screenshot app reale prioritari sulle immagini concettuali). |
| D10 | Preservazione | Tutto il catalogo e i dati esistenti (v. §2); test «catalogo congelato» bloccante. |
| D11 | Cinque sezioni | Tessera · Carriera · Atelier · Collezione · Identità (v. §5). |
| D12 | iPhone / iPad | iPhone verticale compatto coerente con Centrale TVA; iPad dedicato a due colonne; verticale, orizzontale, Split View. |
| D13 | Sviluppo | Solo T0 su TEST; consegna resoconto e attesa approvazione prima di T1; dopo l'approvazione le fasi successive potranno essere accorpate. |

---

## 2. Censimento delle personalizzazioni (dal codice vivo)
Strumento: `python3 tools/tessera_censimento.py --scrivi|--verifica` (carica l'app reale in browser headless e legge le API `tvaCardArt`, `tvaTessera3`, `tvaEmblems`, `tvaRewards`, `tvaIdentity`). Uscita: `docs/tessera2/censimento_runtime_T0.json` (valori completi, anche dei preset) accanto allo snapshot di ID `inventario_personalizzazioni_28112026.json`.

| Famiglia | Esistenti | Note |
|---|---|---|
| Avatar | **8** | agente, variante, esploratore, tecnologico, mistico, astratto, cronista, sentinella |
| Cornici (motore grafico) | **12** | |
| Temi | **10** | |
| Effetti (motore grafico) | **6** | |
| Emblemi | **56** | 7 categorie × 8, 6 finiture (oro, argento, bronzo, rubino, neon, inchiostro) |
| Ricompense | **48** | 20 titoli, 12 cornici, 10 temi, 6 effetti; 5 rarità (c, n, r, e, l); condizioni verificabili invariate |
| Stile 3.0 | font 4 · sfondi 9 · texture 6 · cornici di stile 7 · decorazioni 6 · effetti 6 · icone 3 · layout 4 | |
| **Preset di stile** | **7** | Archivio Classico, Cosmic, Mystic, Tech, Dark Multiverse, Royal, Temporal |
| Altro | foto locale (JPEG ≤ 600 KB) · retro identità · rotazione 3D · condivisione/esportazione PNG · 3 distintivi in vetrina · 14 distintivi · 8 ranghi · VAR-ID · identità Variante (emblema, motto, universo, personaggio preferito) | |

Risultato: nessuna personalizzazione ulteriore oltre a D10 è emersa; i 7 preset includono «Temporal», non citato nell'elenco di D10 («eventuali ulteriori personalizzazioni già presenti» → preservato).
Osservazione sull'anteprima concettuale: mostra 4 sfondi e icone che **non** sono il catalogo reale (es. avatar/volto, rango «Agente Senior», livello 18, 1.976 voci): sono segnaposto grafici e **non** definiscono valori (D10).

---

## 3. Compatibilità con i dati esistenti (verificata con test automatici)
Profilo campione con nome, VAR-ID, aspetto, stile, identità, ricompense (anche una con condizione non soddisfatta), foto locale e progresso, caricato due volte:
- chiavi `user-name`, `tessera-id`, `tessera-look`, `tessera-photo`, `watched`, `ratings`, `notes`, `favorites` **byte-identiche**; `identity-v1` e `tessera-style-v1` con tutti i valori scelti preservati (l'app può solo normalizzare il formato); `rewards`: sblocchi e selezioni seminati identici, l'app aggiunge solo sblocchi maturati (comportamento esistente, mai revoca);
- Annulla non scrive nulla; Salva scrive in `tessera-look` con lo stesso formato; esportazione PNG funzionante;
- XP, livello, rango, percentuale, distintivi su 3 profili: identici al riferimento (`docs/tessera2/baseline_xp_T0.json`); formula livello 100+(n−1)·30; blocco di calcolo XP e `TESSERA_TIERS` byte-identici a `e1920d1`.
Esito: **`python3 tests/tessera_t0_test.py` → 56 PASS, 0 FAIL** (due esecuzioni consecutive; verificato con mutazione che il confronto rileva un avatar rimosso e una rarità modificata).
Chiavi create dall'app oltre al seed (comportamento esistente): `auto-backup`, `badges-earned`, `live-state-v1`.

Limiti dichiarati: i test non coprono Safari iOS reale né iPad reale (collaudo manuale a fine fase); la foto accettata dall'app è solo JPEG (regola esistente, invariata).

---

## 4. Componenti grafici e tecnici riutilizzabili
| Componente | Dove | Riuso previsto |
|---|---|---|
| Motore SVG carta (`tvaCardArt.build/thumb/avatarThumb/frameSvg`) | `tc-art-js` | anteprima viva Atelier, miniature, esportazione |
| Stile 3.0 (`tvaTessera3.render/applyPreset/opts/styleNow`) | `tva-tessera3` | anteprima, preset, sfondi (si aggiungono nuovi sfondi alla mappa `BGS`) |
| Emblemi (`tvaEmblems.svg`, 56 + finiture) | `tva-emblems` | Collezione, Identità, vetrina |
| Ricompense (`tvaRewards.catalog/unlocked/equip/progress`) | `rw-js` | Collezione, Atelier (condizioni e requisiti visibili) |
| Identità (`tvaIdentity.get/set/backup*`) | `tva-identity` | sezione Identità, contratto Friends |
| Editor classico (`tvaTessera.open`) + foto/PNG/share (`exportPng`, `share`, `flip`) | `tc-js` | resta intatto («Editor completo»); le funzioni di condivisione sono riutilizzate |
| Design system: sfondo antracite, oro/beige/ambra, serif titoli, sans funzionale, pannelli arrotondati, bordo sottile | CSS `index.html` | invariato; barra a 5 sezioni modellata sulla barra pill di Centrale TVA |
| Barra di navigazione originale, launcher Miss Minutes | shell app | invariati; i controlli restano fuori dalla zona del launcher (oggi, negli screenshot reali, il launcher sovrasta il bordo destro di «Condividi» e dei preset: da correggere in T1, come fatto in Atlas) |
| Pattern modulo lazy (`atlante2/*.js/css`) e `assets/tablet.css` (≥768×600) | repo | nuovo modulo lazy `tessera2/` e layout iPad a due colonne |
| Preferenza movimento ridotto (`tvaTessera3.reduced`) | `tva-tessera3` | sfondi animati |

---

## 5. Architettura delle cinque sezioni (La mia Tessera)
Modulo **lazy additivo** `tessera2/` (`tessera2.js`, `tessera2.css`, dati), caricato all'apertura della sezione, senza toccare le chiavi esistenti. Il nuovo hub si aggancia alla stessa voce «Tessera» della barra; l'overlay e l'editor attuali restano raggiungibili (voce «Editor completo» nell'Atelier) per tutta la durata del progetto.

| Sezione | Contenuto (D11) | Fonti dati (sola lettura, nessun duplicato) | Azioni |
|---|---|---|---|
| **Tessera** | carta fronte/retro 3D, identità, vetrina 6 slot, accesso rapido, condivisione/PNG | `tvaTessera.current/model`, `tvaIdentity`, `tessera-v2.vetrina` | gira, ruota 3D, condividi/esporta (riuso `share/exportPng`), apri Atelier |
| **Carriera** | passaporto, rango e livello **separati**, progressione, statistiche effettive, riconoscimenti | `marvelXpInfo`, `tesseraRank/Pct`, badge, Atlas (`leggiXpAtlante` sola lettura) | nessuna scrittura |
| **Atelier** | anteprima in tempo reale; Avatar, Preset, Titoli, Cornici, Temi, Effetti, Sfondi animati + tutti i controlli dell'editor attuale; Salva/Annulla | stesse API dell'editor classico; nuove opzioni in `tessera-v2` | Salva/Annulla con bozza (come oggi); «Editor completo» |
| **Collezione** | emblemi, ricompense, badge, ottenuti/sbloccabili, filtri sui dati reali, gestione vetrina | `tvaEmblems`, `tvaRewards`, badge | assegna alla vetrina; nessuna rarità nuova |
| **Identità** | Passaporto Variante, VAR-ID, universo origine/preferito, personaggio preferito, titolo personale, selezione da TVA Atlas, privacy | `tvaIdentity`, Atlas (catalogo, sola lettura), `tessera-v2.privacy` | modifica identità, backup identità esistente |

Note: «universo di origine» (D11) è un campo **nuovo** distinto dall'«universo preferito» (esistente, `identity-v1.univ`): sarà additivo in `tessera-v2` e migrato senza toccare quello esistente; «statistiche personali effettive» = una sola fonte di calcolo (negli screenshot reali Home «3/138 completati» e Centrale «4/138 visti» differiscono: da verificare in T2, non assumo la causa).

### 5.1 Schema dati additivo `tessera-v2` (bozza, non implementato)
Chiave **nuova** `marvel-ultimate-timeline-tessera-v2` (nessuna chiave rinominata):
```json
{ "v": 1,
  "vetrina": [ {"t":"badge|emblema|ricompensa","id":"…"} | null, … ×6 ],
  "sfondoAnim": "sacra-linea | terminale-tva | …  | null",
  "animazioni": "auto | statico | off",
  "titolo": { "modo": "ufficiale | personale", "testo": "≤40 caratteri" },
  "origine": { "universoId": "…|null" },
  "privacy": { "carta":"p","identita":"p","rango":"p","titolo":"p","preferiti":"p","statistiche":"p","emblemi":"p","vetrina":"p" },
  "ts": 0 }
```
Regole: validazione rigorosa, valori di ripiego, `textContent`/SVG costruito (mai HTML da dati utente), limite 40 caratteri con normalizzazione e rimozione di caratteri di controllo, copia di sicurezza prima di ogni conversione, nessun invio in rete. `privacy`: tutto «privato» di default; nessuna rete in questa fase. Foto **mai** nello schema. Il titolo personale è un campo separato da rango e titoli ufficiali.

### 5.2 Predisposizioni (contratti, senza logica e senza UI vuota)
`tvaTrophies.list()` (vuota), contratto «identità condivisa v1» (nome, VAR-ID, aspetto, rango/livello, titolo personale, universo/preferito, statistiche scelte, emblemi/ricompense, vetrina, `legameNexus: nessuno`), hook disattivati per Missioni/Evolution/Arcade/Quiz/Rankings. L'interfaccia non mostra slot finché la fonte non è disponibile (D8).

### 5.3 iPhone / iPad (D12)
iPhone: verticale, compatto, barra a cinque sezioni sul modello di Centrale TVA, area di tocco ≥ 44 px, safe area, nessun overflow. iPad (≥768×600): due colonne — carta e anteprima a sinistra, contenuto della sezione a destra — con comportamento dedicato per verticale, orizzontale e Split View; non un semplice ingrandimento.

---

## 6. Piano delle verifiche automatiche
Già operative (T0): `tests/tessera_t0_test.py` (56 controlli) + `tools/tessera_censimento.py --verifica`, da eseguire a **ogni** fase T1–T7 e bloccanti.
Da aggiungere per fase:
- T1: nessun overflow 320–430 px e iPad; carta nuova ⊇ elementi della carta attuale; launcher non sovrapposto ai controlli.
- T2: valori di Carriera = valori di `marvelXpInfo`/rango (stessa fonte); nessuna scrittura su chiavi di progresso.
- T3: ogni elemento del catalogo selezionabile nell'Atelier e nell'editor classico; Salva/Annulla equivalenti; reduce-motion; validazione titolo (40 car., caratteri di controllo, HTML non interpretato).
- T4: vetrina 6 slot con migrazione dei 3 esistenti identici; ordine e svuotamento; esportazione PNG.
- T5: migrazione «origine» additiva con copia di sicurezza; nessuna modifica a `identity-v1`.
- T6: contratti presenti, nessun effetto XP, nessuna chiamata di rete.
- T7: suite essenziale esistente (Atlas a70, Miss Minutes, Tessera) senza regressioni; prestazioni animazioni.
Regola: una fase non arriva all'approvazione se un test di guardia fallisce.

---

## 7. Rischi e punti aperti
- Condizioni di sblocco degli 8 sfondi: da approvare separatamente (D4); nessun XP nuovo.
- Collaudo reale su iPhone/iPad Safari e Split View: non eseguibile in automatico.
- «Universo di origine» e privacy hanno bisogno della struttura dati nuova (`tessera-v2`); non ancora implementati.
- `friends3-js` resta basato su Firestore: riallineamento in macro-fase 8 (non toccato).
- Home/Centrale: possibile discrepanza dei contatori titoli (da verificare in T2).

## 8. Prossimo passo (in attesa)
Approvazione di T0 → T1 (hub «La mia Tessera», carta fronte/retro, correzione sovrapposizioni, iPhone). Dopo l'approvazione le fasi T1–T7 potranno essere accorpate come da D13.
