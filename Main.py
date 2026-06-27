# main.py
# Entry point — chỉ khởi chạy app

import sys
import os

# Đảm bảo import đúng khi chạy từ bất kỳ thư mục nào
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.Main_Window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
