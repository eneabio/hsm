#! python
import os
#it's necessary install sphinx
#first of all >python setup.py build_scripts
#after run this script from the directory where is setup.py:
#>python scripts/build_doc.py

os.system("mkdir ./docs/rst")
os.system("sphinx-apidoc -o ./docs/rst ./hsm")
os.system("cd ./docs/rst")
os.system("sphinx-quickstart")
os.system("cd ..")
os.system("mv conf.py ./docs/rst")
os.system("mv index.rst ./docs/rst")
os.system("sphinx-build -b html ./docs/rst ./docs/_build") 
os.system("rmdir _build")
os.system("rmdir _static")
os.system("rmdir _templates")

print "Build doc"
