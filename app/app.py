from PyQt5.QtWidgets import QApplication
from datetime import datetime
import sys
import os
import logging
import json

from src.gui import MainUi
from src.constants import BASE_PATH


def setup():
    with open(os.path.join(BASE_PATH, "fb_config.json"), "r") as f:
        settings = json.load(f)

    logging_settings = settings["logging"]
    logging.root.handlers = []
    handlers = []

    if logging_settings["streamToConsole"]:
        handlers.append(logging.StreamHandler())
    if logging_settings["saveLogs"]:
        handlers.append(
            logging.FileHandler(
                os.path.join(
                    BASE_PATH,
                    "logs",
                    f'log_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt',
                )
            )
        )

    logging.basicConfig(
        level=logging_settings["level"],
        format=logging_settings["format"],
        handlers=handlers,
    )

    return settings


def main():
    settings = setup()
    app = QApplication(sys.argv)
    ui = MainUi(
        fixed_size=settings["windowFixedSize"],
        dimensions=settings["windowDimensions"],
        defaultWorkbookName=settings["defaultWorkbookName"],
        startDriverOnStartup=settings["startDriverOnStartup"],
        lang=settings["defaultLang"],
        request_pause=settings["requestPause"],
        driver=settings["driver"],
    )
    ui.show()
    app.exit(app.exec_())


if __name__ == "__main__":
    main()
