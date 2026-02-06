#!bin/bash

### Kill all the processes in case of Ctrl+C

cleanup() {
  rm 200
  echo "Killing all the processes"
  pkill -P $$
  exit 0
}

trap cleanup SIGINT SIGTERM

VERSION=1 ## Version number of the tool

CONFIGID=$1

INPUTFILE="./experimentalSetup/random/random_set_${CONFIGID}.json"

if [[ ! -f $INPUTFILE ]]; then
    echo "Configuration file doesn't exist"
    exit 1
fi

THREAD_NUMBER=$(jq -r '.thread_number' $INPUTFILE)
START_NB_THREAD=$(jq -r '.start_nb_thread' $INPUTFILE)

TIMEOUT_SYSTEM_GENERATION=$(jq -r '.timeout_system_generation' $INPUTFILE)
TIMEOUT_FULL_COMPUTATION=$(jq -r '.timeout_full_computation' $INPUTFILE)

PERMUTATION=$(jq -r '.permutation' $INPUTFILE)
PERMUTATION_CONF_NB=$(jq -r '.permutation_conf_number' $INPUTFILE)
PERMUTATION_SET_NB=$(jq -r '.permutation_set_number' $INPUTFILE)

NUMBER_TEST_COMPARISON=$(jq -r '.number_test' $INPUTFILE)

DIRRES="results/comparisons"
mkdir -p $DIRRES

DIRCOMPARE="results/benchmark"

FOLDER_WORKING="./${DIRRES}/random_compare_${PERMUTATION}_set_${PERMUTATION_CONF_NB}_${PERMUTATION_SET_NB}"

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

FOLDER_TO_COMPARE="./${DIRCOMPARE}/${PERMUTATION}_set_${PERMUTATION_CONF_NB}_${PERMUTATION_SET_NB}"

exec > $FOLDER_WORKING/logs/global.log 2>&1

chmod 777 ./comparisons_random/random_comparison_parameters.py

python3 ./comparisons_random/random_comparison_parameters.py $FOLDER_TO_COMPARE $FOLDER_WORKING $NUMBER_TEST_COMPARISON ## Generate and perform algebraic attack on random ideals to compare to systems corresponding to algebraic attacks on primitives

### Take advantage of multithreading

for ((i=$START_NB_THREAD; i<$THREAD_NUMBER+$START_NB_THREAD; i++)); do
  taskset -c "$i" bash ./comparisons_random/perform_experiments_per_thread.sh $FOLDER_WORKING $TIMEOUT_SYSTEM_GENERATION $TIMEOUT_FULL_COMPUTATION &
  PIDS+=($!)
done
for pid in "${PIDS[@]}"; do
  wait "$pid"
done

rm -f $FOLDER_WORKING/200 $FOLDER_WORKING/ids.lock

wait 

echo "All experiments done !"