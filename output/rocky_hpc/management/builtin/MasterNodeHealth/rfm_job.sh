#!/bin/bash
bash -c 
        set -eu

        echo "MASTER=$(hostname -s)"

        CPU_COUNT=$(lscpu -p=CPU |
            awk '!/^#/ {count++} END {print count+0}')

        MEM_KB=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
        MEM_MB=$((MEM_KB / 1024))

        echo "CPU_COUNT=$CPU_COUNT"
        echo "MEMORY_MB=$MEM_MB"

        test "$CPU_COUNT" -ge 2
        test "$MEM_MB" -ge 1500

        systemctl is-active --quiet munge
        echo "MUNGE_OK"

        systemctl is-active --quiet slurmctld
        echo "SLURMCTLD_OK"

        echo "MASTER_HEALTH_OK"
