# coding: utf-8

from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QTableView, QHBoxLayout, QStandardItemModel, QStandardItem
from PyQt4.QtCore import Qt

from ui.windows import myWindow
from dbhandler import DBHandler
from ui.widgets import DBViewWidget

class ViewWindow(myWindow):
    def __init__(self, parent=None, dbName = None):
        super(ViewWindow, self).__init__(parent, layoutCls=QHBoxLayout, fixed = False)
        if not dbName: raise Exception("dbName could not be empty or None!")
        self.myLayout.addWidget(DBViewWidget(self, self.countWords(str(dbName)), DetailWindow, dbName))
        self.setWindowTitle("Daten von " + str(dbName))
    
    def countWords(self, dbName):
        query = "Select * from wort order by count desc"
        dbh = DBHandler()
        dbh.reconnect(dbName)
        cursor = dbh.execute(query)
        dbh.commit()
        if cursor == None: print "No cursor returned: ", cursor
        return [[entry[1], entry[2]] for entry in cursor.fetchall()]
        


def collect(data):
    res = []
    def add(start, end):
        if start == end: res.append([start])
        else: res.append([start, end])
    
    start = 0
    for i in range(len(data)-1):
        if data[i]+1 == data[i+1]: continue
        add(data[start], data[i])
        start = i+1
    if start <= len(data): add(data[start], data[-1])
    return res

def toStr(data):
    res = ""
    for v in data:
        res += "%d, " %(v[0]) if len(v) == 1 else "%d-%d, " %(v[0], v[1])
    return res[:-2]


class DetailWindow(myWindow):
  
    listToParaAndRdnr = {}
  
    def __init__(self, parent = None):
        super(DetailWindow, self).__init__(parent, layoutCls = QHBoxLayout, fixed = False)
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
        rdnrsAsStr = toStr(collect([item for sublist in rdnrs for item in sublist]))
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