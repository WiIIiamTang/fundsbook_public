import logging
import json
import os
from PyQt5 import QtCore
from PyQt5.QtCore import QThreadPool
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QStatusBar,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QMainWindow,
    QWidget,
    QFileDialog,
    QDesktopWidget,
    QPlainTextEdit,
    QProgressBar,
    QSizePolicy,
    QTabWidget,
    QSpacerItem,
)
from ..workers import (
    EastMoneyFundScraper,
    WorkbookManager,
    start,
    buy_funds_from_workbook,
)
from ..constants import BASE_PATH
from .ThreadWorker import ThreadWorker
from .Translator import Translator


class ThreadFlag:
    """
    Holds a boolean flag that can be used to communicate with worker
    threads.
    """

    def __init__(self, initial_flag: bool = True):
        self.flag = initial_flag


class MainUi(QMainWindow):
    """
    Represents the main window for the app
    Holds the thread pool that runs background processes
    (web scraper)
    """

    def __init__(self, **kwargs):
        """
        Initializes the main window according to the config settings
        """
        super().__init__()

        ##########################################################################
        # initial language is set
        self.lang = kwargs.get("lang", "en")
        self.translator = Translator(self.lang)
        self.create_t = self.translator.get_translation_function()

        ###########################################################################
        # This flag indicates whether or not to continue running ThreadWorkers
        # Any long-running function (ie. a web scraper that pauses between requests) will be
        # that is run in the threadpool should check this periodically. The instructions
        # are given by:
        #   True: continue running
        #   False: return and cleanly exit when possible
        self.run_threads = ThreadFlag()

        ###########################################################################
        # Window
        self.setWindowTitle("楚枫基金管家")
        self.defaultWorkbookName = kwargs.get("defaultWorkbookName")
        dimensions = kwargs.get("dimensions")

        if kwargs.get("fixed_size"):
            self.setFixedSize(dimensions[0], dimensions[1])
        else:
            self.setGeometry(0, 0, dimensions[0], dimensions[1])

        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        ###########################################################################
        # Init web scraper
        self.scraper_settings = {
            "driver": kwargs.get("driver"),
            "options_arguments": ["--headless"],
            "request_pause": kwargs.get("request_pause"),
            "random_pauses": False,
        }
        if kwargs.get("startDriverOnStartup"):
            self.scraper = EastMoneyFundScraper(
                driver=kwargs.get("driver"),
                driver_options_arguments=["--headless"],
                request_pause=kwargs.get("request_pause"),
                random_pauses=False,
            )
            self.scraper.start_driver()

        ###########################################################################
        # Create visuals
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self.tabs = QTabWidget()
        self._createDisplay()  # main ui elements
        self._createStatus()  # bottom status bar
        self._createInfoBox()  # lower log box
        self._createSettings()  # settings tab
        self._createBuyTab()  # buy tab

        self.tabs.addTab(self.display, "Tasks")
        self.tabs.addTab(self.buytab, "Buy Funds")
        # self.tabs.addTab(self.infoTextBox, "Logs")
        self.tabs.addTab(self.settingstab, "Settings")

        self.generalLayout.addWidget(self.tabs)
        self.generalLayout.addWidget(self.infoTextBox)

        ###########################################################################
        # Thread pool
        self.threadpool = QThreadPool()
        self.threads_are_running = False
        logging.info(
            f"(Init pyqt window) app is running with maximum {self.threadpool.maxThreadCount()} threads"
        )
        self.infoTextBox.appendPlainText(
            f"(Init pyqt window) app is running with maximum {self.threadpool.maxThreadCount()} threads"
        )

        ###########################################################################
        # Load user settings
        self._loadPreferences()

    def _createBuyTab(self):
        self.buytab = QWidget()

        t = self.create_t("buy-funds")
        buy_label = QLabel(t("Buy funds"), parent=self.display)
        buy_label.setStyleSheet(
            "padding-top: 10px; border-top: 2px solid gray; font-size: 14px"
        )

        buy_funds_layout = QGridLayout()
        buy_funds = self.buytab
        buy_funds_layout.addWidget(buy_label, 0, 0, 1, 3)

        self.fund_id_box = QLineEdit(buy_funds)
        self.fund_id_box.setPlaceholderText(t("Fund id"))
        self.amount_box = QLineEdit(buy_funds)
        self.amount_box.setPlaceholderText(t("Amount $"))
        self.date_box = QLineEdit(buy_funds)
        self.date_box.setPlaceholderText(t("Date"))
        self.buy_button = QPushButton(t("Buy"), parent=buy_funds)
        self.buy_button.clicked.connect(self.buy_funds)

        buy_funds_layout.addWidget(self.fund_id_box, 1, 0)
        buy_funds_layout.addWidget(self.amount_box, 1, 1)
        buy_funds_layout.addWidget(self.date_box, 1, 2)
        buy_funds_layout.addWidget(self.buy_button, 2, 1)

        # Add spacer
        buy_funds_layout.addItem(QSpacerItem(20, 200), 3, 0)

        buy_funds.setLayout(buy_funds_layout)

    def _createSettings(self):
        t = self.create_t("settings")
        self.settingstab = QWidget()

        settings_label = QLabel(
            t("Settings (**requires restart)"), parent=self.settingstab
        )
        # settings_label.setStyleSheet(
        #     "padding-top: 10px; border-top: 2px solid gray; font-size: 14px"
        # )

        settings_layout_grid = QGridLayout()
        settings_layout_grid.addWidget(settings_label, 0, 0, 1, 5)
        settings = self.settingstab

        self.driver_startup = QCheckBox(
            t("**Start driver automatically"), parent=self.settingstab
        )
        self.setting_export_data = QCheckBox(
            t("Export data to JSON at end of updates"), parent=self.settingstab
        )
        self.setting_request_pause = QLineEdit(self.display)
        self.setting_request_pause.setText("5")
        self.setting_request_pause.setFixedWidth(50)
        self.language_selector = QComboBox(parent=self.settingstab)
        self.language_selector.setFixedWidth(100)
        self.language_selector.addItems(["English", "Chinese", "French"])
        self.setting_funds = QCheckBox(
            t("Run updates on Funds sheet (基金日记)"), parent=self.settingstab
        )
        self.setting_rankings = QCheckBox(
            t("Run updates on Rankings sheet (基金排队)"), parent=self.settingstab
        )
        self.setting_top50 = QCheckBox(
            t("Run updates on all top50 sheets (各类基金前50名)"), parent=self.settingstab
        )
        self.theme = QCheckBox(t("**Dark theme"), parent=self.settingstab)

        settings_layout_grid.addWidget(self.driver_startup, 1, 0)
        settings_layout_grid.addWidget(self.setting_export_data, 2, 0)
        settings_layout_grid.addWidget(
            QLabel(t("**Web scraper pause duration between requests")), 3, 0
        )
        settings_layout_grid.addWidget(self.setting_request_pause, 3, 1)
        settings_layout_grid.addWidget(
            QLabel(t("**Language"), parent=self.settingstab), 4, 0, 1, 1
        )
        settings_layout_grid.addWidget(self.language_selector, 5, 0, 2, 1)
        settings_layout_grid.addWidget(self.theme, 7, 0, 1, 1)
        settings_layout_grid.addWidget(self.setting_funds, 8, 0)
        settings_layout_grid.addWidget(self.setting_rankings, 9, 0)
        settings_layout_grid.addWidget(self.setting_top50, 10, 0)

        settings_layout_grid.setHorizontalSpacing(10)
        settings_layout_grid.addItem(QSpacerItem(20, 100), 11, 0)
        settings.setLayout(settings_layout_grid)

    def _createDisplay(self):
        # The main display will be a VBox
        self.display = QWidget(self._centralWidget)
        display_layout = QVBoxLayout()
        t = self.create_t("workbook-intro")

        # Intro text
        intro_text = QLabel(
            t("Choose the workbook and click run to start the scraper."),
            parent=self.display,
        )
        intro_text.setWordWrap(True)
        intro_text.setFont(QFont("Arial", 12))
        intro_text.setStyleSheet("border-bottom: 2px solid black")
        display_layout.addWidget(intro_text)

        # File selection button
        self.choose_btn = QPushButton(
            t("Choose excel workbook (.xlsx)"), parent=self.display
        )
        self.choose_btn.clicked.connect(self.getfile)
        self.choose_btn.setStyleSheet("color: red; font-size: 14px")
        self.choose_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        display_layout.addWidget(self.choose_btn, 2)

        # File selection text box
        display_layout.addWidget(QLabel(t("Selected file")))
        self.file_path_chosen = QLineEdit(self.display)
        self.file_path_chosen.setReadOnly(True)
        self.file_path_chosen.setText(self.defaultWorkbookName)
        display_layout.addWidget(self.file_path_chosen)

        # Three horizontal buttons grouped together:
        # start scraper, start driver, stop driver
        t = self.create_t("core")
        gridbuttons = QWidget(self.display)
        gridbuttons_layout = QGridLayout()

        self.start_btn = QPushButton(
            t("Run scraper and update sheets"), parent=self.display
        )
        self.start_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.start_btn.setStyleSheet("color: red; font-size: 20px")
        self.start_btn.clicked.connect(self.start_workbook_jobs)
        gridbuttons_layout.addWidget(self.start_btn, 0, 1, 2, 1)

        self.start_driver_btn = QPushButton(t("Start web driver"), parent=self.display)
        self.start_driver_btn.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Expanding
        )
        self.start_driver_btn.setStyleSheet("color: red; font-size: 14px")
        self.start_driver_btn.clicked.connect(self.start_web_driver)
        gridbuttons_layout.addWidget(self.start_driver_btn, 0, 0)

        self.stop_driver_btn = QPushButton(t("Stop web driver"), parent=self.display)
        self.stop_driver_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.stop_driver_btn.setStyleSheet("color: red; font-size: 14px")
        self.stop_driver_btn.clicked.connect(self.stop_web_driver)
        gridbuttons_layout.addWidget(self.stop_driver_btn, 1, 0)

        gridbuttons.setLayout(gridbuttons_layout)
        display_layout.addWidget(gridbuttons, 5)

        # Progress bar
        plabel = QLabel(t("Progress"))
        plabel.setStyleSheet("font-size: 14px")
        display_layout.addWidget(plabel)

        pgrid = QGridLayout()
        self.progress_bar = QProgressBar(self.display)
        self.progress_bar.setMaximum(10)
        self.progress_bar.setValue(0)
        pgrid.addWidget(self.progress_bar, 0, 0)

        self.plabel_current = QLabel("Task")
        self.plabel_current.setAlignment(QtCore.Qt.AlignCenter)
        pgrid.addWidget(self.plabel_current, 0, 0)

        display_layout.addLayout(pgrid)

        # Stop button
        self.stop_btn = QPushButton(t("Stop"), parent=self.display)
        self.stop_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.stop_btn.setStyleSheet("border-color: red")
        self.stop_btn.clicked.connect(self.stop_workers)
        display_layout.addWidget(self.stop_btn, 1)

        # Buy funds
        # t = self.create_t("buy-funds")
        # buy_label = QLabel(t("Buy funds"), parent=self.display)
        # buy_label.setStyleSheet(
        #     "padding-top: 10px; border-top: 2px solid gray; font-size: 14px"
        # )
        # display_layout.addWidget(buy_label, 1)

        # buy_funds_layout = QGridLayout()
        # buy_funds = QWidget(self.display)

        # self.fund_id_box = QLineEdit(buy_funds)
        # self.fund_id_box.setPlaceholderText(t("Fund id"))
        # self.amount_box = QLineEdit(buy_funds)
        # self.amount_box.setPlaceholderText(t("Amount $"))
        # self.date_box = QLineEdit(buy_funds)
        # self.date_box.setPlaceholderText(t("Date"))
        # self.buy_button = QPushButton(t("Buy"), parent=buy_funds)
        # self.buy_button.clicked.connect(self.buy_funds)

        # buy_funds_layout.addWidget(self.fund_id_box, 0, 0)
        # buy_funds_layout.addWidget(self.amount_box, 0, 1)
        # buy_funds_layout.addWidget(self.date_box, 0, 2)
        # buy_funds_layout.addWidget(self.buy_button, 1, 1)

        # buy_funds.setLayout(buy_funds_layout)
        # display_layout.addWidget(buy_funds, 1)

        # settings menu
        # t = self.create_t("settings")
        # settings_label = QLabel(t("Settings (**requires restart)"), parent=self.display)
        # settings_label.setStyleSheet(
        #     "padding-top: 10px; border-top: 2px solid gray; font-size: 14px"
        # )
        # display_layout.addWidget(settings_label, 1)

        # settings_layout = QGridLayout()
        # settings = QWidget(self.display)

        # self.driver_startup = QCheckBox(
        #     t("**Start driver automatically"), parent=self.display
        # )
        # self.setting_export_data = QCheckBox(
        #     t("Export data to JSON at end of updates"), parent=self.display
        # )
        # self.setting_request_pause = QLineEdit(self.display)
        # self.setting_request_pause.setText("5")
        # self.setting_request_pause.setFixedWidth(50)
        # self.language_selector = QComboBox(parent=self.display)
        # self.language_selector.setFixedWidth(100)
        # self.language_selector.addItems(["English", "Chinese", "French"])
        # self.setting_funds = QCheckBox(
        #     t("Run updates on Funds sheet (基金日记)"), parent=self.display
        # )
        # self.setting_rankings = QCheckBox(
        #     t("Run updates on Rankings sheet (基金排队)"), parent=self.display
        # )
        # self.setting_top50 = QCheckBox(
        #     t("Run updates on all top50 sheets (各类基金前50名)"), parent=self.display
        # )

        # settings_layout.addWidget(self.driver_startup, 0, 0)
        # settings_layout.addWidget(self.setting_export_data, 1, 0)
        # settings_layout.addWidget(
        #     QLabel(
        #         t("**Web scraper pause duration between requests"), parent=self.display
        #     ),
        #     2,
        #     0,
        #     1,
        #     1,
        # )
        # settings_layout.addWidget(self.setting_request_pause, 3, 0)
        # settings_layout.addWidget(
        #     QLabel(t("**Language"), parent=self.display), 0, 2, 1, 1
        # )
        # settings_layout.addWidget(self.language_selector, 1, 2, 2, 1)
        # settings_layout.addWidget(self.setting_funds, 0, 1)
        # settings_layout.addWidget(self.setting_rankings, 1, 1)
        # settings_layout.addWidget(self.setting_top50, 2, 1)

        # settings_layout.setHorizontalSpacing(20)
        # settings.setLayout(settings_layout)
        # display_layout.addWidget(settings, 1)

        # add the main display to the general layout
        self.display.setLayout(display_layout)
        self.generalLayout.addWidget(self.display)

    def _createInfoBox(self):
        self.infoTextBox = QPlainTextEdit(self._centralWidget)
        self.infoTextBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.infoTextBox.resize(1024, 100)
        self.infoTextBox.setFixedHeight(100)
        self.infoTextBox.setReadOnly(True)
        # self.generalLayout.addWidget(self.infoTextBox)

    def _createStatus(self):
        self.status = QStatusBar()
        self.status.showMessage(
            f'楚枫基金管家 | Web driver status: {"ON" if hasattr(self, "scraper") and self.scraper.is_on else "OFF"}'
        )
        self.setStatusBar(self.status)

    def _workerDone(self):
        self.status.showMessage("thread done")
        self.infoTextBox.appendPlainText("worker thread done")
        self.threads_are_running = False

    def _workerProgress(self, s):
        """
        Displays worker progress log messages onto the ui
        These messages are NOT translatable.
        """
        if s.startswith("PROG:"):
            print(s.strip("PROG:"))
            self.plabel_current.setText(s.strip("PROG:"))
        else:
            self.status.showMessage(s)
            self.infoTextBox.appendPlainText(s)

    def _workerProgressNum(self, n):
        # print(n)
        # print(f'progress bar current: {self.progress_bar.value()}')
        if n == -1:
            self.progress_bar.setValue(self.progress_bar.value() + 1)
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(n)

    def _workerResult(self, obj):
        if type(obj) is bool:
            if obj:
                self.infoTextBox.appendPlainText("The thread exited correctly")
            else:
                self.infoTextBox.appendPlainText("The thread did not exit correctly")

    def _savePreferences(self):
        settings = {}
        lang_short = {"English": "en", "Chinese": "cn", "French": "fr"}
        with open(
            os.path.join(BASE_PATH, "fb_config.json"), "r", encoding="utf-8"
        ) as f:
            settings = json.load(f)
            settings["startDriverOnStartup"] = self.driver_startup.isChecked()
            settings["darkTheme"] = self.theme.isChecked()
            settings["exportDataAtEnd"] = self.setting_export_data.isChecked()
            settings["runFunds"] = self.setting_funds.isChecked()
            settings["runRankings"] = self.setting_rankings.isChecked()
            settings["runTop50"] = self.setting_top50.isChecked()
            settings["defaultLang"] = lang_short[
                self.language_selector.itemText(self.language_selector.currentIndex())
            ]
            settings["requestPause"] = int(self.setting_request_pause.text())

        with open(
            os.path.join(BASE_PATH, "fb_config.json"), "w", encoding="utf-8"
        ) as f:
            f.write(json.dumps(settings, indent=4))

    def _loadPreferences(self):
        settings = {}
        with open(
            os.path.join(BASE_PATH, "fb_config.json"), "r", encoding="utf-8"
        ) as f:
            settings = json.load(f)

        self.driver_startup.setChecked(settings["startDriverOnStartup"])
        self.setting_export_data.setChecked(settings["exportDataAtEnd"])
        self.setting_funds.setChecked(settings["runFunds"])
        self.setting_rankings.setChecked(settings["runRankings"])
        self.setting_top50.setChecked(settings["runTop50"])
        self.theme.setChecked(settings["darkTheme"])
        self.language_selector.setCurrentIndex(
            ["en", "cn", "fr"].index(settings["defaultLang"])
        )
        self.setting_request_pause.setText(str(settings["requestPause"]))

    def getfile(self):
        """Chooses a file and sets the text box to the path of the file"""
        dlg = QFileDialog()
        fname = dlg.getOpenFileName(
            self, "Open file", filter="Excel VBA (*.xlsm);;Excel Workbooks (*.xlsx)"
        )
        self.file_path_chosen.setText(fname[0])
        self.infoTextBox.appendPlainText(f"Set path to {self.file_path_chosen.text()}")

    def stop_workers(self):
        """
        Sets the run_threads flag to false.
        All functions running through the threadpool should be checking this
        flag periodically, and should exit cleanly when possible.
        """
        self.run_threads.flag = False
        self.infoTextBox.appendPlainText(
            "-------- Sending exit code to threads: wait a couple of seconds for it to finish -------------"
        )
        self.status.showMessage(
            "Issued exit to threads. It may take a couple of seconds to complete."
        )
        self.threads_are_running = False

    def start_workbook_jobs(self):
        """Starts all three workbook jobs (funds, ranking, top)"""
        if self.threads_are_running:
            self.infoTextBox.appendPlainText("There is already a job in progress")
            self.status.showMessage("There is already a job in progress")
        elif hasattr(self, "scraper") and self.scraper.is_on:
            self.infoTextBox.appendPlainText("Starting all workbook jobs")
            self.status.showMessage("Web scraper starting")
            self.workbook_manager = WorkbookManager(
                self.file_path_chosen.text(), backup=False
            )
            self.run_threads.flag = True

            worker = ThreadWorker(
                start,
                self.scraper,
                self.workbook_manager,
                self.run_threads,
                self.setting_export_data.isChecked(),
                self.setting_funds.isChecked(),
                self.setting_rankings.isChecked(),
                self.setting_top50.isChecked(),
            )

            # connect the FINISHED signal
            worker.signals.finished.connect(self._workerDone)

            # connect the PROGRESS signal (str)
            worker.signals.progress.connect(self._workerProgress)

            # connect the PROGRESS_NUM signal (int)
            worker.signals.progress_num.connect(self._workerProgressNum)

            # connect the RESULT signal (object)
            worker.signals.result.connect(self._workerResult)

            self.threadpool.start(worker)
            self.threads_are_running = True
        else:
            self.infoTextBox.appendPlainText(
                "Web driver is not on. Start the driver before running."
            )
            self.status.showMessage("Error starting tasks")

    def start_web_driver(self):
        """Starts the web driver"""
        if hasattr(self, "scraper") and self.scraper.is_on:
            self.infoTextBox.appendPlainText("The web driver is already on")
            self.status.showMessage("Error starting web driver")
        else:
            self.scraper = EastMoneyFundScraper(
                driver=self.scraper_settings["driver"],
                driver_options_arguments=self.scraper_settings["options_arguments"],
                request_pause=self.scraper_settings["request_pause"],
                random_pauses=self.scraper_settings["random_pauses"],
            )
            self.infoTextBox.appendPlainText("Started web driver")
            self.status.showMessage("Started web driver")
            self.scraper.start_driver()

    def stop_web_driver(self):
        """Stops the web driver"""
        if hasattr(self, "scraper"):
            if not self.scraper.is_on:
                self.infoTextBox.appendPlainText("The web driver is already off")
                self.status.showMessage("Error stopping web driver")
            else:
                self.scraper.stop_driver()
                self.infoTextBox.appendPlainText("Stopped web driver")
                self.status.showMessage("Stopped web driver")
        else:
            self.infoTextBox.appendPlainText("There is no web driver started")
            self.status.showMessage("Error stopping web driver")

    def buy_funds(self):
        """Adds an entry to the spreadsheet for that fund and date"""
        self.infoTextBox.appendPlainText(
            f"Trying to buy the funds selected {self.fund_id_box.text()}, {self.amount_box.text()}, {self.date_box.text()}"
        )
        self.status.showMessage("Trying to buy the funds selected")

        if self.threads_are_running:
            self.infoTextBox.appendPlainText("There is already a job in progress")
            self.status.showMessage("Error starting buy funds")
        elif hasattr(self, "scraper") and self.scraper.is_on:
            self.workbook_manager = WorkbookManager(
                self.file_path_chosen.text(), backup=False
            )

            worker = ThreadWorker(
                buy_funds_from_workbook,
                self.workbook_manager,
                self.fund_id_box.text(),
                self.amount_box.text(),
                self.date_box.text(),
            )

            # connect the FINISHED signal
            worker.signals.finished.connect(self._workerDone)

            # connect the PROGRESS signal (str)
            worker.signals.progress.connect(self._workerProgress)

            self.threadpool.start(worker)
            self.threads_are_running = True
        else:
            self.infoTextBox.appendPlainText(
                "Web driver is not on. Start the driver before running."
            )
            self.status.showMessage("Error starting buy funds")

    def closeEvent(self, event):
        """
        Override the close event to also check if the web driver is still on first.
        The driver will be stopped first if it is on.
        """
        logging.info("Program exit")
        self.stop_workers()
        self._savePreferences()
        if hasattr(self, "scraper") and self.scraper.is_on:
            logging.warning(
                "(Program exit) web driver is still on. Stopping first then exiting..."
            )
            self.scraper.stop_driver()
            event.accept()
        else:
            event.accept()
