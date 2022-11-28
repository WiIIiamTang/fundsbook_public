import argparse
import time
import subprocess
import os
import sys
from src.updater import Updater
from src.constants import PROD


def main():
    print("hello launcher-updater")
    parser = argparse.ArgumentParser()
    parser.add_argument("version", type=str, help="current launcher version")
    parser.add_argument("base_path", type=str, help="abspath to parent directory")
    parser.add_argument("--cleanup_downloads", action="store_true")
    parser.add_argument("--use_cached", action="store_true")
    args = parser.parse_args()
    lu = Updater(
        "https://api.github.com/repos/WiIIiamTang/fundsbook_public/releases/latest",
        args.version,
        args.base_path,
        args.cleanup_downloads,
        args.use_cached,
    )
    lu.check()
    if lu.download():
        print("Update successful.")
        if PROD:
            subprocess.Popen([os.path.join(args.base_path, "launcher", "launcher.exe")])
            sys.exit(0)


if __name__ == "__main__":
    main()
    print("Exiting automatically in 3 seconds...")
    time.sleep(3)
