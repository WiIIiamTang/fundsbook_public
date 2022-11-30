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
elif [[ $1 == 'test-dev' ]]; then
    echo "Running tests"
    # run tests with pytest
    TEST_ENV=dev pytest tests
elif [[ $1 == 'test-prod' ]]; then
    echo "Running tests"
    # run tests with pytest
    TEST_ENV=prod pytest tests
elif [[ $1 == 'tag' ]]; then
    echo "Tagging release"
    ./util/tag_release.sh $2 $3 $4 $5
else
    echo "Invalid option"
fi