#!/bin/bash

rm -rf clean_notebooks
mkdir clean_notebooks
find notebooks/ -maxdepth 1 -name *ipynb -execdir \
  jupyter nbconvert --clear-output '{}' --output '../clean_notebooks/{}' \;
