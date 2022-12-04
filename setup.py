import sys
from cx_Freeze import setup, Executable

base = None
includes = ['tkinter', 'requests', 'dateutil']

if sys.platform == 'win32':
    base = 'Win32GUI'


exe = Executable(script="./app.py", base=base)

setup(name='Wellnote Downloader',
      version='0.1',
      description='Wellnote Downloader',
      options={"build exe": {"includes": includes}},
      executables=[exe])
