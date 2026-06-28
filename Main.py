         
                                 

import sys
import os

                                                    
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.Main_Window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
