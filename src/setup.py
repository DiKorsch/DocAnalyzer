from distutils.core import setup
import py2exe

setup(name="liftr",
      version="0.1",
      author="Dimitri Korsch",
      author_email="korschdima@yahoo.de",
      license="GNU General Public License (GPL)",
      packages=['ui','ui.windows','cfb','doc','tools'],
      package_data={"liftr": ["ui/*"]},
      scripts=["main.py"],
      windows=[{"script": "main.py"}],
      options={
         "py2exe": {
#              "skip_archive": True,
             "includes": ["sip", "sqlite3"],
              "dll_excludes": [
                  "MSVCP90.dll",
                  "MSWSOCK.dll",
                  "mswsock.dll",
                  "powrprof.dll",
                  ],
          }
      })