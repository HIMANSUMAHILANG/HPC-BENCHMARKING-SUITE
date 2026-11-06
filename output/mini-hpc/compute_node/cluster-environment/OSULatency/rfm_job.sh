#!/bin/bash
#SBATCH --job-name="rfm_OSULatency"
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --output=rfm_job.out
#SBATCH --error=rfm_job.err
#SBATCH --partition=High
module load hpl
module load osu
module load stream
module load openblas
module load gcc/13.0
module load mpi-5.0.10
export OMPI_MCA_btl_tcp_if_include=enp0s8
echo "========================================"
echo "          HPC BENCHMARK START            "
echo "========================================"
echo "JOB ID: $SLURM_JOB_ID"
echo "JOB NODELIST: $SLURM_JOB_NODELIST"
echo "NUMBER OF NODES: $SLURM_JOB_NUM_NODES"
echo "NUMBER OF TASKS: $SLURM_NTASKS"
echo "TASKS PER NODE: $SLURM_TASKS_PER_NODE"
echo "========================================"
srun --cpus-per-task=1 --mpi=pmix_v3 osu_latency
