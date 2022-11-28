#!/usr/bin/bash
if [[ $2 == "debug" ]]; then
    echo "Building with debug flags"
    app_spec="app/app_debug.spec"
    launcher_spec="launcher/launcher_debug.spec"
else
    app_spec="app/app.spec"
    launcher_spec="launcher/launcher.spec"
fi

if [[ $1 == "app" ]]; then
    echo "Building app:"
    pyinstaller $app_spec -y --clean
    echo "Done building app"
elif [[ $1 == "launcher" ]]; then
    echo "Building launcher:"
    pyinstaller $launcher_spec -y --clean
    echo "Done building launcher"
else
    echo "Building all..."
    echo "Building app:"
    pyinstaller $app_spec -y --clean
    echo "Building launcher:"
    pyinstaller $launcher_spec -y --clean
    echo "Done building all"
fi