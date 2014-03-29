# coding: utf-8
from PyQt4.QtGui import QWidget, QTableView, QCheckBox, QPushButton
from PyQt4.QtGui import QStandardItemModel, QStandardItem, QHBoxLayout, QLineEdit
from PyQt4.QtGui import QFormLayout, QGridLayout, QVBoxLayout
from PyQt4.QtCore import QString, pyqtSignal, Qt, QModelIndex
from dbhandler import DBInterface


def capitalized(s):
    if len(s) == 0 or (not(s.isalpha() or "-" in s)):
        return False
    c = s[0]
    if c == c.upper(): return True
    else: return False

class myWidget(QWidget):
    def __init__(self, parent = None, layoutCls = None):
        super(myWidget, self).__init__(parent)
        self.myLayout = (layoutCls or QFormLayout)(self)
        self.setLayout(self.myLayout)


class SearchWidget(QWidget):
    clicked = pyqtSignal(str)
    reset = pyqtSignal()
  
    def __init__(self, parent  = None):
        super(SearchWidget, self).__init__(parent)
        self.myLayout = QHBoxLayout(self)
        self.button = QPushButton("Suchen", parent = self)
        self.resetBtn = QPushButton(QString.fromUtf8("Zurücksetzen"), parent = self)
        self.lineedit = QLineEdit(parent = self)
        self.setLayout(self.myLayout)
        self.layout().addWidget(self.lineedit)
        self.layout().addWidget(self.button)
        self.layout().addWidget(self.resetBtn)
        
        self.button.clicked.connect(self.searchemited)
        self.resetBtn.clicked.connect(self.reset)
    
    def searchemited(self):
        self.clicked.emit(self.lineedit.text())
    
class myTable(myWidget):
    doubleClicked = pyqtSignal(QModelIndex)
    blDoubleClicked = pyqtSignal(QModelIndex)
    
    detailsReady = pyqtSignal(list, str)
    
    def __init__(self, parent  = None, content = []):
        super(myTable, self).__init__(parent, QHBoxLayout)
        
        self.table = {}
        
        self.table[False] = QTableView(self)
        self.table[False].doubleClicked.connect(self.showDetails)
        
        self.table[True] = QTableView(self)
        self.table[True].doubleClicked.connect(self.showBlackListDetails)
        
        self.btnAddToBl = QPushButton(">", self)
        self.btnAddToBl.clicked.connect(self.addToBl) 
        self.btnAddToBl.setMaximumWidth(30)
        
        self.btnRemoveFromBl = QPushButton("<", self)
        self.btnRemoveFromBl.clicked.connect(self.removeFromBl) 
        self.btnRemoveFromBl.setMaximumWidth(30)
        
        btnLayout = QVBoxLayout()
        btnLayout.addWidget(self.btnAddToBl)
        btnLayout.addWidget(self.btnRemoveFromBl)
        
        self.myLayout.addWidget(self.table[False])
        self.myLayout.addLayout(btnLayout)
        self.myLayout.addWidget(self.table[True])
        
        
        self._defaultContent = list(content)
        self._currentCont = {
         True: self._init_black_list(), 
         False: [] }
        
        self.alphaSorting = False
        self.caps = False
        
        self.setContent(self._defaultContent)
    
    def _init_black_list(self):
        return []
    
    def setModel(self, model, blackList = False):
        self.table[blackList].setModel(model)
    
    def updateContent(self):
        for val in [True, False]: self.setContent(self._currentCont[val], val)

    def updateBlackList(self, addToBl):
        if len(self._currentCont[addToBl]) == 0: return
        curVal = self._currentCont[addToBl][self.table[addToBl].currentIndex().row()]
        self._currentCont[addToBl].remove(curVal)
        self._currentCont[not addToBl].append(curVal)
        self.updateContent()
    
    
    def addToBl(self): self.updateBlackList(False)
    
    def removeFromBl(self): self.updateBlackList(True)
    
    def setContent(self, content, blackList = False):
        model = QStandardItemModel(self)
        c = 0
        if self.caps:
            content = [val for val in content if capitalized(val[0])]
        
        if self.alphaSorting:
            content = sorted(content, key=lambda val: val[0])
        else:
            content = sorted(content, key=lambda val: val[1], reverse=True)
            
        for value in content:
            model.insertRow(c, self._createListItem(value))
            c += 1

        self._currentCont[blackList] = content
        
        model.setHeaderData(0, Qt.Horizontal, "Wort")
        model.setHeaderData(1, Qt.Horizontal, "Vorkommen")
        self.setModel(model, blackList)
        
    def _createListItem(self, values):
        result = []
        for val in values:
            item = QStandardItem(str(val))
            item.setEditable(False)
            result.append(item)
        return result
    
    def reset(self, blackList = False):
        self.setContent([val for val in self._defaultContent if val not in self._currentCont[not blackList]], blackList)
    
    def filter(self, text, blackList = False):
        self.setContent([val for val in self._defaultContent if str(text).lower() in val[0].lower()], blackList)
    
    def sortAlpha(self, checked):
        self.alphaSorting = checked
        self.setContent(self._currentCont[False])
          
    def capsClicked(self, caps):
        self.caps = caps
        self.setContent(self._currentCont[False])
    
    def showBlackListDetails(self, idx):
        pass
        
    def showDetails(self, idx):
        word = self._get_word_for_row(row = idx.row())
        cursor = self._get_info_for_word(word = word)
        self.detailsReady.emit(cursor.fetchall(), "Vorkommen von \"%s\"" %(word[0]))
    
    def _get_info_for_word(self, word = None, row = -1):
        if not word and row < 0: print "no word or row given!"; return
        if word is None: return self._get_info_for_word(word=self._get_word_for_row(row))
        cursor = DBInterface().getWordInfo(word[0])
        return cursor
    
    def _get_word_for_row(self, row, blackList = False):
        return self._currentCont[blackList][row]        
            
class DBViewWidget(QWidget):
    
    def __init__(self, parent  = None, content = [], detailWindowCls = None):
        super(DBViewWidget, self).__init__(parent)
        self.detailWindow = detailWindowCls() if detailWindowCls else None

        self.myLayout = QGridLayout(self)
        self.myLayout.setContentsMargins(0, 0, 0, 0)
        
        self._tableWidget = myTable(self, content)
        self._tableWidget.detailsReady.connect(self.openDetailWindow)
        
        self._chkBxCaps = QCheckBox(QString.fromUtf8("Großbuchstaben"), self)
        self._chkBxCaps.toggled.connect(self._tableWidget.capsClicked)
        
        self._chkBxSorting = QCheckBox(QString.fromUtf8("Alphabetisch"), self)
        self._chkBxSorting.toggled.connect(self._tableWidget.sortAlpha)
        
        self._searchWidget = SearchWidget(self)
        self._searchWidget.clicked.connect(self._tableWidget.filter)
        self._searchWidget.reset.connect(self._tableWidget.reset)
        
        self.myLayout.addWidget(self._searchWidget,         0, 0, 1, 2)
        self.myLayout.addWidget(self._chkBxCaps,            1, 0, 1, 1)
        self.myLayout.addWidget(self._chkBxSorting,         1, 1, 1, 1)
        self.myLayout.addWidget(self._tableWidget,          2, 0, 1, 2)
        
#         self._init_contents(content)
#         self.setContent(self._defaultContent)
    
    def openDetailWindow(self, data, caption):
        self.detailWindow.showDetails(data, caption)
        self.detailWindow.show()
        self.detailWindow.raise_()
    
    def showBlackList(self, val):
        print "showing black list", val
    
      
                
