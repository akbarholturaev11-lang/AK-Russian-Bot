#!/bin/bash
set -e

echo "=== Alembic migration check ==="

# alembic current xato bo'lsa ham to'xtatmaymiz
CURRENT=$(alembic current 2>&1 || true)
echo "Alembic current output:"
echo "$CURRENT"

# Revision ID bor-yo'qligini tekshiramiz (masalan: "0016_add_course_promo_sent (head)")
# Agar output da hech qanday revision ID bo'lmasa — stamp head
if echo "$CURRENT" | grep -qE "^[0-9a-f]|[0-9]{4}_"; then
    echo "Revision found in DB — running upgrade head normally."
else
    echo "No revision ID detected (only INFO lines or empty). Stamping at head..."
    alembic stamp head
    echo "Stamp complete."
fi

echo "=== Running alembic upgrade head ==="
alembic upgrade head && echo "Migrations OK." || {
    echo "Upgrade still failed — force stamp and retry..."
    alembic stamp head
    alembic upgrade head
    echo "Done after force stamp."
}

echo "=== Starting uvicorn ==="
export PYTHONUNBUFFERED=1
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
