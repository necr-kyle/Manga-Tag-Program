# MangaTagProgram v0.5

import os, sys, tempfile
from tagsetting import TagSetting, TaggedDataList
from tkinter import *
from base import *
from imageviewer import ImageViewer
from zipfile import ZipFile

class TagGUI:
    def __init__(self, tmpDir):
        self.tmpDir = tmpDir
        self.tagSetting = TagSetting()
        self.taggedDataList = TaggedDataList()
        self.fileTagChanged = False
        self.curPage = 0
        self.imageViewer = ImageViewer(self.tmpDir)

        self.window = Tk()
        self.window.title("Manga Tag Program")

        self.labelDir = Label(self.window, text = 'Input Directory:')
        self.dirVar = StringVar()
        self.entryDir = Entry(self.window, textvariable = self.dirVar, width = 40)
        self.labelSearch = Label(self.window, text = 'Input keywords:')
        self.searchVar = StringVar()
        self.entrySearch = Entry(self.window, textvariable = self.searchVar, width = 20)
        self.buttonSearch = Button(self.window, text = "Search", command = self.searchFileWithKeyword) 
        self.labelDir.grid(row = 1, column = 1)
        self.entryDir.grid(row = 1, column = 2, columnspan = 2)
        self.labelSearch.grid(row = 1, column = 4)
        self.entrySearch.grid(row = 1, column = 5)
        self.buttonSearch.grid(row = 1, column = 6)
        
        self.listPath = Listbox(self.window, height = 12, width = 100, borderwidth = 4)  
        self.listPath.grid(row = 2, column = 1, columnspan = 6)

        self.buttonOpenDir = Button(self.window, text = "Open Directory", width = 16, command = self.openDirectory)
        self.labelCurDir = Label(self.window, text = "Current Directory:", width = 20)
        self.textCurDir = Text(self.window, height = 1, width = 60)
        self.buttonOpenDir.grid(row = 3, column = 1)    
        self.labelCurDir.grid(row = 3, column = 2)
        self.currentDir = ""
        self.textCurDir.grid(row = 3, column = 3, columnspan = 4)
        self.textCurDir.config(state = DISABLED)

        self.buttonOpenFile = Button(self.window, text = "Open File", width = 16, command = self.openFile)
        self.labelCurFile = Label(self.window, text = "Current File:", width = 20)
        self.textCurFile = Text(self.window, height = 1, width = 60)
        self.buttonOpenFile.grid(row = 4, column = 1)    
        self.labelCurFile.grid(row = 4, column = 2)
        self.currentFile = ""
        self.textCurFile.grid(row = 4, column = 3, columnspan = 4)
        self.textCurFile.config(state = DISABLED)
        
        self.labelListTag = Label(self.window, text = "List of Tags:", width = 20)
        self.labelListFileTag = Label(self.window, text = "List of File Tags:", width = 20)
        self.labelListTag.grid(row = 5, column = 1, columnspan = 2)
        self.labelListFileTag.grid(row = 5, column = 4, columnspan = 3)
        
        self.listTag = Listbox(self.window, height = 12, width = 40, borderwidth = 4)
        self.listFileTag = Listbox(self.window, height = 12, width = 40, borderwidth = 4)
        self.listTag.grid(row = 6, column = 1, rowspan = 6, columnspan = 2)
        self.listFileTag.grid(row = 6, column = 4, rowspan = 6, columnspan = 3)

        self.buttonSearchWithTag = Button(self.window, text = "↑ Find File with Tag", width = 20, command = self.searchFileWithTag)
        self.buttonAddTag = Button(self.window, text = "<---┐Add Tag", width = 20, command = self.addTag)        
        self.tagVar = StringVar()
        self.entryTag = Entry(self.window, textvariable = self.tagVar, width = 20)
        self.buttonDeleteTag = Button(self.window, text = "<-x--Delete Tag", width = 20, command = self.deleteTag)
        self.buttonAddFileTag = Button(self.window, text = "---Add to File--->", width = 20, command = self.addFileTag)        
        self.buttonDeleteFileTag = Button(self.window, text = "Delete File Tag--x-->", width = 20, command = self.deleteFileTag)        
        self.buttonSearchWithTag.grid(row = 6, column = 3)
        self.buttonAddTag.grid(row = 7, column = 3)
        self.entryTag.grid(row = 8, column = 3)
        self.buttonDeleteTag.grid(row = 9, column = 3)
        self.buttonAddFileTag.grid(row = 10, column = 3)
        self.buttonDeleteFileTag.grid(row = 11, column = 3)

        self.textMessage = Text(self.window, height = 4, width = 100)
        self.textMessage.grid(row = 12, column = 1, rowspan = 2, columnspan = 6)

        self.loadTags()
        self.addMessage(self.textMessage, self.taggedDataList.readFile())
        
        self.entryDir.focus_get()
        self.window.mainloop()
        if self.fileTagChanged:
            self.fileTagChanged = False
            self.taggedDataList.writeFile()
        

    def openDirectory(self):   
        if not checkIfPath(self.dirVar.get()):
            self.addMessage(self.textMessage, "# Error 00: Directory \"" + self.dirVar.get() + "\" doesn't exist.")
            return
        self.listPath.delete(0, END)
        try:
            for roots, dirs, files in os.walk(self.dirVar.get()):
                for file in files:
                    if file.find('.zip') > -1:
                        self.listPath.insert(END, os.path.join(roots, file))
            self.currentDir = self.dirVar.get()
            self.addMessage(self.textCurDir, self.currentDir, True)
        except:
            self.addMessage(self.textMessage, "# Error 01: Unable to open directory: \"" + self.dirVar.get() + '".')

    def openFile(self):
        path = self.listPath.get(ANCHOR)
        if path == '':
            self.addMessage(self.textMessage, "# Error 02: Please select a file from the list of tags.")
            return 
        if not checkIfZipPath(path):
            self.addMessage(self.textMessage, "# Error 03: Zip file \"" + self.dirVar.get() + "\" doesn't exist.")
            return
        self.listFileTag.delete(0, END)
        if self.fileTagChanged:
            self.fileTagChanged = False
            self.taggedDataList.writeFile()
        if not self.taggedDataList.isEmpty():
            self.loadFileTags(path)
        self.currentFile = path
        self.addMessage(self.textCurFile, path, True)
        self.imageViewer.close()
        self.imageViewer.open(path)

    def searchFileWithKeyword(self):
        if self.searchVar.get() == '':
            return
        j = 0
        for i in range(self.listPath.size()):
            path = self.listPath.get(i - j)
            name = pathToName(path)
            if name.find(self.searchVar.get()) < 0:                
                self.listPath.delete(i - j)
                j += 1

    def searchFileWithTag(self):
        tag = self.listTag.get(ANCHOR)
        if tag == "":
            return '# Error 23: Please select a tag from the list of tags.'
        self.listPath.delete(0, END)
        for path in self.taggedDataList.getPathWithTags(tag):
            self.listPath.insert(END, path)
        return 'All files with tag "' + tag + '" are listed.'

    def loadTags(self):           
        msg = self.tagSetting.readFile()     
        if msg.find('# Error') < 0:            
            for tag in self.tagSetting.get():
                self.listTag.insert(END, tag)
        self.addMessage(self.textMessage, msg)
    
    def loadFileTags(self, zipfile):
        for tag in self.taggedDataList.getZipTags(zipfile):
            self.listFileTag.insert(END, tag)

    def addTag(self):        
        if self.tagVar.get() != '':
            self.listTag.insert(END, self.tagVar.get())
            msg = self.tagSetting.addTag(self.tagVar.get())        
        else:
            msg = "# Error 20: Empty Input in entryTag."
        self.addMessage(self.textMessage, msg)

    def deleteTag(self):
        msg = self.tagSetting.deleteTag(self.listTag.get(ANCHOR))
        self.listTag.delete(ANCHOR)
        self.addMessage(self.textMessage, msg)

    def addFileTag(self):
        if self.currentFile == '':
            msg = "# Error 22: Please start with opening a file."
            self.addMessage(self.textMessage, msg)
            return
        if self.listTag.get(ANCHOR) != '':
            self.listFileTag.insert(END, self.listTag.get(ANCHOR))
            msg = self.taggedDataList.addTag(self.currentFile, self.listTag.get(ANCHOR))
            self.fileTagChanged = True
        else:
            msg = "# Error 21: Please select a tag from the taglist at left side."
        self.addMessage(self.textMessage, msg)

    def deleteFileTag(self):
        if self.currentFile == '':
            msg = "# Error 22: Please start with opening a file."
            self.addMessage(self.textMessage, msg)
            return
        if self.listFileTag.get(ANCHOR) != '':
            msg = self.taggedDataList.deleteTag(self.currentFile, self.listFileTag.get(ANCHOR))
            self.listFileTag.delete(ANCHOR)
            self.fileTagChanged = True
        else:
            msg = "# Error 23: Please select a tag from the taglist above."
        self.addMessage(self.textMessage, msg)

    def addMessage(self, msgbox, msg, single_line = False):
        msgbox.config(state = NORMAL)
        try:            
            if single_line:
                msgbox.insert(END, msg)
                msgbox.delete(0.0, END)
                msgbox.insert(END, msg)
            else:
                msgbox.insert(END, msg + '\n')           
        except:
            msgbox.config(state = DISABLED)
        msgbox.config(state = DISABLED)
        msgbox.see(END)
        
with tempfile.TemporaryDirectory() as tmpDir:  
    TagGUI(tmpDir)
