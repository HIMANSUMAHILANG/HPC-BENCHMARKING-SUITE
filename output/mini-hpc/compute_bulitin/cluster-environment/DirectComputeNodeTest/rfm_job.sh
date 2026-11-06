#!/bin/bash
module load hpl
module load osu
module load stream
module load openblas
module load gcc/13.0
module load mpi-5.0.10
ssh compute1 "hostname && lscpu | grep 'Model name' && free -h"
