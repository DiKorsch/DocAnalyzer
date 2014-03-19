# coding: utf-8
from PyQt4.QtGui import QWidget, QVBoxLayout, QTableView, QCheckBox, QPushButton
from PyQt4.QtGui import QStandardItemModel, QStandardItem, QHBoxLayout, QLineEdit
from PyQt4.QtCore import QString, pyqtSignal, Qt
from dbhandler import DBInterface


def capitalized(s):
    if len(s) == 0 or (not(s.isalpha() or "-" in s)):
        return False
    c = s[0]
    if c == c.upper(): return True
    else: return False

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
    
    
class DBViewWidget(QWidget):
    _defaultContent = []
    _capitalContent = []
    _currentCont = []
    _lastCurrent = []
    
    def __init__(self, parent  = None, content = [], detailWindowCls = None):
        super(DBViewWidget, self).__init__(parent)
        self.myLayout = QVBoxLayout(self)
        self._tableWidget = QTableView(self)
        self.detailWindow = detailWindowCls() if detailWindowCls else None
        self._tableWidget.doubleClicked.connect(self.showDetails)
        self._chkBx = QCheckBox(QString.fromUtf8("Großbuchstaben"), self)
        self._chkBx.toggled.connect(self.toggleContent)
        
        self._searchWidget = SearchWidget(self)
        self._searchWidget.clicked.connect(self.filter)
        self._searchWidget.reset.connect(self.reset)
        
        self.myLayout.addWidget(self._searchWidget)
        self.myLayout.addWidget(self._tableWidget)
        self.myLayout.addWidget(self._chkBx)
        
        self.setFixedSize(400, 300)
        
        self._init_contents(content)
        self.setContent(self._defaultContent)
    
    def filter(self, text):
      self._lastCurrent = self._currentCont
      self.setContent([val for val in self._currentCont if str(text).lower() in val[0].lower()])
    
    def reset(self):
      if self._lastCurrent: self.setContent(self._lastCurrent)
    
    def showDetails(self, idx):
      word = self._get_word_for_row(row = idx.row())
      cursor = self._get_info_for_word(word = word)
      self.detailWindow.showDetails(cursor.fetchall(), "Vorkommen von \"%s\"" %(word[0]))
      self.detailWindow.show()
      self.detailWindow.raise_()
    
    def _get_info_for_word(self, word = None, row = -1):
      if not word and row < 0: print "no word or row given!"; return
      if word is None: return self._get_info_for_word(word=self._get_word_for_row(row))
      cursor = DBInterface().getWordInfo(word[0])
      return cursor
    
    def _get_word_for_row(self, row):
      return self._currentCont[row]      
      
    def _init_contents(self, content):
        self._defaultContent = list(content)
        for value in content:
            if capitalized(value[0]):
                self._capitalContent.append(value)
                
                
    def setContent(self, content):
      self._currentCont = content
      model = QStandardItemModel(self)
      c = 0
      for value in content:
        model.insertRow(c, self._createListItem(value))
        c += 1
      
      model.setHeaderData(0, Qt.Horizontal, "Wort")
      model.setHeaderData(1, Qt.Horizontal, "Vorkommen")
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