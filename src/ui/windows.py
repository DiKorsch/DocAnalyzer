# coding: utf-8
from PyQt4.QtGui import QDialog, QFormLayout, QPushButton, QLineEdit, QFileDialog
from PyQt4.QtGui import QListWidget, QLayout, QMessageBox, QProgressBar, QWidget
from PyQt4.QtGui import QTableView, QHBoxLayout, QStandardItemModel, QStandardItem

from PyQt4.QtCore import QString, QDir, Qt

import os
from fileReader import Reader
from ui.widgets import DBViewWidget
from dbhandler import DBHandler

def messageBox(icon = QMessageBox.Information, title = "", message = "", parent = None, buttons = QMessageBox.StandardButton):
    return QMessageBox(icon, title, message,  buttons, parent).exec_()

class myDialog(QDialog):
    myLayout = None
    def __init__(self, parent = None, layoutCls = None):
        super(myDialog, self).__init__(parent)
        self.myLayout = (layoutCls or QFormLayout)(self)
        self.myLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(self.myLayout)
        
class MainWindow(myDialog):
    _openBtn = None
    _readBtn = None
    _viewBtn = None
    _openTextField = None
    
    _listWidget = None
    
    _progressFiles = None
    _progressParagraphs = None
    
    _progresses = None
    
    _dbViewWin = None
    
    currentFolder = QDir.currentPath()
    
    currentReader = None

    def __init__(self, parent = None, *args, **kwargs):
        super(MainWindow, self).__init__(parent, *args, **kwargs)
        self.setWindowTitle("DocAnalyzer")
#         self.setFixedSize(400, 300)
        self.addFileRow()
        self.addListWidget()
        self.addReadRow()
        self.addProgressBars()
        self.addViewBtn()
        
    
    def addViewBtn(self):
        self._viewBtn = QPushButton("Datenbank anzeigen", self)
        self._viewBtn.clicked.connect(self.openDBView)
        self.myLayout.addRow(self._viewBtn)

    def addReadRow(self):
        self._readBtn = QPushButton(QString.fromUtf8("Inhalt speichern"), self)
        self.myLayout.addRow(self._readBtn)
        
        self._readBtn.clicked.connect(self.saveFilesToDB)
    
    def addFileRow(self):
        self._openBtn = QPushButton(QString.fromUtf8("Ordner auswählen"), self)
        self._openTextField = QLineEdit(self)
        
        self._openBtn.clicked.connect(self.openFolder)
        self.myLayout.addRow(self._openTextField, self._openBtn)
    
    def addListWidget(self):
        self._listWidget = QListWidget(self)
        self.myLayout.addRow(self._listWidget)
        
    def addProgressBars(self):
        self._progresses = QWidget(self)
        self._progressFiles = QProgressBar(self._progresses)
        self._progressParagraphs = QProgressBar(self._progresses)
        progLayout = QFormLayout(self._progresses)
        progLayout.addRow("Dateien", self._progressFiles)
        progLayout.addRow("Paragraphen", self._progressParagraphs)
        self._progresses.setLayout(progLayout)
        self._progresses.setEnabled(False)
        self.myLayout.addRow(self._progresses)

    def openFolder(self):
        newFolder = str(QFileDialog.getExistingDirectory(parent=self, caption="Ordner auswählen", directory = self.currentFolder))
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
            if fName.endswith(".doc"): self._listWidget.addItem(fName)

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
    
    def openDBView(self):
        selWindow = DBSelectorWindow(self)
        if not selWindow.exec_(): return
        dbName = selWindow.getDBName()
        if not dbName:
            messageBox(QMessageBox.Critical, "Fehler", "Der Name darf nicht leer sein!",  self, QMessageBox.Ok)
            return None
        
#         if self._dbViewWin == None:
        self._dbViewWin = ViewWindow(self, "%s.sqlite" %str(dbName))
        self._dbViewWin.show()
        
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

class DBSelectorWindow(myDialog):
    _lineEdit = None
    _acceptBtn = None
    _rejectBtn = None
    
    def __init__(self, parent = None):
        super(DBSelectorWindow, self).__init__(parent)
#         self.setFixedSize(300, 200)
        self.addLineEdit()
        self.addButtons()
        
    def addLineEdit(self):
        self._lineEdit = QLineEdit(self)
        self.layout().addRow("Name der Datenbank:", self._lineEdit)    
    
    def addButtons(self):
        accBtn = QPushButton(QString.fromUtf8("Auswählen"), self)
        rejBtn = QPushButton("Abbrechen", self)
        
        accBtn.clicked.connect(self.accept)
        rejBtn.clicked.connect(self.reject)
        
        self.myLayout.addRow(accBtn, rejBtn)
        
        self._acceptBtn = accBtn
        self._rejectBtn = rejBtn
    
    def getDBName(self):
        return self._lineEdit.text()
    
    
class ViewWindow(myDialog):
    def __init__(self, parent=None, dbName = None):
        super(ViewWindow, self).__init__(parent)
        if not dbName: raise Exception("dbName could not be empty or None!")
        self.layout().addWidget(DBViewWidget(self, self.countWords(str(dbName)), DetailWindow))
        self.setWindowTitle("Daten von " + str(dbName))
    
    def countWords(self, dbName):
        query = "Select * from wort order by count desc"
        dbh = DBHandler()
        dbh.reconnect(dbName)
        cursor = dbh.execute(query)
        dbh.commit()
        if cursor == None: print "No cursor returned: ", cursor
        return [[entry[1], entry[2]] for entry in cursor.fetchall()]
        
class DetailWindow(myDialog):
  
  listToParaAndRdnr = {}
  
  def __init__(self, parent = None):
    super(DetailWindow, self).__init__(parent, layoutCls = QHBoxLayout)
    self._listWidget = QListWidget(self)
    self._paraAndRdnr = QTableView(self)
    self.layout().addWidget(self._listWidget)
    self.layout().addWidget(self._paraAndRdnr)
    self._listWidget.clicked.connect(self.showParaAndRdnr)
  
  def showParaAndRdnr(self, listItem):
    paraAndRdnr = self.listToParaAndRdnr.get(listItem.row())
    model = QStandardItemModel(self)
    c = 0
    for para, rdnrs in paraAndRdnr.iteritems():
      l = self._createListItem(para, rdnrs)
      model.insertRow(c, l)
      c += 1
    model.setHeaderData(0, Qt.Horizontal, "Paragraph")
    model.setHeaderData(1, Qt.Horizontal, "Randnummern")
    self._paraAndRdnr.setModel(model)
    
  def _createListItem(self, para, rdnrs):
    rdnrsAsStr = "".join([str(item) + ", " for sublist in rdnrs for item in sublist])[:-2]
    item1 = QStandardItem(para.decode("utf-8"))
    item1.setToolTip(para.decode("utf-8"))
    item2 = QStandardItem(rdnrsAsStr)
    item2.setToolTip(rdnrsAsStr)
    return [item1, item2]
  
  def showDetails(self, content, windowTitle = None):
    if windowTitle: self.setWindowTitle(windowTitle)
    details = self._map_details(content)
    self._listWidget.clear()
    i = 0
    for fileName, paraAndRdnrs in details.iteritems():
      self._listWidget.addItem(fileName)
      self.listToParaAndRdnr[i] = paraAndRdnrs
      i += 1
    
  def _map_details(self, data):
    def nestedMap(data):
      res = {}
      idx = len(data[0])-1
      for d in data:
        old = res.get(d[idx], [])
        old.append(d[:idx])
        res[d[idx]] = old
      return res
  
    res = nestedMap(data)
    for k, v in res.iteritems():
      res[k] = nestedMap(v)
    return res
        