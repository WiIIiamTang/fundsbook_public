#!/usr/bin/bash

# get the name of the release folder
if [ -z "$1" ]; then
    echo "No release folder name provided, using default fundbook_release"
    release_folder="fundbook_release"
else
    release_folder=$1
fi

echo "Bundling $release_folder to releases"

rm -rf release/$release_folder
mkdir release/$release_folder

cp -r dist/launcher release/$release_folder
cp -r dist/app release/$release_folder

python util/create_shortcut_windows.py "fundsbook.lnk" "release/$release_folder/launcher/launcher.exe" "release/$release_folder"