#!/bin/bash
#SBATCH --job-name="rfm_osu_bandwidth_test_70b90ff0"
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --output=rfm_job.out
#SBATCH --error=rfm_job.err
#SBATCH --partition=High
#SBATCH --nodelist=master,compute2
module load hpl
module load osu
module load stream
module load openblas
module load gcc/13.0
module load mpi-5.0.10
module load gcc
module load mpi-5.0.10
module load osu
srun --cpus-per-task=1 osu_bw -m 1048576:1048576 -x 100 -i 1000
