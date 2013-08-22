# coding=utf-8
#from cfb.reader import CfbReader
from doc.reader import DocReader
from os import path
from dbhandler import DBHandler
import os
import sys

NEW_LINE = u"\n"

PLAIN_FOLDER = "plain"

def createDirIfNeeded(dirName):
  if not path.isdir(dirName) and not path.exists(dirName):
    os.mkdir(dirName)
  

def collectListToString(aList):
  RESULT = ""
  for el in aList:
    RESULT += el
    if el != aList[0]:
      RESULT += NEW_LINE
  return RESULT.rstrip()

def capitalized(s):
  if not len(s) or (not(s.isalpha() or "-" in s)):
    return False
  c = s[0]
  if c == c.upper(): return True
  else: return False

def extractWords(line):
  charsToDelete = ['.', ',', ';', ':', '?', '!', '"', "'", "(", ")"]
  charsToReplaceWithSpace = ['/', ]

  cleanLine = line.rstrip()
  for c in charsToDelete:
    cleanLine = cleanLine.replace(c, '') 
  for c in charsToReplaceWithSpace:
    cleanLine = cleanLine.replace(c, ' ') 

  return cleanLine.split()

class WordLocation(object):
  def __init__(self, paragraph, rdNr):
    self.paragraph = paragraph
    self.rdNr = rdNr
    

class Word(object):
  def __init__(self, word):
    self.word = word
    self.rstCnt()
    self.locations = []

  def addLocation(self, paragraph, rdNr):
    self.addLocationInst(WordLocation(paragraph, rdNr))

  def addLocationInst(self, inst):
    self.locations.append(inst)

  def locationsAsStr(self):
    RESULT = ""
    i = 0
    for loc in self.locations:
      if i > 0:
        RESULT += ", "
      RESULT += "%s/%s" %(loc.paragraph, loc.rdNr)
      i += 1
    return RESULT

  def incCnt(self): self.cnt += 1
  def decCnt(self): self.cnt -= 1
  def rstCnt(self): self.cnt = 1

  def hash(self):
    return hash(self.word)

  def iscapitalized(self):
    return capitalized(self.word)

  def __str__(self):
    return "%s, cnt:%s" %(self.word, self.cnt)

class ParagraphWords(object):
  def __init__(self, content, paragraph, rdNr):
    self.content = content    
    self.capWords = {}
    self.normalWords = {}
    words = extractWords(content)
    for w in words:
      word = Word(w)
      word.addLocation(paragraph, rdNr)
      if word.iscapitalized():
        dictToModify = self.capWords
      else:
        dictToModify = self.normalWords
      if dictToModify.has_key(word.hash()):
        oldInst = dictToModify.get(word.hash())
        oldInst.incCnt()
      else:
        oldInst = word
      dictToModify.update({word.hash(): oldInst})

class Paragraph(object):
  def __init__(self, paraContent, docCaption):
    self.rdWordMap = {}
    self.rawContent, self.document = paraContent, docCaption
    self.caption, nl, self.content = paraContent.partition(NEW_LINE)
    filePath = path.join(PLAIN_FOLDER, path.join(self.document, self.caption))
    self.__mapContentToRdNr()
    # for k in self.rdWordMap:
    #   for w in self.rdWordMap[k].capWords.values():
    #     print k, "===> ", w
      # exit()
  
  def __mapContentToRdNr(self):
    curRdNr = None
    curLines = []
    self.rdWordMap = {}
    for line in self.content.split(NEW_LINE):
      if line.isdigit():
        if curRdNr != None:
          # save collected lines
          self.rdWordMap.update({curRdNr:ParagraphWords(collectListToString(curLines), self.caption, curRdNr)})
        # reset the lines and set new RdNr
        curLines = []
        curRdNr = int(line)
        continue

      if curRdNr == None:
        continue
      curLines.append(line)

    

def addWord(aDict, word):
  if aDict.has_key(word.hash()):
    oldInst = aDict.get(word.hash())
    oldInst.cnt += word.cnt
    for loc in word.locations:
      oldInst.addLocationInst(loc)
    aDict.update({word.hash(): oldInst})
  else:
    aDict.update({word.hash(): word})
  return aDict

def readDocFile(fName):
  docF = DocReader(fName)
  rawCont = docF.read().decode('latin-1').encode('utf-8')
  contentParted = rawCont.partition(NEW_LINE)
  caption = contentParted[0]
  content = contentParted[2]

  # createDirIfNeeded(path.join(PLAIN_FOLDER, caption))

  paragraphs = content.split(u'%s\x0c' %(NEW_LINE))

  cRESULT = {}
  # nRESULT = {}
  for rawPara in paragraphs:
    para = Paragraph(rawPara, caption)
    for k in para.rdWordMap:
      for w in para.rdWordMap[k].capWords.values():
        cRESULT = addWord(cRESULT, w)
      # for w in para.rdWordMap[k].normalWords.values():
      #   nRESULT = addWord(nRESULT, w)

  return cRESULT

  # cap_out = open(path.join(PLAIN_FOLDER, "cap_%s.csv" %(path.basename(fName))), "w")
  # cap_out.write("Anzahl;Wort;kommt vor in\n")
  # for w in cRESULT.values():
  #   cont = "%s;%s;%s\n" %(w.cnt, w.word, w.locationsAsStr())
  #   cap_out.write(cont.encode('latin-1'))
  # cap_out.close()

  # norm_out = open(path.join(PLAIN_FOLDER, "norm_%s.csv" %(path.basename(fName))), "w")
  # norm_out.write("Anzahl;Wort;kommt vor in\n")
  # for w in nRESULT.values():
  #   cont = "%s;%s;%s\n" %(w.cnt, w.word, w.locationsAsStr())
  #   norm_out.write(cont.encode('latin-1'))
  # norm_out.close()


if len(sys.argv) != 2:
  print "foldername missing"
  exit()

createDirIfNeeded(PLAIN_FOLDER)

TO_FILE = False

dirName = sys.argv[1]
print "processing folder %s" %(dirName)
outFolder = path.join(PLAIN_FOLDER, path.basename(dirName))
createDirIfNeeded(outFolder)
outFile = path.join(outFolder, "cap_%s.csv" %(path.basename(dirName)))
print "output is %s " %(outFile)




print "working ..."
RES = {}
for fName in os.listdir(dirName):
  if not fName.endswith(".doc"): continue
  newRES = readDocFile(path.join(dirName, fName))
  for w in newRES.values():
    RES = addWord(RES, w)


if TO_FILE:
  print "Writing to File"
  cap_out = open(outFile, "w")
  cap_out.write("Anzahl;Wort;kommt vor in;\n")
  for w in RES.values():
    cnt = w.cnt
    word = w.word
    loc = w.locationsAsStr().replace(";", ".")
    
    cont = ("%s;%s;%s;\n" %(cnt, word, loc)).encode("latin-1")
    cap_out.write(cont)

  cap_out.close()
else:
  dbh = DBHandler(True)
  for w in RES.values():
    cnt = w.cnt
    word = w.word
    locs = w.locations
    if " " in word: continue 
    wID = dbh.addWord(word, cnt)
    for loc in locs:
      dbh.addLocation(wID, loc.paragraph, int(loc.rdNr))
  
# readDocFile('../tests/doc/P_089-104.doc')

