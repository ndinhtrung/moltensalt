#!/bin/bash
#SBATCH --job-name=salt_append
#SBATCH --account=project_2004485
#SBATCH --partition=medium
#SBATCH --time=00:30:00
#SBATCH --nodes=1
#SBATCH --array=0-3
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/append_salt_%A_%a.out
#SBATCH --error=logs/append_salt_%A_%a.err

module load python-data
cd /scratch/project_2004485/trungnguyen/GG_FUNDAMAT/moltensalt/simulations/3d_validation/Ni5Cr

python3 -u append_salt_parallel.py