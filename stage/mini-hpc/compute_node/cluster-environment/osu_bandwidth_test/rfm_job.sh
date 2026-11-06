#!/bin/bash
#SBATCH --job-name="rfm_osu_bandwidth_test"
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --output=rfm_job.out
#SBATCH --error=rfm_job.err
#SBATCH --partition=High
#SBATCH --nodelist=compute1,compute2
module load hpl
module load osu
module load stream
module load openblas
module load gcc/13.0
module load mpi-5.0.10
srun --cpus-per-task=1 --mpi=pmix_v3 osu_bw
