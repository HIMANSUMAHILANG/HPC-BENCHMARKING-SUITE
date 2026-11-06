#!/bin/bash
#SBATCH --job-name="rfm_stream_test"
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=2
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
export OMP_NUM_THREADS=2
export OMP_PROC_BIND=close
export OMP_PLACES=cores
srun --cpus-per-task=1 /mnt/shared/test35/hpc-reframe/input/stream
