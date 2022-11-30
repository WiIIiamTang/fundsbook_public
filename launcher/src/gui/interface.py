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
from ..constants import BASE_PATH, PROD, LAUNCHER_INTERNAL_VERSION, APP_INTERNAL_VERSION


class MainUi(QMainWindow):
    def __init__(self, **kwargs):
        super().__init__()
        self.updater = Updater(
            "https://api.github.com/repos/WiIIiamTang/fundsbook_public/releases/latest"
        )
        self.app_version = APP_INTERNAL_VERSION
        self.lu_version = LAUNCHER_INTERNAL_VERSION
        self.channel = "stable"
        self.setWindowTitle("Fundbook Launcher")
        self.setFixedSize(300, 400)
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

        self.blank_info_box = QLabel("")
        display_layout.addWidget(self.blank_info_box)
        self.blank_info_box.setFont(QFont("Arial", 10))
        display_layout.addWidget(self.blank_info_box)

        self.install_update_btn = QPushButton("Install update")
        self.install_update_btn.clicked.connect(self.install_update)
        display_layout.addWidget(self.install_update_btn)
        self.install_update_btn.hide()

        self.formatted_info_text = f"Current version: {self.app_version} (app) {self.lu_version} (launcher)\
             \nLatest version: {'-' if self.updater.repo_version is None else self.updater.repo_version}\
             \nChannel: {self.channel}"
        self.info = QLabel(self.formatted_info_text)
        self.info.setWordWrap(True)
        self.info.setFont(QFont("Arial", 8))
        display_layout.addWidget(self.info)

        self.display.setLayout(display_layout)
        self.generalLayout.addWidget(self.display)

        self.check_update_btn_action()

    def close_launcher(self):
        self.close()

    def install_update(self):
        self.updater.install_update()
        print("update done, hiding button")
        self.install_update_btn.hide()
        self.check_update_btn_action()

    def check_update_btn_action(self):
        print("checking for updates")
        self.updater.check()
        print(self.updater)
        print(self.updater.new_app_update, self.updater.new_lu_update)
        self.app_version = self.updater.app_version
        self.lu_version = self.updater.local_version
        if self.updater.new_app_update or self.updater.new_lu_update:
            self.info.setText(
                f"Current version: {self.app_version} (app) {self.lu_version} (launcher)\
                 \nLatest version: {self.updater.repo_version}\
                 \nChannel: {self.channel}"
            )
            self.blank_info_box.setText(
                f"Update available:\
                \n{'- App' if self.updater.new_app_update else ''}\
                \n{'- Launcher (requires restart)' if self.updater.new_lu_update else ''}"
            )
            self.install_update_btn.show()
        else:
            print("no update available")
            self.info.setText(
                f"Current version: {self.app_version} (app) {self.lu_version} (launcher)\
                 \nLatest version: {self.updater.repo_version}\
                 \nChannel: {self.channel}"
            )
            self.blank_info_box.setText("No updates available")

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
