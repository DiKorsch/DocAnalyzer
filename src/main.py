
if __name__ == '__main__':
    from fileReader import Reader
    from os import path
    from dbhandler import DBInterface
    
    DBInterface().clear_db()
    reader = Reader()
    reader.save_file(path.abspath("../tests/Paragraphen/P_001-007.doc"))
    
    reader.write()
