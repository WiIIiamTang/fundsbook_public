#!/usr/bin/bash

# git tag the commit for release
appver=$1
launcherapp=$2
channel=$3
channelver=$4

if [[ $appver == '' && $launcherapp == '' ]]; then
    echo "Please provide the app version and launcher version"
    exit 1
fi

if [[ $channel == '' && $channelver == '' ]]; then
    echo "Please provide the channel"
    exit 1
fi

tag="v$appver-$channel.$channelver+lu--$launcherapp"

echo "Tagging release $tag"
echo "Continue? (y/n)"
read -r response

if [[ $response == 'y' ]]; then
    git tag -a $tag -m "auto-tagged release $tag"
    # open the VERSION file and update the version
    echo "Updating VERSION file"
    echo "$appver-$channel.$channelver" > VERSION
    mv -f VERSION app/VERSION
    # open the VERSION file and update the launcher version
    echo "Updating launcher VERSION file"
    echo "$launcherapp" > VERSION
    mv -f VERSION launcher/VERSION
    echo "Ready for release!"
else
    echo "Aborting"
fi