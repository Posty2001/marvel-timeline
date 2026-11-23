#!/usr/bin/env bash
# TVA Live - commit dei soli dati su test/tva-archives (usato dal workflow; testato con un remoto locale).
# Permessi minimi: scrive SOLO i 4 file di assets/live/ e SOLO verso il branch TEST (refspec fisso). Mai main.
# Uso: tools/live_git_commit.sh <file-messaggio> [remote=origin]
set -euo pipefail
BRANCH="test/tva-archives"
MSG_FILE="${1:?file messaggio}"; REMOTE="${2:-origin}"
ALLOWED="assets/live/calendar.json assets/live/trailers.json assets/live/manifest.json assets/live/status.json"
[ "$(git rev-parse --abbrev-ref HEAD)" = "$BRANCH" ] || { echo "ERRORE: branch corrente diverso da $BRANCH: rifiuto di committare." >&2; exit 3; }
git add -- $ALLOWED
if git diff --cached --quiet; then echo "Nessuna modifica da committare."; exit 0; fi
extra="$(git diff --cached --name-only | grep -vxF -f <(printf '%s\n' $ALLOWED) || true)"
[ -z "$extra" ] || { echo "ERRORE: file non consentiti in stage: $extra" >&2; exit 4; }
git -c user.name="tva-live-bot" -c user.email="41898282+github-actions[bot]@users.noreply.github.com" commit -q -F "$MSG_FILE"
for i in 1 2 3; do
  git pull -q --rebase "$REMOTE" "$BRANCH" || true
  if git push -q "$REMOTE" "HEAD:refs/heads/$BRANCH"; then echo "Pubblicato su $BRANCH (solo dati)."; exit 0; fi
  sleep 3
done
echo "ERRORE: push non riuscito dopo 3 tentativi (il catalogo precedente resta valido)." >&2; exit 5
