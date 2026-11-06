#!/bin/bash
#SBATCH --job-name="rfm_SharedFilesystemTest"
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --output=rfm_job.out
#SBATCH --error=rfm_job.err
#SBATCH --time=0:3:0
#SBATCH --partition=High
srun --cpus-per-task=1 bash -c 
        set -eu

        SHARED_PATH="/home"
        JOB_ID="$SLURM_JOB_ID"
        TASK_ID="$SLURM_PROCID"

        FILE="$SHARED_PATH/.reframe_${JOB_ID}_${TASK_ID}"

        echo "NODE=$(hostname -s)"
        echo "SHARED_PATH=$SHARED_PATH"

        test -d "$SHARED_PATH"

        touch "$FILE"

        # Wait until both tasks' files are visible.
        FOUND=0

        for attempt in $(seq 1 20); do
            if [ -f "$SHARED_PATH/.reframe_${JOB_ID}_0" ] &&
               [ -f "$SHARED_PATH/.reframe_${JOB_ID}_1" ]; then
                FOUND=1
                break
            fi
            sleep 1
        done

        if [ "$FOUND" -ne 1 ]; then
            echo "SHARED_VISIBILITY_FAILED"
            exit 1
        fi

        rm -f "$FILE"

        echo "SHARED_FS_OK"
