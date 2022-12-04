#!/usr/bin/bash
if [[ $2 == "debug" ]]; then
    echo "Building with debug flags"
    app_spec="app/app_debug.spec"
    launcher_spec="launcher/launcher_debug.spec"
else
    app_spec="app/app.spec"
    launcher_spec="launcher/launcher.spec"
fi

launcher_updater_spec="launcher-updater/launcher-updater.spec"

if [[ $1 == "app" ]]; then
    echo "Building app:"
    pyinstaller $app_spec -y --clean
    echo "Done building app"
elif [[ $1 == "launcher" ]]; then
    echo "Building launcher:"
    pyinstaller $launcher_spec -y --clean
    echo "Done building launcher"
elif [[ $1 == "launcher_updater" ]]; then
    echo "Building launcher_updater:"
    pyinstaller $launcher_updater_spec -y --clean
    echo "Done building launcher_updater"
elif [[ $1 == "quick" ]]; then
    echo "Building all (not clean)..."
    echo "Building app:"
    pyinstaller $app_spec -y
    echo "Building launcher:"
    pyinstaller $launcher_spec -y
    echo "Building launcher_updater:"
    pyinstaller $launcher_updater_spec -y
    echo "Done building all"
else
    echo "Building all..."
    echo "Building app:"
    pyinstaller $app_spec -y --clean
    echo "Building launcher:"
    pyinstaller $launcher_spec -y --clean
    echo "Building launcher_updater:"
    pyinstaller $launcher_updater_spec -y --clean
    echo "Done building all"
fi