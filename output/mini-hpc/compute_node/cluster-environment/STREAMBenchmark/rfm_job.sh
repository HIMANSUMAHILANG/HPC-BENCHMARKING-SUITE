#!/bin/bash
#SBATCH --job-name="rfm_STREAMBenchmark"
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --output=rfm_job.out
#SBATCH --error=rfm_job.err
#SBATCH --partition=High
module load hpl
module load osu
module load stream
module load openblas
module load gcc/13.0
module load mpi-5.0.10
module load gcc/13.0
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
echo "STREAM THREADS: $OMP_NUM_THREADS"
echo "STREAM NODE: $(hostname)"
echo "========================================"
echo "          HPC BENCHMARK START            "
echo "========================================"
echo "JOB ID: $SLURM_JOB_ID"
echo "JOB NODELIST: $SLURM_JOB_NODELIST"
echo "NUMBER OF NODES: $SLURM_JOB_NUM_NODES"
echo "NUMBER OF TASKS: $SLURM_NTASKS"
echo "TASKS PER NODE: $SLURM_TASKS_PER_NODE"
echo "========================================"
srun --cpus-per-task=2 --mpi=pmix_v3 /mnt/shared/test35/hpc-reframe/input/stream
