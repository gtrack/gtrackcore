import os
import shutil

def removeFile(fn):
    if os.path.exists(fn):
         os.remove(fn)

def removeDirectoryTree(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    