# CODING=utf-8
from doc.reader import DocReader
from os import path
from dbhandler import DBInterface, DBHandler
import os, re

from PyQt4.QtCore import QObject, pyqtSignal, QThread

NEW_LINE = "\n"

CODING = "latin-1"

import traceback

class ReaderThread(QThread):
    folderStatusUpdated = pyqtSignal(int, int)
    fileStatusUpdated = pyqtSignal(int, int)
    ready = pyqtSignal()
    
    def __init__(self, dbi, method, absPath, dbName):
        self.dbi = dbi
        self.dbName = dbName
        self.method = str(method)
        self.absPath = str(absPath)
        
        self.readChars = 0
        super(ReaderThread, self).__init__()
    
    def run(self):
        try:
            self.dbi.reconnect(self.dbName)
            self.dbi.clear_db()
            if self.method == "folder":
                self.save_folder(self.absPath)
            elif self.method == "file":
                self.save_file(self.absPath)
            self.dbi.writeWords()
            self.ready.emit()
        except Exception, e:
            print __file__, "ReaderThread > run(): ", e
            traceback.print_exc()
        finally:
            self.dbi.disconnect()
            
    def save_folder(self, folderPath):
        if not path.isdir(folderPath): 
            print "[ReaderThread.save_folder] \"%s\" is not a folder!" %(folderPath)
            return
        
        files = []
        for f in os.listdir(folderPath):
            if f.endswith(".doc") and not f.startswith("~"):
                files.append(f)
        i = 0
        for fName in files:
            self.save_file(path.join(folderPath, fName))
            i += 1
            self.folderStatusUpdated.emit(i, len(files))
                
    def save_file(self, filePath):
        docF = DocReader(filePath)
        
        rawCont = docF.read()
        rawCont = rawCont.decode(CODING)
        
        self.readChars = 0
        size = len(rawCont)
        contentParted = rawCont.partition(NEW_LINE)
        caption = contentParted[0]
        content = contentParted[2]
        paraSplitter = '%s\x0c' %(NEW_LINE)
        paragraphs = content.split(paraSplitter)
#         print filePath, "got %d paragraphs" %(len(paragraphs))
        
        FILE_ID = self.dbi.addFile(path.basename(filePath), caption)
        for para in paragraphs:
            paraCaption, __, paraContent = para.partition(NEW_LINE)
            self.readChars += len(para) + len(paraSplitter)
            PARAGRAPH_ID = self.dbi.addParagraph(paraCaption, FILE_ID)
            curRdNr = None
            rdNrContent = []
            for line in paraContent.split(NEW_LINE):
                # eigentlich werden randnummern in textboxes als eigene Zeile erkannt...
                if line.isdigit():
                    if curRdNr != None:
                        RDNR_ID = self.dbi.addRdNr(curRdNr, PARAGRAPH_ID)
                        self.save_content(rdNrContent, RDNR_ID, PARAGRAPH_ID, FILE_ID)
                    rdNrContent = []
                    curRdNr = int(line)
#                     self.readChars += len(line) + len(NEW_LINE)
                # ... wenn man aber die Dokumente aus odt importiert, werden die in die zeile vorne drangehangen(zusammen mit 2 tabs)
                elif re.match("\d+\t\t", line[:10]):
                    partition = line.partition("\t\t")
                    if curRdNr != None:
                        RDNR_ID = self.dbi.addRdNr(curRdNr, PARAGRAPH_ID)
                        self.save_content(rdNrContent, RDNR_ID, PARAGRAPH_ID, FILE_ID)
                    rdNrContent = [partition[2].strip()]
                    curRdNr = int(partition[0])
                else:
                    rdNrContent.append(line)
            self.fileStatusUpdated.emit(self.readChars, size)

    def save_content(self, content, RDNR_ID, PARAGRAPH_ID, FILE_ID):
        for line in content:
            words = self.extract_words(line)
            for word in words:
                self.dbi.addWord(word, RDNR_ID, PARAGRAPH_ID, FILE_ID)
#             self.readChars += len(line) + len(NEW_LINE)
    
    def clean_line(self, line):
        charsToDelete = ['.', ',', ';', ':', '?', '!', '"', "'", "(", ")", chr(0)]
        charsToReplaceWithSpace = ['/', ]
    
        cleanLine = line.rstrip()
        for c in charsToDelete:
            cleanLine = cleanLine.replace(c, '') 
        for c in charsToReplaceWithSpace:
            cleanLine = cleanLine.replace(c, ' ') 
        return cleanLine
      
    def extract_words(self, line):
        return self.clean_line(line).split()
    
    def write(self):
        self.dbi.writeWords()

class Reader(QObject):
    folderStatusUpdated = pyqtSignal(int, int)
    fileStatusUpdated = pyqtSignal(int, int)
    ready = pyqtSignal()
    
    _curThread = None
    
    def __init__(self):
        super(Reader, self).__init__()
        self.dbi = DBInterface()
        self.dbi.clear_db()
    
    def save_folder(self, folderPath, dbName):
        DBHandler().disconnect()
        thread = ReaderThread(self.dbi, "folder", folderPath, dbName)
        thread.folderStatusUpdated.connect(self.folderStatusUpdated)
        thread.fileStatusUpdated.connect(self.fileStatusUpdated)
        thread.ready.connect(self.ready)
        thread.start()
        self._curThread = thread
                
    def save_file(self, filePath):
        DBHandler().disconnect()
        thread = ReaderThread(self.dbi, "file", filePath)
        thread.folderStatusUpdated.connect(self.folderStatusUpdated)
        thread.fileStatusUpdated.connect(self.fileStatusUpdated)
        thread.ready.connect(self.ready)
        thread.start()
        self._curThread = thread
