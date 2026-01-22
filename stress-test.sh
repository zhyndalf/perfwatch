#!/bin/bash
#
# PerfWatch Stress Test Script
# Generates load on CPU, Memory, Disk, and Network for metrics visualization
#
# Usage: ./stress-test.sh [duration_seconds]
# Default: 60 seconds
#

DURATION=${1:-60}

echo "============================================"
echo "  PerfWatch Stress Test"
echo "============================================"
echo ""
echo "  Duration: ${DURATION}s"
echo "  Dashboard: http://localhost:3000"
echo ""
echo "  Press Ctrl+C to stop early"
echo "============================================"
echo ""

# Cleanup on exit
cleanup() {
    echo ""
    echo "Stopping stress test..."
    jobs -p | xargs -r kill 2>/dev/null
    rm -f /tmp/stress_test_* 2>/dev/null
    echo "Done!"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# ============================================
# CPU STRESS - Max out all cores
# ============================================
echo "[CPU] Starting CPU stress on all cores..."
CORES=$(nproc)
for i in $(seq 1 $CORES); do
    (
        while true; do
            # Heavy math operations
            echo "scale=3000; 4*a(1)" | bc -l > /dev/null 2>&1
        done
    ) &
done
echo "[CPU] Started $CORES workers"

# ============================================
# MEMORY STRESS - Allocate and access memory
# ============================================
echo "[MEM] Starting memory stress (512MB)..."
python3 << 'PYTHON' &
import time
import os

# Allocate 512MB
size_mb = 512
print(f"[MEM] Allocating {size_mb}MB...")
data = bytearray(size_mb * 1024 * 1024)

# Continuously access memory to prevent swap
print(f"[MEM] Memory allocated, accessing continuously...")
i = 0
while True:
    # Write pattern to memory
    for j in range(0, len(data), 4096):
        data[j] = i % 256
    i += 1
    time.sleep(0.1)
PYTHON
echo "[MEM] Memory stress started"

# ============================================
# DISK I/O STRESS - Read/write operations
# ============================================
echo "[DISK] Starting disk I/O stress..."
(
    while true; do
        # Write random data
        dd if=/dev/urandom of=/tmp/stress_test_file bs=1M count=50 conv=fdatasync 2>/dev/null
        # Read it back
        dd if=/tmp/stress_test_file of=/dev/null bs=1M 2>/dev/null
        # Sync to ensure writes
        sync
        rm -f /tmp/stress_test_file
    done
) &
echo "[DISK] Disk I/O stress started"

# ============================================
# NETWORK STRESS - Generate network traffic
# ============================================
echo "[NET] Starting network stress..."
(
    while true; do
        # Hit the backend API repeatedly
        for i in $(seq 1 20); do
            curl -s http://localhost:8000/health > /dev/null &
            curl -s http://localhost:8000/api/db-status > /dev/null &
        done
        wait
        sleep 0.5
    done
) &
echo "[NET] Network stress started"

# ============================================
# Additional load - File operations
# ============================================
echo "[FILE] Starting file operation stress..."
(
    mkdir -p /tmp/stress_test_dir
    while true; do
        # Create many small files
        for i in $(seq 1 100); do
            echo "stress data $RANDOM" > /tmp/stress_test_dir/file_$i
        done
        # Read them
        cat /tmp/stress_test_dir/* > /dev/null 2>&1
        # Delete them
        rm -f /tmp/stress_test_dir/*
        sleep 0.2
    done
) &
echo "[FILE] File operation stress started"

echo ""
echo "============================================"
echo "  All stress tests running!"
echo "  View metrics at: http://localhost:3000"
echo "============================================"
echo ""

# Progress display
START_TIME=$(date +%s)
while true; do
    ELAPSED=$(($(date +%s) - START_TIME))
    REMAINING=$((DURATION - ELAPSED))

    if [ $REMAINING -le 0 ]; then
        echo ""
        echo "Duration complete!"
        break
    fi

    # Show current system stats
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEM_INFO=$(free -m | awk 'NR==2{printf "%.0f%% (%dMB/%dMB)", $3*100/$2, $3, $2}')

    printf "\r  [%3ds remaining] CPU: %s%% | MEM: %s     " $REMAINING "$CPU_USAGE" "$MEM_INFO"
    sleep 2
done

echo ""
echo "Stress test completed!"
