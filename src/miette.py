# Miette is "small sweet thing" in french

from cfb.reader import CfbReader
from doc.reader import DocReader
from tools import hex_dump

# r = DocReader('../tests/doc/mw_lorem_ipsum.doc')
r = DocReader('../tests/doc/P_089-104.doc')
#r = DocReader('../tests/doc/gd_lorem_ipsum.doc')
#r = DocReader('../tests/doc/oo_lorem_ipsum.doc')
#r = DocReader('../tests/doc/te_lorem_ipsum.doc')

#r = DocReader('../tests/doc/mw_vesna_yandex_ru.doc')
#r = DocReader('../tests/doc/gd_vesna_yandex_ru.doc')
#r = DocReader('../tests/doc/oo_vesna_yandex_ru.doc')
#r = DocReader('../tests/doc/te_vesna_yandex_ru.doc')

out = open("out", "w")

out.write(r.read())

out.close()
