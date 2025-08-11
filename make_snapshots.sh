#!/bin/bash
#
# Creates an HTML snapshot of the current state of the notebooks. Use this script
# to prepare examples of running the notebooks including the output.
#
# To also clear the output of the notebooks to prepare to commiting changes, pass
# in the -c option.

clear_outputs=false
make_snapshots=false

while getopts ":cs" option; do
    case $option in
        c) # Clear the notebook output
            clear_outputs=true;;
        s) # Snapshot the notebooks
            make_snapshots=true;;
        \?)
            echo "Usage: $0 [-c] [-s]"
            exit 1;;
    esac
done

if [ "${make_snapshots}" = true ] ; then
    mkdir tmp
    for filename in notebooks/**/*.ipynb; do
	if grep -E -q 'EmailKey|Bearer' "$filename"; then
            echo "Token found in the notebook. Exiting script."
            rm -r "$tmp"
            exit 1
        fi

        jupyter nbconvert "${filename}" --clear-output --output ../tmp/test-clear
        if diff "${filename}" tmp/test-clear.ipynb > /dev/null ; then
            read -p "${filename} has no output, do you still want to snapshot it? [y/N] " yn
            case $yn in
                [yY] )
                    ;;
                [nN] )
                    echo "skipping"
                    continue;;
                * )
                    echo "skipping"
                    continue;;
            esac
        fi
        jupyter nbconvert "${filename}" --to html --output-dir notebooks/snapshot
    done
    rm tmp/test-clear.ipynb
    rmdir tmp
fi

if [ "${clear_outputs}" = true ] ; then
    find notebooks -maxdepth 1 -name *ipynb -execdir \
        jupyter nbconvert --clear-output '{}' --output './{}' \;
fi

