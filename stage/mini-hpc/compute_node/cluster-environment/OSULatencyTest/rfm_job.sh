#!/bin/bash
#SBATCH --job-name="rfm_OSULatencyTest"
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --output=rfm_job.out
#SBATCH --error=rfm_job.err
#SBATCH --partition=High
#SBATCH --partition=High
#SBATCH --mpi=pmix_v3
#SBATCH --nodelist=compute1,compute2
module load hpl
module load osu
module load stream
module load openblas
module load gcc/13.0
module load mpi-5.0.10
export OMPI_MCA_btl_tcp_if_include=enp0s8
srun --cpus-per-task=2 osu_latency
