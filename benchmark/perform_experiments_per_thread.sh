#!/bin/bash

FOLDER_WORKING=$1
TIMEOUT_SYSTEM_GENERATION=$2
TIMEOUT_FULL_COMPUTATION=$3

STACK_FILE="./ids.txt"
LOCK_FILE="./ids.lock"

TEST_NUM="1"

chmod 777 ./benchmark/perform_experiments.py
chmod 777 ./utils/systems_solver.py

### Find the ID of the first experiment to perform from the list of experiments. The list of first ID is stored in ids.txt. 
### A locker is used to avoid two processes to write at the same time in the file.
### When the ids.txt file is empty, the process is stopped.

while [ "$TEST_NUM" -ne "0" ]; do

  cd $FOLDER_WORKING

  TEST_NUM=$(

      flock -x 200 bash -c '
      mapfile -t LINES < "$1"
      if [ "${#LINES[@]}" -eq 0 ]; then
      exit 1
      fi

      LAST="${LINES[-1]}"
      unset "LINES[-1]"
      printf "%s\n" "${LINES[@]}" > "$1"
      echo "$LAST"
  ' _ "$STACK_FILE"

  ) 200>"$LOCK_FILE"

  if [ -z "$TEST_NUM" ]; then
    break
  fi

  echo "PID $$ : First ID list : $TEST_NUM"

  ### Perform the experiments of the list to treat.

  cd ../../..

  python3 ./benchmark/perform_experiments.py $FOLDER_WORKING $TEST_NUM $TIMEOUT_SYSTEM_GENERATION $TIMEOUT_FULL_COMPUTATION

  done