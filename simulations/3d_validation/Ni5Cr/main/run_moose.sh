#!/bin/bash
#SBATCH --job-name=moltensalt_Ni5Cr_diff1

#SBATCH --account=project_2004485
#SBATCH --partition=medium
#SBATCH --time=00:30:00

#SBATCH --nodes=4
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=1

#SBATCH --output=logs/moltensalt_Ni5Cr_diff1_%A.out
#SBATCH --error=logs/moltensalt_Ni5Cr_diff1_%A.err

module purge
module load gcc/13.1.0 openblas/0.3.18-omp csc-tools cmake/3.21.4

APP_NAME=test_corrosion
BASE_DIR=/scratch/$SLURM_JOB_ACCOUNT/trungnguyen/GG_FUNDAMAT/moltensalt/simulations/3d_validation/Ni5Cr/lit_diff1
MOOSE_DIR=/scratch/$SLURM_JOB_ACCOUNT/moose

echo
echo Started at time: $(date)
echo

cd $BASE_DIR
echo Working in $PWD
echo Running on $SLURM_JOB_NUM_NODES nodes with $SLURM_NTASKS_PER_NODE tasks per node and $SLURM_CPUS_PER_TASK threads per task.
echo

srun -n $SLURM_NTASKS $MOOSE_DIR/$APP_NAME/$APP_NAME-opt -i ebsd_reader.i --n_threads=$SLURM_CPUS_PER_TASK

echo
echo Finished at time: $(date)
echo