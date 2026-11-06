
#!/bin/bash

# ==========================================================
# HPC BENCHMARK ORCHESTRATOR + PERFORMANCE REPORT GENERATOR
# ==========================================================

set -uo pipefail

PROJECT_DIR="/mnt/shared/test35/hpc-reframe"
REFRAME_BIN="/mnt/shared/test35/.local/bin/reframe"
CONFIG="${PROJECT_DIR}/config/cluster_info_2.py"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

RUN_DIR="${PROJECT_DIR}/reports/benchmark_run_${TIMESTAMP}"
LOG_DIR="${RUN_DIR}/logs"
RFM_REPORT_DIR="${RUN_DIR}/reframe"

SUMMARY_FILE="${RUN_DIR}/summary.csv"
STATUS_FILE="${RUN_DIR}/run_status.tsv"

mkdir -p "$LOG_DIR" "$RFM_REPORT_DIR"

cd "$PROJECT_DIR" || exit 1

# ----------------------------------------------------------
# Validate prerequisites
# ----------------------------------------------------------

if [[ ! -x "$REFRAME_BIN" ]]; then
    echo "ERROR: ReFrame not found: $REFRAME_BIN"
    exit 1
fi

if [[ ! -f "$CONFIG" ]]; then
    echo "ERROR: Configuration not found: $CONFIG"
    exit 1
fi

if [[ ! -f "${PROJECT_DIR}/scripts/generate_report.py" ]]; then
    echo "ERROR: Report generator not found."
    exit 1
fi

# ----------------------------------------------------------
# Benchmark execution order
# ----------------------------------------------------------

declare -a BENCHMARKS=(
    "HPL:hpl_test.py"
    "OSU_LATENCY:osu_latency.py"
    "OSU_BANDWIDTH:osu_bw.py"
    "OSU_ALLREDUCE:osu_allreduce.py"
    "STREAM:stream.py"
)

TOTAL=${#BENCHMARKS[@]}
PASSED=0
FAILED=0

printf "benchmark\tstatus\tduration_seconds\n" > "$STATUS_FILE"

echo "=========================================================="
echo "       HPC BENCHMARK PERFORMANCE ORCHESTRATOR"
echo "=========================================================="
echo "Run ID       : $TIMESTAMP"
echo "Project      : $PROJECT_DIR"
echo "ReFrame      : $REFRAME_BIN"
echo "Configuration: $CONFIG"
echo "Total tests  : $TOTAL"
echo "Report dir   : $RUN_DIR"
echo "Started      : $(date)"
echo "=========================================================="

# ----------------------------------------------------------
# Execute each benchmark sequentially
# ----------------------------------------------------------

for ENTRY in "${BENCHMARKS[@]}"; do

    BENCHMARK="${ENTRY%%:*}"
    TEST_FILE="${ENTRY##*:}"

    TEST_PATH="${PROJECT_DIR}/tests/${TEST_FILE}"

    TEST_LOG="${LOG_DIR}/${BENCHMARK}.log"
    JSON_REPORT="${RFM_REPORT_DIR}/${BENCHMARK}.json"

    START_EPOCH=$(date +%s)

    echo
    echo "=========================================================="
    echo "STARTING BENCHMARK: $BENCHMARK"
    echo "TEST FILE         : $TEST_FILE"
    echo "START TIME        : $(date)"
    echo "=========================================================="

    if [[ ! -f "$TEST_PATH" ]]; then

        echo "ERROR: Test file not found: $TEST_PATH" | tee "$TEST_LOG"

        STATUS="NOT_FOUND"
        RC=1

    else

        "$REFRAME_BIN" \
            -C "$CONFIG" \
            -c "$TEST_PATH" \
            -r \
            -v \
            --performance-report \
            --report-file="$JSON_REPORT" \
            > "$TEST_LOG" 2>&1

        RC=$?

        if [[ $RC -eq 0 ]]; then
            STATUS="PASSED"
            PASSED=$((PASSED + 1))
        else
            STATUS="FAILED"
            FAILED=$((FAILED + 1))
        fi

    fi

    END_EPOCH=$(date +%s)
    DURATION=$((END_EPOCH - START_EPOCH))

    printf "%s\t%s\t%s\n" \
        "$BENCHMARK" "$STATUS" "$DURATION" >> "$STATUS_FILE"

    echo
    echo "BENCHMARK : $BENCHMARK"
    echo "STATUS    : $STATUS"
    echo "DURATION  : ${DURATION}s"
    echo "LOG       : $TEST_LOG"
    echo "=========================================================="

done

# ----------------------------------------------------------
# Generate centralized performance report
# ----------------------------------------------------------

echo
echo "Generating centralized performance report..."

python3 "${PROJECT_DIR}/scripts/generate_report.py" "$RUN_DIR"

REPORT_RC=$?

# ----------------------------------------------------------
# Final execution summary
# ----------------------------------------------------------

echo
echo "=========================================================="
echo "             BENCHMARK EXECUTION COMPLETED"
echo "=========================================================="

echo "Total tests : $TOTAL"
echo "Passed      : $PASSED"
echo "Failed      : $FAILED"
echo "Report      : $RUN_DIR/report.html"

if [[ $REPORT_RC -ne 0 ]]; then
    echo "WARNING: Performance report generation failed."
fi

if [[ $FAILED -gt 0 || $REPORT_RC -ne 0 ]]; then
    echo "OVERALL STATUS: FAILURE"
    exit 1
else
    echo "OVERALL STATUS: SUCCESS"
    exit 0
fi
