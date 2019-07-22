# This Python file uses the following encoding: utf-8
import sys
import time
from threading import Thread

try:
    from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QLineEdit, QCheckBox, \
    QProgressBar
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtCore import QFile, QObject
except ModuleNotFoundError:
    import pip
    import os

    f = None
    if hasattr(pip, "main"):
        f = pip.main
    else:
        from pip._internal import main

        f = main
    # win32api.MessageBox(0, 'Пожалуйста подождите',
    #                     'Пожалуйста, подождите, пока программа устанавливает необходимые библиотеки...', 0x00001000)
    print("Пожалуйста, подождите, пока программа устанавливает необходимые библиотеки...")
    f(["install", "PySide2"])
    # win32api.MessageBox(0, 'Установка завершена!', 'Запустите программу снова.', 0x00001000)
    print("Установка завершена! Запустите программу снова.")
    sys.exit()


class MainWindow(QObject):
    def __init__(self, ui_file, parent=None):
        super(MainWindow, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        dir_btn: QPushButton = self.window.findChild(QPushButton, "dir_choose_btn")
        dir_btn.clicked.connect(self.dir_btn_handler)

        self.dirPath: QLineEdit = self.window.findChild(QLineEdit, "dirPath")

        self.repeatFiles_dir: QLineEdit = self.window.findChild(QLineEdit, "repeatFiles_dir")
        self.singleFiles_dir: QLineEdit = self.window.findChild(QLineEdit, "singleFiles_dir")

        self.moveSingleFiles: QCheckBox = self.window.findChild(QCheckBox, "moveSingleFiles")
        self.moveRepeatFiles: QCheckBox = self.window.findChild(QCheckBox, "moveRepeatFiles")

        self.sortBar: QProgressBar = self.window.findChild(QProgressBar, "sortBar")
        self.sortBar.setValue(0)
        self.moveBar: QProgressBar = self.window.findChild(QProgressBar, "moveBar")
        self.moveBar.setValue(0)

        self.startButton: QPushButton = self.window.findChild(QPushButton, "startButton")
        self.startButton.clicked.connect(self.start_handler)
        self.stopButton: QPushButton = self.window.findChild(QPushButton, "stopButton")
        self.stopButton.clicked.connect(self.stop_handler)

        self.mainThread: Thread = None
        self.running = False

        self.window.destroyed.connect(self.stop_handler)
        self.window.show()

    def start_handler(self):
        self.running = True
        self.mainThread = Thread(target=self.main)
        self.mainThread.start()
        return

    def stop_handler(self):
        self.running = False
        return

    def dir_btn_handler(self):
        dialog = QFileDialog()
        dirname = dialog.getExistingDirectory()
        self.dirPath.setText(dirname)

    def main(self):
        return



if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow("mainwindow.ui", parent=app)
    sys.exit(app.exec_())
