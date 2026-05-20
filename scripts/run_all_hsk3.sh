#!/bin/bash
# HSK3 barcha 20 ta darsni database ga seed qilish
# Ishlatish: bash scripts/run_all_hsk3.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=============================="
echo " HSK3 Seed Runner - 20 ta dars"
echo "=============================="
echo ""

cd "$PROJECT_DIR"

SUCCESS=0
FAILED=0
FAILED_LESSONS=""

for i in $(seq -f "%02g" 1 20); do
    SCRIPT="scripts/seed_hsk3_lesson_${i}.py"
    echo -n "HSK3-L${i} seeding... "
    if python3 "$SCRIPT" 2>&1; then
        echo "✅ OK"
        ((SUCCESS++))
    else
        echo "❌ FAILED"
        ((FAILED++))
        FAILED_LESSONS="$FAILED_LESSONS L${i}"
    fi
done

echo ""
echo "=============================="
echo " Natija: $SUCCESS/20 muvaffaqiyatli"
if [ $FAILED -gt 0 ]; then
    echo " Xatolar:$FAILED_LESSONS"
fi
echo "=============================="
