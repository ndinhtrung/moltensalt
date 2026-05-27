#!/bin/bash
#SBATCH --job-name=moltensalt_Ni5Cr_diff1

#SBATCH --account=project_2004485
#SBATCH --partition=medium
#SBATCH --time=2:00:00

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=16

#SBATCH --output=logs/moltensalt_Ni5Cr_diff1_%A.out
#SBATCH --error=logs/moltensalt_Ni5Cr_diff1_%A.err

module purge
module load gcc/11.2.0 openmpi/4.1.2 openblas/0.3.18-omp csc-tools hdf5/1.10.7-mpi yaml-cpp/0.7.0 cmake/3.21.4
export PATH=/appl/opt/python/3.10.9-gnu112/bin:$PATH

PROJECT_ID=2004485
APP_NAME=test_corrosion
BASE_DIR=/scratch/project_$PROJECT_ID/trungnguyen/GG_FUNDAMAT/moltensalt/simulations/3d_validation/Ni5Cr/lit_diff1
MOOSE_DIR=/scratch/project_$PROJECT_ID/moose

echo
echo Started:
date
echo

cd $BASE_DIR
echo Working in $PWD.
echo

srun --ntasks=$SLURM_NTASKS $MOOSE_DIR/$APP_NAME/$APP_NAME-opt -i ebsd_reader.i --n_threads=$SLURM_CPUS_PER_TASK

echo
echo Finished:
date
echo