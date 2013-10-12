# coding=utf-8
from doc.reader import DocReader
from os import path
from dbhandler import DBInterface
from time import time

dbi = DBInterface()
dbi.clear_db()
i = 0

def extract_words(line):
    charsToDelete = ['.', ',', ';', ':', '?', '!', '"', "'", "(", ")", chr(0)]
    charsToReplaceWithSpace = ['/', ]

    cleanLine = line.rstrip()
    for c in charsToDelete:
        cleanLine = cleanLine.replace(c, '') 
    for c in charsToReplaceWithSpace:
        cleanLine = cleanLine.replace(c, ' ') 

    return cleanLine.split()

def save_content(content, RDNR_ID, PARAGRAPH_ID, FILE_ID):
    global dbi
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

NEW_LINE = "\n"

filename = path.abspath("../tests/Paragraphen/P_001-007.doc")

docF = DocReader(filename)

t1 = time()
rawCont = docF.read()
rawCont = rawCont.decode('latin-1')

contentParted = rawCont.partition(NEW_LINE)
caption = contentParted[0]
content = contentParted[2]
paragraphs = content.split('%s\x0c' %(NEW_LINE))

FILE_ID = dbi.addFile(path.basename(filename), caption)
for para in paragraphs:
    paraCaption, nl, paraContent = para.partition(NEW_LINE)
    PARAGRAPH_ID = dbi.addParagraph(paraCaption, FILE_ID)
    curRdNr = None
    rdNrContent = []
    for line in paraContent.split(NEW_LINE):
        if line.isdigit():
            if curRdNr != None:
                RDNR_ID = dbi.addRdNr(curRdNr, PARAGRAPH_ID)
                save_content(rdNrContent, RDNR_ID, PARAGRAPH_ID, FILE_ID)
            rdNrContent = []
            curRdNr = int(line)
        else:
            rdNrContent.append(line)

