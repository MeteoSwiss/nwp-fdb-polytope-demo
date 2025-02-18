#!/bin/bash
#
# Verifies that all of the notebook files have had the output cleared.
# This script can be used in a test as a test in CI to prevent github pushes
# of dirty notebooks.


export DIFF_FAIL=0
for filename in notebooks/*.ipynb; do
  jupyter nbconvert "$filename" --clear-output --output test-clear
  if diff "$filename" notebooks/test-clear.ipynb > /dev/null ; then
    echo "Notebook $filename is cleared."
  else
    echo "Notebook $filename was not cleared."
    DIFF_FAIL=1
  fi
  rm notebooks/test-clear.ipynb
done

exit $DIFF_FAIL

