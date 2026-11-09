// Unisce le regole PROPOSTE (nodo `users`) alle regole ATTUALI di produzione, esportate da te in current.rules.json
// (Console Firebase > Realtime Database > Regole > copia). Non modifica nulla in produzione: scrive solo database.rules.merged.json.
import fs from 'node:fs';
const cur = JSON.parse(fs.readFileSync(new URL('./current.rules.json', import.meta.url), 'utf8'));
const add = JSON.parse(fs.readFileSync(new URL('../rules.users.proposed.json', import.meta.url), 'utf8'));
if (!cur.rules) throw new Error('current.rules.json: manca la chiave "rules"');
if (cur.rules.users) throw new Error('Esiste gia\' un nodo "users" nelle regole attuali: fermarsi e verificare.');
const fr = JSON.parse(fs.readFileSync(new URL('../rules.friends.proposed.json', import.meta.url), 'utf8'));
for (const k of Object.keys(fr.rules)) if (cur.rules[k]) throw new Error('Esiste gia\' un nodo "' + k + '" nelle regole attuali: fermarsi e verificare.');
const merged = { rules: Object.assign({}, cur.rules, { users: add.rules.users }, fr.rules) };
for (const k of Object.keys(cur.rules)) if (JSON.stringify(merged.rules[k]) !== JSON.stringify(cur.rules[k])) throw new Error('Il merge ha alterato ' + k);
fs.writeFileSync(new URL('./database.rules.merged.json', import.meta.url), JSON.stringify(merged, null, 2));
console.log('OK: database.rules.merged.json creato. Nodi invariati:', Object.keys(cur.rules).join(', '));
