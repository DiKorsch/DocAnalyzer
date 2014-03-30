#coding=utf-8
import sys, traceback
from ui.windows import myDialog
from PyQt4.QtGui import QTextEdit, QPushButton, QLabel, QApplication,\
    QGridLayout
from PyQt4.QtCore import QString
from PyQt4.Qt import Qt

class ReportWindow(myDialog):
    def __init__(self, text, parent = None):
        super(ReportWindow, self).__init__(parent, layoutCls = QGridLayout)
        self.setWindowTitle("Fehler!")
        
        self.infoLabel = QLabel(self)
        self.infoLabel.setText("Ein Fehler ist aufegtretten. Bitte senden Sie den unteren Text an <a  href=\"mailto:korschdima@yahoo.de\">korschdima@yahoo.de</a>!")
        self.infoLabel.setTextFormat(Qt.RichText)
        self.infoLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.infoLabel.setOpenExternalLinks(True)

        self.text = text
        
        self.textArea = QTextEdit(self)
        self.textArea.setPlainText(text)
        self.textArea.setReadOnly(True)

        self.okBtn = QPushButton(QString.fromUtf8("Meldung schließen"), self)
        self.okBtn.clicked.connect(self.close)
        
        self.copyBtn = QPushButton(QString.fromUtf8("Text kopieren"), self)
        self.copyBtn.clicked.connect(self.copy)
        
        self.myLayout.addWidget(self.infoLabel,     0,0,1,2)
        self.myLayout.addWidget(self.textArea,      1,0,1,2)
        self.myLayout.addWidget(self.copyBtn,       2,0,1,1)
        self.myLayout.addWidget(self.okBtn,         2,1,1,1)
        
    def copy(self):
        clip = QApplication.clipboard()
        clip.setText(self.text)
        
        
def install_excepthook():
    def excepthook(exctype, value, tb):
        s = ''.join(traceback.format_exception(exctype, value, tb))
        reportCrash(s)
    sys.excepthook = excepthook

def reportCrash(s):
    infoWin = ReportWindow(s)
    return infoWin.exec_() 