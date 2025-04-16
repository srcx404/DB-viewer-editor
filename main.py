import sys
from PyQt5.QtWidgets import QApplication
from dbviewer import DBViewer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 样式使界面更美观
    window = DBViewer()
    window.show()
    sys.exit(app.exec_())
