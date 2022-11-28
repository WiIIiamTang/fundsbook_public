import sys
import os

PROD = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
if PROD:
    BASE_PATH = os.path.abspath(sys._MEIPASS)
else:
    BASE_PATH = os.path.join(os.getcwd(), "launcher-updater")
LAUNCHER_INTERNAL_VERSION = "lu--0.1.0"
