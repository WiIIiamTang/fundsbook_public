#!/usr/bin/bash

# git tag the commit for release
appver=$1
launcherapp=$2

if [[ $appver == '' && $launcherapp == '' ]]; then
    echo "Please provide the app version and launcher version"
    exit 1
fi

tag="v$appver+lu--$launcherapp"

echo "Tagging release $tag"
echo "Continue? (y/n)"
read -r response

if [[ $response == 'y' ]]; then
    # open the VERSION file and update the version
    echo "Updating VERSION file"
    echo "$appver" > VERSION
    mv -f VERSION app/VERSION
    # open the VERSION file and update the launcher version
    echo "Updating launcher VERSION file"
    echo "$launcherapp" > VERSION
    mv -f VERSION launcher/VERSION
    git add .
    git commit -m "bump to release $tag"
    git tag -a $tag -m "auto-tagged release $tag"
    echo "Ready for release!"
else
    echo "Aborting"
fi