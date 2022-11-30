import sys
import os

PROD = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
if PROD:
    BASE_PATH = os.path.abspath(sys._MEIPASS)
else:
    BASE_PATH = os.path.join(os.getcwd(), "launcher")

# This should be the only place where the lu version is defined
with open(os.path.join(BASE_PATH, "VERSION")) as f:
    LAUNCHER_INTERNAL_VERSION = f.read().strip()

# get app internal version
with open(os.path.join(os.path.join(BASE_PATH, ".."), "app", "VERSION"), "r") as f:
    # app/VERSION should be the only place where the app version is defined
    APP_INTERNAL_VERSION = f.read().strip()
