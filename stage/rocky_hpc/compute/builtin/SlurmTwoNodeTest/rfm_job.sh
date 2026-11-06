#!/bin/bash
#SBATCH --job-name="rfm_SlurmTwoNodeTest"
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --output=rfm_job.out
#SBATCH --error=rfm_job.err
#SBATCH --time=0:2:0
#SBATCH --partition=High
srun --cpus-per-task=1 bash -c 
        set -eu

        echo "TASK_ID=$SLURM_PROCID"
        echo "NODE=$(hostname -s)"
        echo "JOB_ID=$SLURM_JOB_ID"

        case "$(hostname -s)" in
            compute1|compute2) ;;
            *)
                echo "UNEXPECTED_NODE"
                exit 1
                ;;
        esac

        echo "SLURM_TASK_OK"
