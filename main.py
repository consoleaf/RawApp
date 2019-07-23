# This Python file uses the following encoding: utf-8
import sys
import os
import time
from threading import Thread

try:
    from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QLineEdit, QCheckBox, \
        QProgressBar, QMessageBox, QWidget
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtCore import QFile, QObject, QRunnable, Slot, QThreadPool, Signal, SIGNAL
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

        self.worker: Worker = None
        self.running = False

        self.thread_pool = QThreadPool()
        print("Multi threading with maximum %d threads" % self.thread_pool.maxThreadCount())

        self.msg_box = QMessageBox(parent=self.window)
        self.msg_box.setIcon(QMessageBox.Critical)
        self.msg_box.setWindowTitle("Некорректные настройки")

        self.window.destroyed.connect(self.stop_handler)
        self.window.show()

    def start_handler(self):
        if self.thread_pool.activeThreadCount() > 0:
            return
        if self.check_inputs():
            self.worker = Worker(self)
            self.worker.signals.updated.connect(self.worker_upd_handler)
            self.worker.running = True
            self.thread_pool.start(self.worker)
        return

    def stop_handler(self):
        self.worker.running = False
        self.thread_pool.waitForDone(1000)
        return

    def worker_upd_handler(self, data):
        if data["sortBar"]:
            self.sortBar.setValue(data["sortBar"])
        if data["moveBar"]:
            self.moveBar.setValue(data["moveBar"])

    def dir_btn_handler(self):
        dialog = QFileDialog()
        dirname = dialog.getExistingDirectory()
        self.dirPath.setText(dirname)

    def check_inputs(self):
        errors = []
        if not os.path.exists(self.dirPath.text()):
            errors.append("Выбранная папка не существует")
        if self.moveRepeatFiles.isChecked() and len(self.repeatFiles_dir.text()) < 1:
            errors.append("Введите название папки для переноса повторяющихся файлов")
        if self.moveSingleFiles.isChecked() and len(self.singleFiles_dir.text()) < 1:
            errors.append("Введите название папки для переноса одиночных файлов")
        if errors:
            self.msg_box.setText("\n".join(errors))
            self.msg_box.exec()
            return False
        return True


class Worker(QRunnable):
    """
    Worker thread
    """

    class Signals(QObject):
        updated = Signal(dict)

    def __init__(self, parent):
        """

        :type parent: MainWindow
        """

        super().__init__()
        self.my_parent = parent
        self.running = False
        self.signals = self.Signals()

    @Slot()
    def run(self):
        for i in range(101):
            if not self.running:
                return
            self.signals.updated.emit({
                "sortBar": i * 2,
                "moveBar": i
            })
            time.sleep(0.1)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow("mainwindow.ui", parent=app)
    sys.exit(app.exec_())
