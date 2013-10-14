from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QSharedMemory
from ui.windows import MainWindow

class SingleApplication(QApplication):
    def __init__(self, *argv):
        QApplication.__init__(self, *argv)
        self._memory = QSharedMemory(self)
        self._memory.setKey("pfTool")
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(
                    self._memory.errorString().toLocal8Bit().data())

    def is_running(self):
        return self._running
    
    def exec_(self):
        mainWindow = MainWindow()
        mainWindow.show()
        return super(SingleApplication, self).exec_()
    
    
if __name__ == '__main__':
    from fileReader import Reader
    from os import path
    from dbhandler import DBInterface

    
    import sys
    app = SingleApplication(sys.argv)  
 
    if app.is_running():
        print "[main] the tool is already running!"
        exit()
        
    
    
    print "[main] ready to close"
    r = app.exec_()  
    print "[main] exiting with status %d" %r  
    exit(r)
    DBInterface().clear_db()
    reader = Reader()
    reader.save_file(path.abspath("../tests/Paragraphen/P_001-007.doc"))
    
    reader.write()
