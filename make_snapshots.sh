#!/bin/bash
#
# Creates an HTML snapshot of the current state of the notebooks. Use this script
# to prepare examples of running the notebooks including the output.
#
# To also clear the output of the notebooks to prepare to commiting changes, pass
# in the -c option.

CLEAR_OUTPUTS=false

while getopts ":c" option; do
  case $option in
    c) # Clear the notebook output
      CLEAR_OUTPUTS=true
      ;;
    \?)
      echo "Error: Invalid option"
      exit 1;;
  esac
done

for filename in notebooks/*.ipynb; do
  jupyter nbconvert "$filename" --clear-output --output test-clear
  if diff "$filename" notebooks/test-clear.ipynb > /dev/null ; then
    read -p "$filename has no output, do you still want to snapshot it? [y/N] " yn
    case $yn in
        [yY] )
            ;;
        [nN] )
            echo "skipping"
            continue
            ;;
        * )
            echo "skipping"
            continue
            ;;
    esac
  fi
  cp -f $filename notebooks/snapshot/
  jupyter nbconvert $filename --to html --output-dir notebooks/snapshot
done
rm notebooks/test-clear.ipynb

if [ "$CLEAR_OUTPUTS" = true ] ; then
    find notebooks -maxdepth 1 -name *ipynb -execdir \
      jupyter nbconvert --clear-output '{}' --output './{}' \;
fi

