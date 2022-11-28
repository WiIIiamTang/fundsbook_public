#!/usr/bin/bash

# This script is used to run different options
if [[ $1 == 'app' ]]; then
    echo "Running app"
    python app/app.py
elif [[ $1 == 'launcher' ]]; then
    echo "Running launcher"
    python launcher/launcher.py
elif [[ $1 == 'build' ]]; then
    ./util/build.sh
    ./util/bundle.sh
elif [[ $1 == 'test' ]]; then
    echo "Running tests"
    # run tests with pytest
    pytest tests
else
    echo "Invalid option"
fi