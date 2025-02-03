#!/bin/bash

rm -rf notebooks/cleaned
mkdir notebooks/cleaned
find notebooks/ -maxdepth 1 -name *ipynb -execdir \
  jupyter nbconvert --clear-output '{}' --output 'cleaned/{}' \;
