from Style import MD5CrackerPro
import sys
from PyQt5.QtWidgets import QApplication
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MD5CrackerPro()
    window.show()
    sys.exit(app.exec_())