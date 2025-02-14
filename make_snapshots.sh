#!/bin/bash
#
# Creates an HTML snapshot of the current state of the notebooks. Use this script
# to prepare examples of running the notebooks including the output.
#
# To also clear the output of the notebooks to prepare to commiting changes, pass
# in the -c option.

rm -f notebooks/snapshot/*.ipynb
cp notebooks/*.ipynb notebooks/snapshot/
find notebooks -maxdepth 1 -name *ipynb -execdir \
  jupyter nbconvert '{}' --to html \;
mv notebooks/*.html notebooks/snapshot

while getopts ":c" option; do
  case $option in
    c) # Clear the notebook output
      find notebooks -maxdepth 1 -name *ipynb -execdir \
        jupyter nbconvert --clear-output '{}' --output './{}' \;
      exit;;
    \?)
      echo "Error: Invalid option"
      exit;;
  esac
done

