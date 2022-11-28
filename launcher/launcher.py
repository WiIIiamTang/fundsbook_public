from src.gui import MainUi
from PyQt5.QtWidgets import QApplication
import sys


def main():
    print("hello launcher")
    app = QApplication(sys.argv)
    ui = MainUi()
    ui.show()
    app.exit(app.exec_())


if __name__ == "__main__":
    main()
