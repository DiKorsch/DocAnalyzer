# coding: utf-8

from PyQt4.QtGui import QPushButton, QLineEdit, QFileDialog
from PyQt4.QtGui import QTabWidget, QListWidget, QMessageBox, QProgressBar

from PyQt4.QtCore import QString, QDir

import os
from fileReader import Reader
from ui.windows import myDialog, DBSelectorWindow
from ui.windows.ViewWindow import ViewWindow
from ui.windows.helper import messageBox
from ui.widgets import myWidget
from PyQt4.Qt import pyqtSignal
       
class MainWindow(myDialog):
    _dbViewWin = None
    
    def __init__(self, parent = None, *args, **kwargs):
        super(MainWindow, self).__init__(parent, *args, **kwargs)
        self.setWindowTitle("DocAnalyzer")
        self.myLayout.setContentsMargins(0, 0, 0, 0)
        
        self._tabWidget = QTabWidget(self)
        self._analyzerTab = AnalyzerTab(self._tabWidget)
        self._viewTab = ViewTab(self._tabWidget)
        self._viewTab.clicked.connect(self.openDBView)
        
        self._tabWidget.addTab(self._viewTab, "View")
        self._tabWidget.addTab(self._analyzerTab, "Analyze")

        self.myLayout.addRow(self._tabWidget)
#         self.setFixedSize(400, 300)

        
    def openDBView(self, dbName):
        if not dbName:
            messageBox(QMessageBox.Critical, "Fehler", "Der Name darf nicht leer sein!",  self, QMessageBox.Ok)
            return None
        
#         if self._dbViewWin == None:
        self._dbViewWin = ViewWindow(self, "%s.sqlite" %str(dbName))
        self._dbViewWin.show()
        



class ViewTab(myWidget):
    clicked = pyqtSignal(str)
    def __init__(self, parent = None, *args):
        super(ViewTab, self).__init__(parent, *args)
        
        self._lineEdit = QLineEdit(self)
        self._acceptBtn = QPushButton(QString.fromUtf8("Öffnen"), self)
        self._acceptBtn.clicked.connect(self.click)

        self.myLayout.addRow("Name der Datenbank:", self._lineEdit) 
        self.myLayout.addRow(self._acceptBtn)
        
    def click(self):
        self.clicked.emit(str(self._lineEdit.text()))

class AnalyzerTab(myWidget):
    def __init__(self, parent = None, *args):
        super(AnalyzerTab, self).__init__(parent, *args)
        self.currentFolder = QDir.currentPath()
        self.addFileRow()
        self.addListWidget()
        self.addReadRow()
        self.addProgressBars()
                
    def addFileRow(self):
        self._openBtn = QPushButton(QString.fromUtf8("Ordner auswählen"), self)
        self._openTextField = QLineEdit(self)
        
        self._openBtn.clicked.connect(self.openFolder)
        self.myLayout.addRow(self._openTextField, self._openBtn)

    def addListWidget(self):
        self._listWidget = QListWidget(self)
        self.myLayout.addRow(self._listWidget)
    
    def addReadRow(self):
        self._readBtn = QPushButton(QString.fromUtf8("Inhalt speichern"), self)
        self.myLayout.addRow(self._readBtn)
        self._readBtn.clicked.connect(self.saveFilesToDB)
    
    def addProgressBars(self):
        self._progresses = myWidget(self)
        self._progressFiles = QProgressBar(self._progresses)
        self._progressParagraphs = QProgressBar(self._progresses)
        self._progresses.myLayout.addRow("Dateien", self._progressFiles)
        self._progresses.myLayout.addRow("Paragraphen", self._progressParagraphs)
        self._progresses.setEnabled(False)
        self.myLayout.addRow(self._progresses)
        
    
    def openFolder(self):
        newFolder = str(QFileDialog.getExistingDirectory(parent=self, caption=QString.fromUtf8("Ordner auswählen"), directory = self.currentFolder))
        if not newFolder: 
            print "HIER: ", newFolder
            return            
        self._openTextField.setText(newFolder)
        self.listFolderFiles(newFolder)
        self.currentFolder = newFolder
    
    
    def listFolderFiles(self, folderPath):
        if not os.path.isdir(folderPath):
            print "%s is not a folder!" %folderPath
            return 
        self._listWidget.clear()
        for fName in os.listdir(folderPath):
            if fName.endswith(".doc") and not fName.startswith("~"): self._listWidget.addItem(fName)
    
    
    def saveFilesToDB(self):
        selWindow = DBSelectorWindow(self)
        if not selWindow.exec_(): return
        dbName = selWindow.getDBName()
        if not dbName:
            messageBox(QMessageBox.Critical, "Fehler", "Der Name darf nicht leer sein!",  self, QMessageBox.Ok)
            return
        self.currentReader = Reader()
        
        self._progresses.setEnabled(True)
        self.currentReader.ready.connect(self.readerReady)
        self.currentReader.folderStatusUpdated.connect(self.updateFolderStatus)
        self.currentReader.fileStatusUpdated.connect(self.updateFileStatus)
        self.currentReader.save_folder(str(self.currentFolder), "%s.sqlite" %str(dbName))
    
    def readerReady(self):
        self._progresses.setEnabled(False)
    
    def updateFolderStatus(self, ready, fileCount):
        self._progressFiles.setMaximum(100)
        self._progressFiles.setValue(self._calc_status(ready, fileCount))
    
    def updateFileStatus(self, ready, paragraphCount):
        self._progressParagraphs.setMaximum(100)
        self._progressParagraphs.setValue(self._calc_status(ready, paragraphCount))
    
    def _calc_status(self, done, toDo):
        r = done * 100 / toDo
        if r == 99:
            return 100
        else:
            return r


