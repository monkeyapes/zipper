import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gui import LocalNameApp

if __name__ == '__main__':
    app = LocalNameApp()
    app.run()
