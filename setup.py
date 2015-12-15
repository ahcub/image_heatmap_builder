import sys
from distutils.core import setup
import py2exe
from glob import glob
from os.path import join, dirname

setup(windows=[{'script': 'launcher.py', "icon_resources": [(0, join(dirname(sys.argv[0]), 'heatmap_icon.ico'))]}],
      options={"py2exe": {"includes": ["sip"], 'bundle_files': 2, 'compressed': True}}, requires=['PyQt4'],
      zipfile=None,
      data_files=[('.', glob(join(r'C:\Python34\Lib\site-packages', 'cHeatmap-x86.dll'))),
                  ('.', [join(dirname(sys.argv[0]), 'heatmap_icon.png')])],)
