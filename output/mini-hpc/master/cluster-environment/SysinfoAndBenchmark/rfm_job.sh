#!/bin/bash
module load hpl
module load osu
module load stream
module load openblas
module load gcc/13.0
module load mpi-5.0.10
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
echo "main code"
