# Secret Wars Draft 3.1 — report test e bilanciamento

Build `20261117-1800-arcade-draft31`. Riferimento statistico: **fumetti Marvel (Terra-616), non MCU**. Verifiche Chromium/Playwright separate da quelle che richiedono iPhone reale.

## Revisione delle 120 carte
- 49 carte modificate, 125 ritocchi di singole statistiche: **123 aumenti e 2 riduzioni**; 71 carte invariate. Ogni modifica ha motivazione fumettistica (`CAMBIAMENTI_STATISTICHE.csv`, `CONFRONTO_PRIMA_DOPO.md/.csv`).
- Aumenti concentrati dove le carte erano sottovalutate: asgardiani (Thor, Hela, Odino, Surtur, Ercole, Loki, Beta Ray Bill), cosmici (Galactus, Thanos, Silver Surfer, Adam Warlock, Black Bolt, Ronan, Gorr), mistici (Strange, Scarlet Witch, Dormammu, Mephisto, Doctor Voodoo, Mordo, Doom, Magik), mutanti di livello superiore (Magneto, Professor X, Jean Grey, Phoenix, Legion, Apocalypse, Storm, Iceman, Rogue). Diminuiti: Kingpin (forza umana massima) e Deadpool (resistenza: guarigione, non invulnerabilità).
- Massimo 99 (nessun 100); varianti Phoenix, Zarathos e Rune King Thor distinte dalla base. Le **fasce di generazione delle offerte non sono state toccate**: non servivano.
- Valore Battleworld: min 58, mediana 73,4, max 92 (v3.0: 58 / 72,8 / 91,2).

## Simulazioni (codice reale, seed riproducibili) — v3.1 vs v3.0
- **28.800 draft**, 252.000 offerte: **0 duplicati, 0 offerte non valide, 0 errori di snake**; riproducibilità confermata.
- Spread offerte: mediana 3,0 · p90 4,4 · p99 6,2 · max 10,6 · **96,9% entro 5 punti** (v3.0: 97,1%); banda allargata nel 6,9% dei casi (v3.0: 6,7%).
- Giocatore esperto (ruoli CPU ipotizzati): recluta 75–83% · stratega 64–70% · maestro 50–54% (v3.0: 77–82 / 67–68 / 49–52). Tabella completa in `CONFRONTO_SIMULAZIONI.md`. Differenze entro il rumore campionario (n=900 per cella; ±3 pt; sulle altre politiche n=300, ±5 pt).
- Valore massimo sempre: 15–58% (perde contro stratega/maestro); casuali 11–48%: il solo numero non è dominante.
- Specchio: primo giocatore 43–53% → nessun vantaggio sistematico.
- Contromossa ribalta l'esito nel 3–24% dei casi (a seconda della politica), mai automatica.
- Personaggi: pick rate medio 10%; massimo Galactus 24,7% (solo 1.316 offerte, vittoria 84,6%), Silver Surfer 17%. Vittorie più alte quando scelti: Thanos 86,4 · Odino 85,2 · Galactus 84,6 · Doom 84,4 · Dormammu 83,4 · Rune King Thor 83,3. Più basse: Colossus 47,1 · Havok 48,4. **Dopo la revisione i cosmici di vertice restano i più forti** (coerente coi fumetti) senza che il numero da solo basti a vincere; da osservare nel collaudo.

## Correzioni Safari (screenshot non ricevuti: interventi basati sul codice e sulle schermate di test)
- **Schermata iniziale**: rimossa la riga «Pesi …» duplicata (c'erano pesi nei chip e di nuovo in testo) e l'etichetta «Scenario» ripetuta nel banner; tolta la legenda ▲▼ prima della partita.
- **Quinto ruolo / pulsanti inferiori**: i 5 ruoli sono ora un dock fisso sopra «Auto ruoli / Combatti!» (5 colonne, etichette brevi, nome completo in `title`/aria-label); il quinto non è più nascosto sotto la barra; barra opaca; spaziatore dinamico (ResizeObserver) così il duello non resta coperto.
- **Safe area superiore**: sfondo `html` allineato alla barra (nessuna striscia chiara nel rimbalzo), `scroll-padding-top`, barra superiore sotto la Dynamic Island verificata a 59 px. Se il problema che hai visto è un altro, serve lo screenshot.
- Badge ▲/▼ sulle carte non coprono più i nomi.

## Test Chromium
- `draft3.py` (97 test; v3.0: 73 + 24 nuovi per i fix) · `ux` 20/20 · `offline` 10/10 · `hub` 13/13 · `int1` 12/12.
- Nuovi: dock ruoli visibile e toccabile a 320/390/430 (inizio e fine scroll), assegnazione dei 5 ruoli incluso Specialista, pulsanti sopra la home indicator (34 px) e ≥44 px, nessun testo duplicato, nessuna sovrapposizione col duello.

## Limiti dei test
- Safe area simulata con CDP in Chromium: **iPhone Safari reale NON verificato**.
- Il test dell'animazione di reclutamento controlla stato e tempi, non il rendering.
- Le suite `draft.py`, `draft_fix1.py`, `draft_scn.py` assumono il pool da 16 carte: obsolete.
