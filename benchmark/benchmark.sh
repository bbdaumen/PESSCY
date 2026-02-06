#!bin/bash

### Kill all the processes in case of Ctrl+C

cleanup() {
  rm 200
  echo "Killing all the processes"
  pkill -P $$
  exit 0
}

trap cleanup SIGINT SIGTERM

VERSION=1 ## Version of the tool

PERMUTATION=$1
CONFIGID=$2
SETID=$3

INPUTFILE="./experimentalSetup/${PERMUTATION}/${PERMUTATION}_set_${CONFIGID}.json" ### JSON input file

if [[ ! -f $INPUTFILE ]]; then
    echo "Configuration file doesn't exist"
    exit 1
fi

THREAD_NUMBER=$(jq -r '.thread_number' $INPUTFILE)
START_NB_THREAD=$(jq -r '.start_nb_thread' $INPUTFILE)

TIMEOUT_SYSTEM_GENERATION=$(jq -r '.timeout_system_generation' $INPUTFILE)
TIMEOUT_FULL_COMPUTATION=$(jq -r '.timeout_full_computation' $INPUTFILE)

DIRRES="results/benchmark"
mkdir -p $DIRRES

FOLDER_WORKING="./${DIRRES}/${PERMUTATION}_set_${CONFIGID}_${SETID}" ### Folder where the results and logs are stored

if [[ -d "$FOLDER_WORKING" ]]; then
  echo "The folder ${FOLDER_WORKING} is going to be erased"
  read -r -p "Do you want to continue ? (y/n) [y] : " rep
  rep=${rep:-y}

  if [[ "$rep" != "y" && "$rep" != "Y" ]]; then
    echo "Aborted"
    exit 1
  fi
fi

rm -rf $FOLDER_WORKING/*
mkdir -p $FOLDER_WORKING
mkdir -p $FOLDER_WORKING/logs
mkdir -p $FOLDER_WORKING/res

cp $INPUTFILE $FOLDER_WORKING

exec > $FOLDER_WORKING/logs/global.log 2>&1

#### Generate the parameters for the experiment

chmod 777 ./benchmark/generate_parameters.py

python3 ./benchmark/generate_parameters.py $FOLDER_WORKING $INPUTFILE $PERMUTATION $VERSION ## Perform algebraic attacks on primitives

### Take advantage of multithreading

for ((i=$START_NB_THREAD; i<$THREAD_NUMBER+$START_NB_THREAD; i++)); do
  taskset -c "$i" bash ./benchmark/perform_experiments_per_thread.sh $FOLDER_WORKING $TIMEOUT_SYSTEM_GENERATION $TIMEOUT_FULL_COMPUTATION &
  PIDS+=($!)
done
for pid in "${PIDS[@]}"; do
  wait "$pid"
done

rm -f $FOLDER_WORKING/200 $FOLDER_WORKING/ids.lock

wait 

echo "All experiments done !"