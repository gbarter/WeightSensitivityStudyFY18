#!/bin/bash
#PBS -l walltime=15:00:00          # WALLTIME limit
#PBS -l nodes=1                    # one node
#PBS -N execSpar                   # Name of job
#PBS -A WINDSE                     # project handle

cd $PBS_O_WORKDIR
source activate wisdem
python executeStudy.py



