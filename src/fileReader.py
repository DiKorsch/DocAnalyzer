# CODING=utf-8
from doc.reader import DocReader
from os import path
from time import time
from dbhandler import DBInterface

i = 0
t1 = 0l
NEW_LINE = "\n"

CODING = "latin-1"

"""
def extract_words(line):
    charsToDelete = ['.', ',', ';', ':', '?', '!', '"', "'", "(", ")", chr(0)]
    charsToReplaceWithSpace = ['/', ]

    cleanLine = line.rstrip()
    for c in charsToDelete:
        cleanLine = cleanLine.replace(c, '') 
    for c in charsToReplaceWithSpace:
        cleanLine = cleanLine.replace(c, ' ') 

    return cleanLine.split()

def save_content(content, RDNR_ID, PARAGRAPH_ID, FILE_ID, dbi):
    global i
    global t1
    for line in content:
        for word in extract_words(line):
            dbi.addWord(word, RDNR_ID, PARAGRAPH_ID, FILE_ID)
            i += 1
    t2 = time()
    dbi.writeWords()
    print "%d words written in %01.03f sec" %(i, t2 - t1)
    t1 = t2

def save_file_to_db(filePath, dbi):
    global t1
    docF = DocReader(filePath)
    
    t1 = time()
    rawCont = docF.read()
    rawCont = rawCont.decode('latin-1')
    
    contentParted = rawCont.partition(NEW_LINE)
    caption = contentParted[0]
    content = contentParted[2]
    paragraphs = content.split('%s\x0c' %(NEW_LINE))
    
    FILE_ID = dbi.addFile(path.basename(filePath), caption)
    for para in paragraphs:
        paraCaption, __, paraContent = para.partition(NEW_LINE)
        PARAGRAPH_ID = dbi.addParagraph(paraCaption, FILE_ID)
        curRdNr = None
        rdNrContent = []
        for line in paraContent.split(NEW_LINE):
            if line.isdigit():
                if curRdNr != None:
                    RDNR_ID = dbi.addRdNr(curRdNr, PARAGRAPH_ID)
                    save_content(rdNrContent, RDNR_ID, PARAGRAPH_ID, FILE_ID, dbi)
                rdNrContent = []
                curRdNr = int(line)
            else:
                rdNrContent.append(line)


def save_folder_to_db(folderPath, dbi):
    import os
    if not path.isdir(folderPath):
        raise Exception(folderPath + " is not a dir!");
    files = os.listdir(folderPath)
    for fName in files:
        if fName.endswith(".doc"):
            save_file_to_db(path.join(folderPath, fName), dbi)
"""

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