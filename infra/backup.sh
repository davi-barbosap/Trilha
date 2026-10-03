#!/usr/bin/env bash
# Backup diário (cron 03:00): banco do n8n + exportação dos fluxos para o Git.
# Qualquer falha avisa no Slack — backup que falha em silêncio é o pior cenário.
# Teste a restauração uma vez por trimestre: backup nunca restaurado não é backup.
set -euo pipefail
cd "$(dirname "$0")"

# Variáveis do compose (POSTGRES_USER, SLACK_WEBHOOK_URL…) também para este script
set -a; . ./.env; set +a

avisar_falha() {
  [ -n "${SLACK_WEBHOOK_URL:-}" ] && curl -fsS -X POST -H 'Content-Type: application/json' \
    -d "{\"text\":\":rotating_light: backup.sh falhou na linha $1 ($(hostname))\"}" "$SLACK_WEBHOOK_URL" >/dev/null || true
}
trap 'avisar_falha $LINENO' ERR

DATA=$(date +%F)
COMPOSE="docker compose -f docker-compose.yml --env-file .env"

# 1. Banco do n8n (fluxos, credenciais criptografadas, histórico)
mkdir -p backup
$COMPOSE exec -T postgres pg_dump -U "$POSTGRES_USER" n8n | gzip > "backup/n8n-$DATA.sql.gz"
find backup -name 'n8n-*.sql.gz' -mtime +30 -delete

# 2. Fluxos: exporta dentro do contêiner (sem pasta compartilhada, sem problema de permissão)
#    e substitui n8n/fluxos/ por completo, com um arquivo por fluxo nomeado pelo nome do fluxo.
$COMPOSE exec -T n8n sh -c 'rm -rf /tmp/fluxos && n8n export:workflow --all --separate --pretty --output=/tmp/fluxos'
rm -rf backup/fluxos && $COMPOSE cp n8n:/tmp/fluxos backup/fluxos
rm -rf ../n8n/fluxos && mkdir -p ../n8n/fluxos
for f in backup/fluxos/*.json; do
  nome=$(python3 -c 'import json,re,sys; n=json.load(open(sys.argv[1]))["name"]; print(re.sub(r"[^A-Za-z0-9._-]+","-",n).strip("-"))' "$f")
  cp "$f" "../n8n/fluxos/$nome.json"
done

# 3. Versiona (credenciais não são exportadas pelo n8n)
cd ..
git add -A n8n/fluxos
git diff --cached --quiet || git commit -qm "n8n: exportação diária dos fluxos ($DATA)"
git push -q
