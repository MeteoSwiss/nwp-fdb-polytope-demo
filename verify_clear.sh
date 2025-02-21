#!/bin/bash
#
# Verifies that all of the notebook files have had the output cleared.
# This script can be used in a test as a test in CI to prevent github pushes
# of dirty notebooks.

diff_fail=0
mkdir tmp
for filename in notebooks/*.ipynb; do
    jupyter nbconvert "${filename}" --clear-output --output ../tmp/test-clear
    if diff "${filename}" tmp/test-clear.ipynb > /dev/null ; then
        echo "Notebook ${filename} is cleared."
    else
        echo "Notebook ${filename} was not cleared."
        diff_fail=1
    fi
    rm tmp/test-clear.ipynb
done
rmdir tmp

exit $diff_fail

