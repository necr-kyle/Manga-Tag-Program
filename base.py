import os, sys
from zipfile import ZipFile

def isErrorMsg(msg):
    if msg.find("# Error") > -1:
        return True
    return False

def checkIfPath(path):
    return os.path.exists(path) and os.path.isdir(path)

def checkIfZipPath(path):
    return (path.find('.zip') > -1) and os.path.exists(path) and os.path.isfile(path)

def pathToName(path):  
    return path.split('\\')[-1]

def pathToKey(path):
    file_size = os.stat(path).st_size        
    with ZipFile(path, 'r') as z:
        first_pic_size = z.infolist()[0].file_size
    return str(file_size) + '|' + str(first_pic_size)

