#coding=utf8
from PyQt4.QtGui import QMessageBox

def messageBox(icon = QMessageBox.Information, title = "", message = "", parent = None, buttons = QMessageBox.Ok):
    return QMessageBox(icon, title, message,  buttons, parent).exec_()

