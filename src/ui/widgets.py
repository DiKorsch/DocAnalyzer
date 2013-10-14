# coding: utf-8
from PyQt4.QtGui import QWidget, QVBoxLayout, QTableView, QCheckBox
from PyQt4.QtGui import QStandardItemModel, QStandardItem
from PyQt4.QtCore import QString


def capitalized(s):
    if len(s) == 0 or (not(s.isalpha() or "-" in s)):
        return False
    c = s[0]
    if c == c.upper(): return True
    else: return False

class DBViewWidget(QWidget):
    myLayout = None
    _defaultContent = []
    _capitalContent = []
    
    def __init__(self, parent  = None, content = []):
        super(DBViewWidget, self).__init__(parent)
        self.myLayout = QVBoxLayout(self)
        self._tableWidget = QTableView(self)
        self._chkBx = QCheckBox(QString.fromUtf8("Großbuchstaben"), self)
        
        self._chkBx.toggled.connect(self.toggleContent)
        
        self.myLayout.addWidget(self._tableWidget)
        self.myLayout.addWidget(self._chkBx)
        
        self.setFixedSize(400, 300)
        
        self._init_contents(content)
        self.setContent(self._defaultContent)
        
    
    def _init_contents(self, content):
        self._defaultContent = list(content)
        for value in content:
            if capitalized(value[0]):
                self._capitalContent.append(value)
                
                
    def setContent(self, content):
        model = QStandardItemModel(self)
        c = 0
        for value in content:
            model.insertRow(c, self._createListItem(value))
            c += 1
            
        self._tableWidget.setModel(model)
         
    def toggleContent(self, caps):
        if caps:
            self.setContent(self._capitalContent)
        else:
            self.setContent(self._defaultContent)      
        
    def _createListItem(self, values):
        result = []
        for val in values:
            item = QStandardItem(str(val))
            item.setEditable(False)
            result.append(item)
        return result