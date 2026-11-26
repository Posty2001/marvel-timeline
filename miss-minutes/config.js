/* Configurazione pubblica (nessun segreto). Lascia vuoto: l'indirizzo del gateway si incolla in Miss Minutes > Impostazioni (resta sul dispositivo).
   Se lo scrivi qui (es. 'https://miss-minutes-api.TUO-SOTTODOMINIO.workers.dev') ha la precedenza. Vuoto = nessun AI online.
   archivio: URL https della cartella dell'aggiornamento automatico dell'archivio TMDB (vuoto = SPENTO, nessuna richiesta di rete; v. docs/MISS_MINUTES_2_0_AGGIORNAMENTO_ARCHIVIO.md). */
globalThis.MISS_MINUTES_CONFIG = Object.freeze({ endpoint: '', archivio: '' });
