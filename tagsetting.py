#-*- coding:utf-8 -*-

from base import *
import os, sys, pickle
from zipfile import ZipFile

class TaggedDataList:
    def __init__(self):
        self.tdlist = {}
        self.is_empty = True

    def readFile(self):
        try:
            with open(sys.path[0] + '\\tagged_data.dat', 'rb') as infile:
                end_of_file = False
                while not end_of_file:
                    try:
                        self.tdlist = pickle.load(infile)
                    except:
                        end_of_file = True
            self.is_empty = False
            return 'Tagged datalist imported.'
        except:
            return '# Error 08: Cannot find "tagged_data.dat" in directory.'

    def addTag(self, path, tag):
        try:
            tdata = self.tdlist[pathToKey(path)]
            return tdata.addTag(tag)
        except KeyError as ke:
            self.tdlist[pathToKey(path)] = TaggedData()
            self.tdlist[pathToKey(path)].sendInPath(path)
            self.tdlist[pathToKey(path)].addTag(tag)

    def deleteTag(self, path, tag):
        try:
            tdata = self.tdlist[pathToKey(path)]
            return tdata.deleteTag(tag)
        except KeyError as ke:
            return "# Error 31: File not found in tdlist."

    def getZipTags(self, path):
        try:
            tdata = self.tdlist[pathToKey(path)]
            return tdata.tag_list
        except:
            return []

    def getPathWithTags(self, tag):
        path_list = []
        for key in self.tdlist:
            if tag in self.tdlist[key].tag_list:
                path_list.append(self.tdlist[key].path)
        return path_list

    def writeFile(self):
        with open(sys.path[0] + '\\tagged_data.dat', 'wb') as outfile:
            pickle.dump(self.tdlist, outfile)

    def isEmpty(self):
        return self.is_empty

class TaggedData:
    def __init__(self):
        self.file_size = -1
        self.first_pic_size = -1
        self.path = ""
        self.tag_list = []
    
    def getKey(self):
        return str(self.file_size) + '|' + str(self.first_pic_size)

    def sendInPath(self, path):
        if checkIfZipPath(path):
            self.path = path
            self.file_size = os.stat(path).st_size        
            with ZipFile(path, 'r') as z:
                self.first_pic_size = z.infolist()[0].file_size            

    def matchFile(self, path):        
        with ZipFile(path, 'r') as z:
            if self.first_pic_size != z.infolist()[0].file_size:
                return False
        if os.stat(path).st_size != self.file_size:
            return False
        self.path = path
        return True

    def matchSize(self, fsize, psize):
        return self.first_pic_size == psize and self.file_size == fsize

    def addTag(self, tag):
        if tag not in self.tag_list:
            self.tag_list.append(tag)
            return 'Add tag "' + tag + '".'
        else:
            return 'Tag "' + tag + '" already exists.'

    def deleteTag(self, tag):
        try:
            self.tag_list.remove(tag)
            return 'Remove tag "' + tag + '".'
        except KeyError:
            return '# Error 32: The manga doesn\'t have tag "' + tag + '".'

    def checkMatch(path):
        if self.file_size != os.stat(path).st_size:
            return False
        return True

    def getTag(self):
        return self.tag_list

    


class TagSetting:
    def __init__(self):
        self.tag_list = set()
        self.setFile = False

    def readFile(self):
        self.tag_list.clear()
        try:
            with open(sys.path[0] + "\\tags.dat", 'rb') as infile:  
                end_of_file = False
                while not end_of_file:
                    try:
                        tag = pickle.load(infile)      
                        self.tag_list.add(tag)
                    except:
                        end_of_file = True    
            return "Tags imported."              
        except:
            return "# Error 00: 'tags.dat' doesn't exist."
    
    def addTag(self, newTag):
        self.tag_list.add(newTag)
        self.rewrite()
        return 'Add tag "' + newTag + '".'

    def deleteTag(self, delTag):
        self.tag_list.discard(delTag)
        self.rewrite()
        return 'Delete tag "' + delTag + '".'

    def reset(self, tupleTag):
        try:
            self.tag_list.clear()
            for tag in tupleTag:
                self.tag_list.add(tag)
            self.rewrite()
            return "Tag List Reset."
        except Exception as exc:
            return str(exc)

    def rewrite(self):
        with open(sys.path[0] + "\\tags.dat", 'wb') as outfile:
            for tag in self.tag_list:                
                pickle.dump(tag, outfile)

    def get(self):
        return self.tag_list