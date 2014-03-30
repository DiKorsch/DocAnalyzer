# coding=utf-8
from sqlite3 import dbapi2 as Database
import sqlite3
# from sqlite3 import OperationalError, IntegrityError

## DB constants
DB_NAME = "test.sqlite"

TYPE_INT = "INT"
def TYPE_VCHAR(length):
    return "VARCHAR(%d)" %length
TYPE_VCHAR_STANDARD = TYPE_VCHAR(45)

def VALUE_FOR_INSERT(val, TYPE):
    if val == None: return None
    if TYPE.startswith('INT'):
        return "%s" %(unicode(val))
    elif TYPE.startswith('VARCHAR'):
        return "'%s'" %(val)#unicode(val))

KEY_RDNR, KEY_PARA, KEY_DATEI = "rdnrId", "paragraphId", "dateiId"

class wordCache(object):
    
    def __init__(self, value):
        self.word = value.encode("latin-1")
        self.count = 0
        self.para_locations = []
        self.rdnr_locations = []
        self.datei_locations = []

    def inc(self):
        self.count += 1
    
    def addLocation(self, rdnrID, paragraphID, dateiID):
        def add(value, location):
            if value not in location:
                location.append(value)
            return location
        
        self.para_locations = add(paragraphID, self.para_locations)
        self.rdnr_locations = add(rdnrID, self.rdnr_locations)
        self.datei_locations = add(dateiID, self.datei_locations)
            
    def toQuery(self, dbh, queries = []):
        wordId = dbh.nextIndex("wort")
        queries.append("""INSERT INTO wort 
                    (`ID`, `value`, `count`) 
                    VALUES (%d, \'%s\', %d);""" %(wordId, self.word, self.count))
        for dateiId in self.datei_locations:
            word_datei_Id = dbh.nextIndex("wort_datei")
            queries.append("""INSERT INTO wort_datei 
                    (`ID`, `wortID`, `dateiID`) 
                    VALUES (%d, %d, %d);""" %(word_datei_Id, wordId, dateiId))

        for paraId in self.para_locations:
            word_para_Id = dbh.nextIndex("wort_paragraph")
            queries.append("""INSERT INTO wort_paragraph 
                        (`ID`, `wortID`, `paragraphID`) 
                        VALUES (%d, %d, %d);""" %(word_para_Id, wordId, paraId))
        
        for rdnrId in self.rdnr_locations:
            word_rdnr_Id = dbh.nextIndex("wort_rdnr")
            queries.append("""INSERT INTO wort_rdnr 
                    (`ID`, `wortID`, `rdnrID`) 
                    VALUES (%d, %d, %d);""" %(word_rdnr_Id, wordId, rdnrId))
        return queries
        # print query
        # exit(1)

class DBInterface(object):
    tables = [
        [
        'datei', 
            [
                ['name', TYPE_VCHAR(255)],
                ['caption', TYPE_VCHAR(511)],
            ],
        ],[
        'paragraph',
            [
                ['dateiID', TYPE_INT],
                ['caption', TYPE_VCHAR(511)],
            ]
        ],[
        'rdnr',
            [
                ['paragraphID', TYPE_INT],
                ['value', TYPE_INT],
            ]
        ],[
        'wort',
            [
                ['value', TYPE_VCHAR(256)],
                ['count', TYPE_INT],
            ]
        ],[
        'wort_paragraph',
            [
                ['wortID', TYPE_INT],
                ['paragraphID', TYPE_INT],
            ] 
        ],[
        'wort_rdnr',
            [
                ['wortID', TYPE_INT],
                ['rdnrID', TYPE_INT],
            ]
        ],[
        'wort_datei',
            [
                ['wortID', TYPE_INT],
                ['dateiID', TYPE_INT],
            ]
        ]
    ]


    words = {}
    __instance = None
    __initialized = False

    def __init__(self, *args, **kwargs):
        if self.__initialized: return
        self.__initialized = True
        self._dbh = DBHandler()
        self._init_tables()
        super(DBInterface, self).__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        if not cls.__instance: 
            cls.__instance = super(DBInterface, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def _drop(self):
        self.__instance = None

    def _parse_type(self, value, f_type):
        if f_type == TYPE_INT:
            return int(value)
        elif "VARCHAR" in f_type:
            return str(value)
        else:
            raise Exception("Unknown Type!")

    def clear_db(self):
        for tbl_name, __ in self.tables:
            self._dbh.deleteTableContent(tbl_name)

    def _init_tables(self):
        for name, fields in self.tables:
            if not self._dbh.tableExists(name):
                self._dbh.createTable(name, fields)

    def addFile(self, name, caption):
        return self._dbh.addRow('datei', 
            {
                'name': VALUE_FOR_INSERT(name, TYPE_VCHAR_STANDARD),
                'caption': VALUE_FOR_INSERT(caption, TYPE_VCHAR_STANDARD),
            })

    def addParagraph(self, caption, dateiID):
        return self._dbh.addRow('paragraph', 
            {
                'caption': VALUE_FOR_INSERT(caption, TYPE_VCHAR_STANDARD),
                'dateiID': VALUE_FOR_INSERT(dateiID, TYPE_INT),
            })

    def addRdNr(self, value, paragraphID):
        return self._dbh.addRow('rdnr', 
            {
                'value': VALUE_FOR_INSERT(value, TYPE_INT),
                'paragraphID': VALUE_FOR_INSERT(paragraphID, TYPE_INT),
            })

    def addWord(self, value, rdnrID, paragraphID, dateiID):
        cache = self.words.get(value, wordCache(value))
        cache.addLocation(rdnrID, paragraphID, dateiID)
        cache.inc()
        self.words[value] = cache

    def writeWords(self):
        queries = []
        for word in self.words.values():
            queries = word.toQuery(self._dbh, queries)
        for query in queries:
            self._dbh.execute(query) 
        self._dbh.commit()
        self.words.clear()

    def addWord__(self, value, rdnrID, paragraphID, dateiID):
        query = "SELECT `ID`, `count` FROM wort WHERE `value`=\"%s\" LIMIT 1;" %(value)
        res = self._dbh.execute(query)
        if res:
            res = res.fetchall()
        else:
            return -1
        wordID = -1
        if len(res) == 0:
            wordID = self._dbh.addRow('wort', 
                {
                    'value': VALUE_FOR_INSERT(value, TYPE_VCHAR_STANDARD),
                    'count': VALUE_FOR_INSERT(1, TYPE_INT),
                })
        else:
            wordID = res[0][0]
            count = int(res[0][1])
            query = "UPDATE wort SET count = %s WHERE value = \"%s\";" %(count+1, value)
            self._dbh.execute(query)

        wort_datei_id = self._dbh.addRow(
            'wort_datei', 
                {
                    'wortID': VALUE_FOR_INSERT(wordID, TYPE_VCHAR_STANDARD),
                    'dateiID': VALUE_FOR_INSERT(paragraphID, TYPE_INT),
                })
        wort_paragraph_id = self._dbh.addRow(
            'wort_paragraph', 
                {
                    'wortID': VALUE_FOR_INSERT(wordID, TYPE_VCHAR_STANDARD),
                    'paragraphID': VALUE_FOR_INSERT(paragraphID, TYPE_INT),
                })
        wort_rdnr_id = self._dbh.addRow(
            'wort_rdnr', 
                {
                    'wortID': VALUE_FOR_INSERT(wordID, TYPE_VCHAR_STANDARD),
                    'rdnrID': VALUE_FOR_INSERT(rdnrID, TYPE_INT),
                })
        return wordID, wort_rdnr_id, wort_paragraph_id, wort_datei_id

    def getAll(self, name):
        rows = self._dbh.allRows(name)
        fields = []
        result = {}
        for table_name, tbl_fields in self.tables:
            if table_name == name:
                fields = tbl_fields
                break
        i = 1
        for row in rows:
            row_result = {}
            for field_name, f_type in fields:
                row_result[field_name] = self._parse_type(row[i], f_type)
                i += 1
            result[row[0]] = row_result
        return result
     
    def reconnect(self, dbName):
        self._dbh.reconnect(dbName)
        self._init_tables()
        
    def disconnect(self):
        self._dbh.disconnect()
      
    def getWordInfo(self, word):
        try: 
            query = """
              select rdnrVal, paraCap, datei.name as name
                from datei,
                  (select dateiID, rdnrVal, caption as paraCap
                
                  from paragraph,  
                    (SELECT rdnr.value as rdnrVal, paragraphID
                    from rdnr, wort, wort_rdnr
                
                    where wort.value = "%s" and
                    wort_rdnr.wortID = wort.ID and
                    wort_rdnr.rdnrID = rdnr.ID) as t1
                
                  where t1.paragraphID = paragraph.ID
                  ) as t2
                where datei.ID = t2.dateiID"""
            query = query %word
            return self._dbh.execute(query)
        except Exception, e:
            print "getWordInfo:", e

class DBHandler(object):
    LAST_IDX = {}
    __instance = None
    __initialized = False

    def allRows(self, tblName):
        return self.__selectRow(tblName)

    def addRow(self, tblName, fields):
        nextId = self.nextIndex(tblName)
        if nextId < 0:
            raise Exception("ERROR while adding a row")
        query = """INSERT INTO %s
            (`ID`, %s) VALUES (%s, %s);"""
        colNames = u""
        colValues = u""
        for key in fields:
            colNames += "`%s`," % (key)
            colValues += "%s," %(fields[key])
        colNames, colValues = colNames[:-1], colValues[:-1]
        query = query %(tblName, colNames, nextId, colValues)
        self.execute(query)
        self.commit()
        return nextId

    def execute(self, query, throwAnErr = False):
        return self.connection.execute(query)

    def commit(self):
        self.connection.commit()

    def createTable(self, name, fields):
        query = """CREATE TABLE `%s`(
            `ID` INT NOT NULL,
            %s
            PRIMARY KEY (`ID`));""" 
        queryFields = ""
        for f in fields:
            queryFields += "`%s` %s," %tuple(f)
        query = query %(name, queryFields)
        self.execute(query)
        self.commit()

    def tableExists(self, tblName):
        query = "SELECT * FROM `%s` LIMIT 1;" %(tblName)
        try:
            self.execute(query, True)
            self.commit()
            return True
        except sqlite3.OperationalError:
            return False

    def deleteTable(self, name):
        try:
            self.execute("DROP TABLE IF EXISTS `%s`;" %(name))
            self.commit()
        except Exception, e:
            print "deleteTable:", e

    def deleteTableContent(self, name):
        try:
            self.execute("DELETE FROM `%s`;" %(name))
            self.commit()
        except Exception, e:
            print "deleteTableContent:", e
          

    def __deleteNones(self, aDict):
        RESULT = {}
        for key in aDict:
            if aDict[key] != None:
                RESULT.update({key:aDict[key]})
        return RESULT
 
    def __selectRow(self, tblName, fields={}):
        query = "SELECT * FROM %s"
        conditions = ""
        fields = self.__deleteNones(fields)
        for key in fields:
            if key != fields.keys()[0]: 
                conditions += " AND "
            conditions += "%s=%s" %(key, fields[key])

        if conditions != "":
            query += " WHERE %s;"
            query = query %(tblName, conditions)
        else: 
            query += ";"
            query = query %(tblName)
        curs = self.execute(query)
        self.commit()
        return curs.fetchall()
    

    def nextIndex(self, tblName):
        last_idx = self.LAST_IDX.get(tblName, 0) 
        idx = 1
        if last_idx > 0:
            idx = last_idx + 1
        else:
            curs = self.execute("SELECT ID FROM %s ORDER BY ID DESC LIMIT 1" %(tblName))
            self.commit()
            if curs == None: return -1
            rows = curs.fetchall()
            if len(rows) != 0:
                idx = rows[0][0]+1
        self.LAST_IDX[tblName] = idx
        return idx


    def __connect(self, dbName = DB_NAME):
        con = Database.connect(dbName)
        con.text_factory = str
        return con 

    def disconnect(self):
        if self.connection != None: 
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.stopWorker()
        super(DBHandler, self).__del__()

    def __init__(self, *args, **kwargs):
        if self.__initialized: return
        self.__initialized = True
        self.connection = self.__connect()
        # self._query_lock = Lock()
        # self._worker_thread = DBWorker()
        # self._worker_thread.start()
        super(DBHandler, self).__init__(*args, **kwargs)
    
    def reconnect(self, dbName):
        self.disconnect()
        self.connection = self.__connect(dbName)

    def __new__(cls, *args, **kwargs):
        if not cls.__instance: 
            cls.__instance = super(DBHandler, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def _drop(self):
        self.__instance = None


################ TESTS ################
import unittest



class TestSingletons(unittest.TestCase):
    def test_dbi(self):
        dbi1 = DBInterface()
        dbi2 = DBInterface()
        self.assertEqual(id(dbi1), id(dbi2))

    def test_dbh(self):
        dbh1 = DBHandler()
        dbh2 = DBHandler()
        self.assertEqual(id(dbh1), id(dbh2))

class TestDBInterface(unittest.TestCase):
    def setUp(self):
        global DB_NAME
        DB_NAME = "test_dbi.sqlite"
        self.dbi = DBInterface()
        self.dbi.clear_db()

    def test_add_file(self):
        datei = {
            "name": "word.doc",
            "caption": "Das ist nur ein Text!",
        }
        self.dbi.addFile(**datei)
        tbl_content = self.dbi.getAll("datei")
        self.assertEqual(len(tbl_content), 1)
        self.assertEqual(tbl_content.keys()[0], 1)
        self.assertEqual(tbl_content.get(1), datei)

    def test_add_paragraph(self):
        paragraph = {
            "dateiID": 1,
            "caption": "Das ist nur ein Text!",
        }
        self.dbi.addParagraph(**paragraph)
        tbl_content = self.dbi.getAll("paragraph")
        self.assertEqual(len(tbl_content), 1)
        self.assertEqual(tbl_content.keys()[0], 1)
        self.assertEqual(tbl_content.get(1), paragraph)

    def test_add_rdnr(self):
        rdnr = {
            "paragraphID": 2,
            "value": 2,
        }
        self.dbi.addRdNr(**rdnr)
        tbl_content = self.dbi.getAll("rdnr")
        self.assertEqual(len(tbl_content), 1)
        self.assertEqual(tbl_content.keys()[0], 1)
        self.assertEqual(tbl_content.get(1), rdnr)

    def test_add_word(self):
        word = {
            "value": "Wort",
            "rdnrID": 1,
            "paragraphID": 1,
            "dateiID": 1,
        }
        wordID, word_rdnrID, word_paragraphID, word_dateiID = self.dbi.addWord(**word)
        tbl_content = self.dbi.getAll("wort")
        self.assertEqual(len(tbl_content), 1)
        self.assertEqual(tbl_content.keys()[0], wordID)
        self.assertEqual(tbl_content.get(1), {"value": word["value"], "count": 1})

        tbl_content = self.dbi.getAll("wort_rdnr")
        self.assertEqual(len(tbl_content), 1)
        self.assertEqual(tbl_content.keys()[0], word_rdnrID)
        self.assertEqual(tbl_content.get(1), {"rdnrID": word["rdnrID"], "wortID": wordID})

        tbl_content = self.dbi.getAll("wort_paragraph")
        self.assertEqual(len(tbl_content), 1)
        self.assertEqual(tbl_content.keys()[0], word_paragraphID)
        self.assertEqual(tbl_content.get(1), {"paragraphID": word["paragraphID"], "wortID": wordID})

        tbl_content = self.dbi.getAll("wort_datei")
        self.assertEqual(len(tbl_content), 1)
        self.assertEqual(tbl_content.keys()[0], word_dateiID)
        self.assertEqual(tbl_content.get(1), {"dateiID": word["dateiID"], "wortID": wordID})

    def test_add_existing_word(self):
        word = {
            "value": "Wort",
            "rdnrID": 1,
            "paragraphID": 1,
            "dateiID": 1,
        }
        word2 = dict(word)
        word2["rdnrID"] = 2
        wordID, _, __, ___ = self.dbi.addWord(**word)
        wordID2, _, __, ___ = self.dbi.addWord(**word2)
        self.assertEqual(wordID, wordID2)
        tbl_content = self.dbi.getAll("wort")
        self.assertEqual(len(tbl_content), 1)
        self.assertEqual(tbl_content.keys()[0], 1)
        self.assertEqual(tbl_content.get(1), {"value": word["value"], "count": 2})

# if __name__ == "__main__":
#     unittest.main()
