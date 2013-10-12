import sys
from os import path

if __name__ != "__main__":
    print "This file should not be imported!"
    exit()


USAGE = "Usage: \n\t%s <file name>" %(path.basename(sys.argv[0]))

if len(sys.argv) != 2:
    print USAGE
    exit()

fName = sys.argv[1]
if not path.isfile(fName):
    print USAGE
    exit()

baseName = path.splitext(path.basename(fName))[0]

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


f = open(fName)

normalWordList = []
capWordList = []

for line in f:
    words = extractWords(line)
    for word in words:
        if word in normalWordList or word in capWordList:
            continue
        if capitalized(word):
            capWordList.append(word)
        else:
            normalWordList.append(word)
f.close()

capWordList.sort()
normalWordList.sort()

capOutFile = open("cap_%s.out" %baseName, "w")
normOutFile = open("norm_%s.out" %baseName, "w")

for word in capWordList:
    capOutFile.write("%s\n" %(word))

for word in normalWordList:
    normOutFile.write("%s\n" %(word))

capOutFile.close()
normOutFile.close()