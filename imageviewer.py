from tkinter import *
import PIL, os
from PIL import ImageTk
from zipfile import ZipFile
from base import *

def imageResize(image, max_width, max_height):
    image1 = image
    if image.size[0] > max_width:
        image1 = image.resize((max_width, (int)(image.size[1] * max_width / image.size[0])))
    if image.size[1] > max_height:
        image1 = image.resize(((int)(image.size[0] * max_height / image.size[1]), max_height))
    return image1

def tempPicName(path, page):
    return pathToName(path) + '^' + '{:0>3}'.format(str(page))

def isPic(path):
    suffixes = ['jpg', 'bmp', 'png', 'gif']
    suffix = path.split('.')[-1]
    if suffix in suffixes:
        return True
    return False

def findPicPath(zip_path, tmpDir, page):
    for roots, dirs, files in os.walk(tmpDir):
        for file in files:
            if file.find(tempPicName(zip_path, page)) > -1:
                return os.path.join(roots, file)
    return "# Error 22: The temp picture doesn't exist."

def unzipPic(zip_path, tmpDir, page = 0):
    realLocation = page
    name = zip_path.split('\\')[-1]
    picPath = findPicPath(zip_path, tmpDir, page)
    if not isErrorMsg(picPath):
        return picPath
    count = 0
    try:
        with ZipFile(zip_path, 'r') as z:                        
            for t in range(len(z.infolist())):
                if z.infolist()[t].external_attr != 0x10 and isPic(z.namelist()[t]):
                    if count == page:
                        picName = z.namelist()[t]
                        z.extract(picName, tmpDir)   
                        try:
                            newName = tmpDir + '\\' + name + '^' + '{:0>3}'.format(str(realLocation)) + '.' + picName.split('.')[-1]
                            os.rename(tmpDir + '\\' + picName, newName)
                            return newName
                        except Exception as exc:
                            return ("# Error 99: Python Exception - " + str(exc))
                    count += 1
        return ("# Error 23: Reached the either end of the imagelist.")            
    except Exception as exc:
        return ("# Error 21: Unable to open file: " + zip_path + str(exc))

class ImageViewer:
    def __init__(self, tmpdir):
        self.tmpDir = tmpdir
        self.currentPage = 0
        self.opened = False

    def open(self, zip_path):
        self.opened = True
        self.zip_path = zip_path
        self.top = Toplevel()
        self.top.title(self.zip_path)

        self.labelPic = Label(self.top, height = 40, width = 200)
        self.labelPic.grid(row = 1, column = 1, columnspan = 6)

        self.buttonCover = Button(self.top, text = "To Cover Page(←)", width = 20, command = self._clickCover)        
        self.buttonJumpTo = Button(self.top, text = "Jump to Page(→)", width = 20, command = self._clickJumpTo)
        self.pageVar = StringVar()
        self.entryPage = Entry(self.top, textvariable = self.pageVar, width = 3)
        self.buttonPrev = Button(self.top, text = "Prev Page(↑)", width = 15, command = self._clickPrev)
        self.buttonNext = Button(self.top, text = "Next Page(↓)", width = 15, command = self._clickNext)
        self.buttonCover.grid(row = 2, column = 1)
        self.buttonJumpTo.grid(row = 2, column = 2)
        self.entryPage.grid(row = 2, column = 3)
        self.buttonPrev.grid(row = 2, column = 4)
        self.buttonNext.grid(row = 2, column = 5) 

        self._clickCover()
        self._bindKey()

        self.top.focus_get()
        self.top.mainloop()
        return ""

    def close(self):
        if self.opened:
            self.top.destroy()
            self.opened = False

    def _loadPic(self, path, newcP = 0):
        msg = 'Open image from path "' + path + '".'
        image = PIL.Image.open(path)
        image = imageResize(image, 1080, 600)
        render = ImageTk.PhotoImage(image)
        self.labelPic.config(height = image.size[1], width = image.size[0], image = render)
        self.labelPic.image = render                
        self.currentPage = newcP

    def _keyJumpTo(self, event = None):
        self._clickJumpTo()
        self.top.focus_get()

    def _clickJumpTo(self):
        page = self.pageVar.get()
        if not page.isnumeric() or int(page) > 999 or int(page) < 0:
            return "# Error 24: Please enter a number(0 - 999)."
        page = int(page)
        picPath = unzipPic(self.zip_path, self.tmpDir, page)
        if not isErrorMsg(picPath):
            self._loadPic(picPath, page)
        
    def _keyCover(self, event = None):
        self._clickCover()
        self.top.focus_get()

    def _clickCover(self):
        picPath = unzipPic(self.zip_path, self.tmpDir, 0)
        if not isErrorMsg(picPath):
            self._loadPic(picPath, 0)

    def _keyPrev(self, event = None):
        self._clickPrev()
        self.top.focus_get()

    def _clickPrev(self):
        picPath = unzipPic(self.zip_path, self.tmpDir, self.currentPage - 1)
        if not isErrorMsg(picPath):
            self._loadPic(picPath, self.currentPage - 1)

    def _keyNext(self, event = None):
        self._clickNext()
        self.top.focus_get()

    def _clickNext(self):
        picPath = unzipPic(self.zip_path, self.tmpDir, self.currentPage + 1)
        if not isErrorMsg(picPath):
            self._loadPic(picPath, self.currentPage + 1)
    
    def _bindKey(self):
        self.top.bind("<Up>", self._keyPrev)
        self.top.bind("<Down>", self._keyNext)
        self.top.bind("<Left>", self._keyCover)
        self.top.bind("<Right>", self._keyJumpTo)
