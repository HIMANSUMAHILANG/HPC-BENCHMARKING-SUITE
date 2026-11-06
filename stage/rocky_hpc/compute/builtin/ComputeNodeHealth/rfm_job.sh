#!/bin/bash
#SBATCH --job-name="rfm_ComputeNodeHealth"
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --output=rfm_job.out
#SBATCH --error=rfm_job.err
#SBATCH --time=0:2:0
#SBATCH --partition=High
srun --cpus-per-task=1 bash -c 
        set -eu

        NODE=$(hostname -s)

        CPU_COUNT=$(lscpu -p=CPU |
            awk '!/^#/ {count++} END {print count+0}')

        MEM_KB=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
        MEM_MB=$((MEM_KB / 1024))

        echo "NODE=$NODE"
        echo "CPU_COUNT=$CPU_COUNT"
        echo "MEMORY_MB=$MEM_MB"

        case "$NODE" in
            compute1|compute2) ;;
            *)
                echo "UNEXPECTED_NODE=$NODE"
                exit 1
                ;;
        esac

        test "$CPU_COUNT" -ge 2
        test "$MEM_MB" -ge 1500

        echo "NODE_HEALTH_OK"
