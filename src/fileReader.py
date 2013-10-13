# CODING=utf-8
from doc.reader import DocReader
from os import path
from time import time
from dbhandler import DBInterface

i = 0
t1 = 0l
NEW_LINE = "\n"

CODING = "latin-1"


class Reader(object):
    def __init__(self):
        self.dbi = DBInterface()
        self.dbi.clear_db()
    
    def save_folder(self, folderPath):
        pass

    def save_file(self, filePath):
        global t1
        docF = DocReader(filePath)
        
        t1 = time()
        rawCont = docF.read()
        rawCont = rawCont.decode(CODING)
        
        contentParted = rawCont.partition(NEW_LINE)
        caption = contentParted[0]
        content = contentParted[2]
        paragraphs = content.split('%s\x0c' %(NEW_LINE))
        
        FILE_ID = self.dbi.addFile(path.basename(filePath), caption)
        for para in paragraphs:
            paraCaption, __, paraContent = para.partition(NEW_LINE)
            PARAGRAPH_ID = self.dbi.addParagraph(paraCaption, FILE_ID)
            curRdNr = None
            rdNrContent = []
            for line in paraContent.split(NEW_LINE):
                if line.isdigit():
                    if curRdNr != None:
                        RDNR_ID = self.dbi.addRdNr(curRdNr, PARAGRAPH_ID)
                        self.save_content(rdNrContent, RDNR_ID, PARAGRAPH_ID, FILE_ID)
                    rdNrContent = []
                    curRdNr = int(line)
                else:
                    rdNrContent.append(line)

    def save_content(self, content, RDNR_ID, PARAGRAPH_ID, FILE_ID):
        global i
        global t1
        for line in content:
            for word in self.extract_words(line):
                self.dbi.addWord(word, RDNR_ID, PARAGRAPH_ID, FILE_ID)
                i += 1
    
    def extract_words(self, line):
        charsToDelete = ['.', ',', ';', ':', '?', '!', '"', "'", "(", ")", chr(0)]
        charsToReplaceWithSpace = ['/', ]
    
        cleanLine = line.rstrip()
        for c in charsToDelete:
            cleanLine = cleanLine.replace(c, '') 
        for c in charsToReplaceWithSpace:
            cleanLine = cleanLine.replace(c, ' ') 
    
        return cleanLine.split()
    
    def write(self):
        self.dbi.writeWords()