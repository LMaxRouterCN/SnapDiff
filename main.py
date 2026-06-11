import sys
import os

# 确保能导入 src 目录下的模块
sys.path.append(os.path.dirname(__file__))

from src.gui import MainWindow
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()