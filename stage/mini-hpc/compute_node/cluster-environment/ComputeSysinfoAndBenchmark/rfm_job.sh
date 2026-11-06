#!/bin/bash
#SBATCH --job-name="rfm_ComputeSysinfoAndBenchmark"
#SBATCH --ntasks=1
#SBATCH --output=rfm_job.out
#SBATCH --error=rfm_job.err
#SBATCH --partition=High
module load gcc
module load mpi-5.0.10
echo "=== HOSTNAME & KERNEL ==="
hostname && uname -a
echo "=== CPU INFO ==="
lscpu | grep -E "Model name|Core\(s\) per socket|Socket\(s\)|Thread\(s\) per core"
echo "=== MEMORY INFO ==="
free -h
echo "=== PROG ENVIRONMENT ==="
module list
srun echo "main code"
