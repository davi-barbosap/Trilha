#!/usr/bin/env bash
# Backup diário (cron 03:00): banco do n8n + exportação dos fluxos para o Git.
# Teste a restauração uma vez por trimestre — backup nunca restaurado não é backup.
set -euo pipefail
cd "$(dirname "$0")"
DATA=$(date +%F)
COMPOSE="docker compose -f docker-compose.yml --env-file .env"

mkdir -p backup
$COMPOSE exec -T postgres pg_dump -U "${POSTGRES_USER:-n8n}" n8n | gzip > "backup/n8n-$DATA.sql.gz"
find backup -name 'n8n-*.sql.gz' -mtime +30 -delete

# Fluxos versionados: um JSON por fluxo em n8n/fluxos/ (credenciais não são exportadas)
$COMPOSE exec -T n8n n8n export:workflow --all --separate --pretty --output=/backup/fluxos
cp backup/fluxos/*.json ../n8n/fluxos/ 2>/dev/null || true
cd .. && git add n8n/fluxos && git commit -qm "n8n: exportação diária dos fluxos ($DATA)" && git push -q || true
