import time
import sys
import os
from subprocess import Popen
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QPushButton,
    QDesktopWidget,
    QLabel,
)

from ..updater import Updater
from ..constants import BASE_PATH, PROD


class MainUi(QMainWindow):
    def __init__(self, **kwargs):
        super().__init__()
        self.updater = Updater(
            "https://api.github.com/repos/yourusername/yourrepo/releases/latest"
        )
        self.version = "0.0.1"
        self.setWindowTitle("Launcher")
        self.setFixedSize(300, 300)
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self.display = QWidget(self._centralWidget)
        self._createLaunchBox()

    def _createLaunchBox(self):
        self.launchBox = QWidget(self._centralWidget)
        display_layout = QVBoxLayout()

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_btn_action)
        display_layout.addWidget(self.start_btn)

        self.check_update_btn = QPushButton("Check for updates")
        self.check_update_btn.clicked.connect(self.check_update_btn_action)
        display_layout.addWidget(self.check_update_btn)

        self.close_btn = QPushButton("Exit")
        self.close_btn.clicked.connect(self.close_launcher)
        display_layout.addWidget(self.close_btn)

        self.info = QLabel(self.version)
        self.info.setWordWrap(True)
        self.info.setFont(QFont("Arial", 11))
        display_layout.addWidget(self.info)

        self.display.setLayout(display_layout)
        self.generalLayout.addWidget(self.display)

    def close_launcher(self):
        self.close()

    def check_update_btn_action(self):
        self.updater.check()
        print("checking for updates")

    def start_btn_action(self):
        if PROD:
            print("launching prod")
            # print the current working directory
            print("cwd: ", os.getcwd())
            print(sys._MEIPASS)
            print(os.path.join(sys._MEIPASS, ".."))
            time.sleep(1)
            app_path = os.path.abspath(
                os.path.join(os.path.join(BASE_PATH, ".."), "app", "app.exe")
            )
            print(app_path)
            Popen([app_path])
        else:
            print("launching dev")
            Popen(
                ["python", os.path.join(os.path.join(BASE_PATH, ".."), "app", "app.py")]
            )
        self.showMinimized()
