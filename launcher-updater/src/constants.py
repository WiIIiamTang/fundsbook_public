import sys
import os

PROD = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
if PROD:
    BASE_PATH = os.path.abspath(os.path.dirname(__file__))
else:
    BASE_PATH = os.path.join(os.getcwd(), "launcher-updater")
