# coding: utf-8
from PyQt4.QtGui import QDialog, QLayout, QWidget, QFormLayout

class myDialog(QDialog):
    myLayout = None
    def __init__(self, parent = None, layoutCls = None, fixed = True):
        super(myDialog, self).__init__(parent)
        self.myLayout = (layoutCls or QFormLayout)(self)
        self.setLayout(self.myLayout)
        if fixed: self.myLayout.setSizeConstraint(QLayout.SetFixedSize)

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
    
 
from ui.windows.MainWindow import *
from ui.windows.ViewWindow import *
 
        

        