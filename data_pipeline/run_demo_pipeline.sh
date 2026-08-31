#!/usr/bin/env bash
set -e

# ═══════════════════════════════════════════════════════════════
# Wakala — Demo du pipeline temps reel
# Lance producers + consumers + affiche un resume apres N minutes.
#
# Usage:
#   bash run_demo_pipeline.sh                  # mode normal, 5 min
#   bash run_demo_pipeline.sh --fast           # mode accelere, 2 min
#   bash run_demo_pipeline.sh --fast --duration 10
# ═══════════════════════════════════════════════════════════════

FAST=""
DURATION=5

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)       FAST="--fast"; DURATION=2 ;;
    --duration)   DURATION="$2"; shift ;;
    *)
      echo "Usage: $0 [--fast] [--duration N]"
      exit 1
      ;;
  esac
  shift
done

PYTHON="python"
PIPELINE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$PIPELINE_DIR/logs"
mkdir -p "$LOG_DIR"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   Wakala - Pipeline Temps Reel                        ║"
echo "║   Duree: ${DURATION}min  Mode: ${FAST:-normal}                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 1. Verifier Kafka
echo "-> Verification Kafka..."
if ! python -c "
from confluent_kafka.admin import AdminClient
AdminClient({'bootstrap.servers': 'localhost:9092'}).list_topics(timeout=5)
" 2>/dev/null; then
  echo "  X Kafka non accessible sur localhost:9092"
  echo "  Lance d'abord: docker compose up -d kafka"
  exit 1
fi
echo "  V Kafka OK"

# 2. Creer les topics
echo "-> Creation des topics..."
python "$PIPELINE_DIR/kafka/topics_config.py"

# 3. Nettoyer les logs precedents
rm -f "$LOG_DIR"/*.log

# 4. Lancer les consumers (background)
echo "-> Demarrage des consumers..."
cd "$PIPELINE_DIR"

nohup python -m data_pipeline.kafka.consumers.listing_consumer \
  > "$LOG_DIR/consumer_listings.log" 2>&1 &
PID_CONS_L=$!
echo "  V Consumer listings (PID $PID_CONS_L)"

nohup python -m data_pipeline.kafka.consumers.interaction_consumer \
  > "$LOG_DIR/consumer_interactions.log" 2>&1 &
PID_CONS_I=$!
echo "  V Consumer interactions (PID $PID_CONS_I)"

sleep 2

# 5. Lancer les producers (background)
echo "-> Demarrage des producers..."
python -m data_pipeline.kafka.producers.scrapers.run_producer \
  --live > "$LOG_DIR/producer_listings.log" 2>&1 &
PID_PROD_L=$!
echo "  V Producer listings (scrapers) (PID $PID_PROD_L)"

python -m data_pipeline.kafka.producers.interaction_producer \
  $FAST --duration $DURATION > "$LOG_DIR/producer_interactions.log" 2>&1 &
PID_PROD_I=$!
echo "  V Producer interactions (PID $PID_PROD_I)"

# 6. Attendre la fin de la production
echo ""
echo "-> Production en cours... (${DURATION} minutes)"
wait $PID_PROD_L $PID_PROD_I 2>/dev/null
echo "  Production terminee."

# 7. Laisser les consumers finir d'ecrire le buffer
sleep 3

# 8. Arreter les consumers
kill $PID_CONS_L $PID_CONS_I 2>/dev/null || true
wait $PID_CONS_L $PID_CONS_I 2>/dev/null || true
echo "  Consumers arretes."

# 9. Resume
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   RESUME DU PIPELINE                                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

BRONZE_L_COUNT=$(find "$PIPELINE_DIR/storage/bronze/listings" \
  -name "*.parquet" 2>/dev/null | wc -l)
BRONZE_I_COUNT=$(find "$PIPELINE_DIR/storage/bronze/interactions" \
  -name "*.parquet" 2>/dev/null | wc -l)
BRONZE_L_SIZE=$(du -sh "$PIPELINE_DIR/storage/bronze/listings" \
  2>/dev/null | cut -f1 || echo "0B")
BRONZE_I_SIZE=$(du -sh "$PIPELINE_DIR/storage/bronze/interactions" \
  2>/dev/null | cut -f1 || echo "0B")

echo "  Bronze (listings)     : ${BRONZE_L_COUNT} fichiers (${BRONZE_L_SIZE})"
echo "  Bronze (interactions) : ${BRONZE_I_COUNT} fichiers (${BRONZE_I_SIZE})"

# Derniers evenements Kafka
echo ""
echo "  Derniers listings.raw :"
python -c "
from confluent_kafka import Consumer
c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'demo-summary',
    'auto.offset.reset': 'earliest'
})
c.subscribe(['listings.raw'])
msgs = []
for _ in range(5):
    m = c.poll(2)
    if m and not m.error():
        msgs.append(m)
for m in msgs:
    print(f'    [{m.partition()}] {m.key().decode()}')
c.close()
" 2>/dev/null || echo "    (non disponible)"

echo ""
echo "-> Logs complets: $LOG_DIR/"
echo "-> Commande pour lancer Spark streaming:"
echo "    spark-submit spark/streaming_jobs/clean_listings_job.py"
echo "    spark-submit spark/streaming_jobs/clean_interactions_job.py"
echo ""
echo "V Pipeline termine."
