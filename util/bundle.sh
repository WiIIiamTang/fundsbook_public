#!/usr/bin/bash

# get the name of the release folder
if [ -z "$1" ]; then
    echo "No release folder name provided, using default fundbook_release"
    release_folder="fundbook_release"
else
    release_folder=$1
fi

echo "Bundling $release_folder to releases"

# create the releases folder if it doesn't exist
if [ ! -d "releases" ]; then
    mkdir releases
fi
rm -rf release/$release_folder
mkdir release/$release_folder

cp -r dist/* release/$release_folder

python util/create_shortcut_windows.py "Start Fundsbook.lnk" "release/$release_folder/launcher/launcher.exe" "release/$release_folder"