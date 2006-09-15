#!/usr/bin/python
# -*- coding: utf8 -*-
#
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Keo Sophon (keosophon@khmeros.info)about:blank
#

from PyQt4 import QtCore, QtGui
from translate.storage import factory
from translate.tools import pocount

class Operator(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.store = None
        self._offset = None
        self._backward = None
        self._insource = None
        self._incomment = None
        self._intarget = None
        self._sourcesearch = None
        self._targetsearch = None
        self._commentsearch = None        
        self._matchcase = None              
        self.matchlength = None 
        self._modified = False
        self._saveDone = False
        
        self._unitpointer = None
    
    def getUnits(self, fileName):
        self.store = factory.getobject(fileName)

        # get status for units       
        self.numFuzzy = len(pocount.fuzzymessages(self.store.units))
        self.numTranslated = len(pocount.translatedmessages(self.store.units))
        self.numUntranslated = len(pocount.untranslatedmessages(self.store.units))
        self.numTotal = self.numTranslated + self.numUntranslated
        self.emitCurrentStatus()
        
        self.filteredList = range(len(self.store.units))
        self.emit(QtCore.SIGNAL("newUnits"), self.store.units)
        
        self._unitpointer = 0
        self.emitCurrentUnit()

    def emitCurrentUnit(self):
        if (self._unitpointer == 0):
            self.emit(QtCore.SIGNAL("firstUnit"))
        elif (self._unitpointer == len(self.filteredList) - 1):
            self.emit(QtCore.SIGNAL("lastUnit"))
        else:
            self.emit(QtCore.SIGNAL("middleUnit"))
        currentUnit = self.getCurrentUnit()
        if (currentUnit != len(self.store.units)):
            self.emit(QtCore.SIGNAL("currentUnit"), self.store.units[currentUnit])
            self.emit(QtCore.SIGNAL("currentPosition"), currentUnit)
            print 'currentUnit', currentUnit

    def getCurrentUnit(self):
        try:
            return self.filteredList[self._unitpointer]
        except IndexError:
            return 0
##        
##    def emitNewUnits(self, filter = None):
##        self._unitpointer = 0
##        self.unitPointerList = []
##        self.visibleUnits = []
##        if (filter == 'fuzzy'):
##            #self.visibleUnits = pocount.fuzzymessages(self.store.units)
##            for i in range(len(self.store.units)):
##                if (self.store.units[i].isfuzzy()):
##                    self.unitPointerList.append(i) # id
##                    self.visibleUnits.append(self.store.units[i]) # unit
##        elif (filter == 'translated'):
##            #self.visibleUnits = pocount.translatedmessages(self.store.units)
##            for i in range(len(self.store.units)):
##                if (self.store.units[i].istranslated()):
##                    self.unitPointerList.append(i)
##                    self.visibleUnits.append(self.store.units[i]) # unit
##        elif (filter == 'untranslated'):
##            #self.visibleUnits = pocount.untranslatedmessages(self.store.units)
##            for i in range(len(self.store.units)):
##                if (not self.store.units[i].istranslated()):
##                    self.unitPointerList.append(i)
##                    self.visibleUnits.append(self.store.units[i]) # unit
##        else:
##            self.visibleUnits = self.store.units
##            self.unitPointerList = range(len(self.visibleUnits))
##        
##        #if (len(self.visibleUnits) > 0) and (self.visibleUnits[0].isheader()):
##        #    self.visibleUnits.pop(0)
##        #print 'number of filtered units is', len(self.unitPointerList)
##        self.emit(QtCore.SIGNAL("newUnits"), self.visibleUnits, self.unitPointerList)

    def emitFilteredList(self, filter):
        #pocount.fuzzymessages(self.store.units)
        self._unitpointer = 0
        self.filteredList = []
        if (not filter):
            self.filteredList = range(len(self.store.units))
        else:
            for i in range(len(self.store.units)):
                if (filter == 'fuzzy' and self.store.units[i].isfuzzy()) \
                or (filter == 'translated' and self.store.units[i].istranslated()) \
                or (filter == 'untranslated' and not self.store.units[i].istranslated()):
                    self.filteredList.append(i)
        self.emit(QtCore.SIGNAL("filteredList"), self.filteredList)
        self.emitCurrentUnit()
    
    def emitUpdateUnit(self):
        if (self._unitpointer != None):
            self.emit(QtCore.SIGNAL("updateUnit"))    

    def takeoutUnit(self, value):
        return
        self.unitpointer = value - 1
        if self.unitpointer < 0:
            self.unitpointer = 0
    
    def previous(self):
        if self._unitpointer > 0:
            self.emitUpdateUnit()
            self._unitpointer -= 1
            self.emitCurrentUnit()
        
    def next(self):
        # move to next unit inside the list, not the whole store.units
        if self._unitpointer < len(self.filteredList):
            self.emitUpdateUnit()
            #if (self._unitpointer == len(self.filteredList) - 1):
            #    self._unitpointer -= 1
            self._unitpointer += 1
            self.emitCurrentUnit()
        
    def first(self):
        self.emitUpdateUnit()
        self._unitpointer = 0
        self.emitCurrentUnit()
        
    def last(self):
        self.emitUpdateUnit()
        self._unitpointer = len(self.filteredList) - 1
        self.emitCurrentUnit()

    def saveStoreToFile(self, fileName):
        self.emitUpdateUnit()
        self.store.savefile(fileName)
        self._saveDone = True

    def modified(self):
        self.emitUpdateUnit()
        if self._saveDone:
            self._modified = False
            self._saveDone = False
        return self._modified
    
    def setComment(self, comment):
        """set the comment which is QString type to the current unit."""
        currentUnit = self.getCurrentUnit()
        #self.store.units[currentUnit].removenotes()
        self.store.units[currentUnit].addnote(unicode(comment))
        self._modified = True        
    
    def setTarget(self, target):
        """set the target which is QString type to the current unit."""
        unit = self.getCurrentUnit()
        currentUnit = self.store.units[unit]
        before_isuntranslated = not currentUnit.istranslated()
        unitIsFuzzy = currentUnit.isfuzzy()
        currentUnit.target = unicode(target)
        if (currentUnit.target != ''):
            try:
                self.store.units[unit].marktranslated()
            except AttributeError:
                pass
            if (unitIsFuzzy):
                self.numFuzzy -= 1
                self.store.units[unit].markfuzzy(False)
        after_istranslated = currentUnit.istranslated()
        if (before_isuntranslated and after_istranslated):
            self.numTranslated += 1
            # send takeout current unit signal
            self.emit(QtCore.SIGNAL("takeoutUnit"), self._unitpointer)
        elif (not before_isuntranslated and not after_istranslated):
            self.numTranslated -= 1
            # send takeout current unit signal
            self.emit(QtCore.SIGNAL("takeoutUnit"), self._unitpointer)
        self.emitCurrentStatus()
        self._modified = True

    def setCurrentUnit(self, value):
        self.emitUpdateUnit()
        try:
            self._unitpointer = self.filteredList.index(value)
        except ValueError:
            self._unitpointer = 0
        self.emitCurrentUnit()
   
    def toggleFuzzy(self):
        """toggle fuzzy state for current unit"""
        unit = self.getCurrentUnit()
        unitIsFuzzy = self.store.units[unit].isfuzzy()
        if (unitIsFuzzy):
            self.store.units[unit].markfuzzy(False)
            self.numFuzzy -= 1
            # send takeout current unit signal
            self.emit(QtCore.SIGNAL("takeoutUnit"), self._unitpointer)
        else:
            self.store.units[unit].markfuzzy(True)
            self.numFuzzy += 1
        
        print 'after fuzzied:', self.store.units[unit].isfuzzy()           
        self._modified = True
        self.emitCurrentStatus()
    
    def emitCurrentStatus(self):
        self.numUntranslated = self.numTotal - self.numTranslated
        status = "Total: "+ str(self.numTotal) + "  |  Fuzzy: " +  str(self.numFuzzy) + "  |  Translated: " +  str(self.numTranslated) + "  |  Untranslated: " + str(self.numUntranslated)
        self.emit(QtCore.SIGNAL("currentStatus"), status)
    
    def startSearch(self, text):                        
        self._offset = 0        
        self._backward = False        
        self._insource = True
        self._incomment = False
        self._intarget = False   
        #unit = self.getCurrentUnit()
        unitpointer = self._unitpointer
        while (( unitpointer <=  len(self.store.units) - 1) and unitpointer != None):                    
            unitpointer = self.search(0, unitpointer, text)                    
        else:                        
            self.displayMessageBox(unitpointer)

    def searchNext(self, text):          
        self._backward = False       
        unitpointer = self._unitpointer
        while (( unitpointer <=  len(self.filteredList) - 1) and unitpointer != None):
            unitpointer = self.search(self._offset + 1, unitpointer, text)
        else:
            self.displayMessageBox(unitpointer)
        
    def searchPrevious(self, text):                
        self._backward = True
        unitpointer = self._unitpointer
        if (self._offset == 0):
            if (self._unitpointer != 0):                
                if (self._insource):                
                    unitpointer = self._unitpointer - 1
                self.setFlagsPrevious()
            else:
                if (not self._insource):                
                    self.setFlagsPrevious()
                else:
                    unitpointer = self._unitpointer - 1        
        while (unitpointer >= 0 and unitpointer != None):
            unitpointer = self.search(self._offset - 1, unitpointer, text)
        else:
            self.displayMessageBox(unitpointer)            
                
    def search(self, offset, unitpointer, text):
        temp = None        
        if (self.filteredList):
            searchString = ''
            if (self._sourcesearch and self._insource):
                searchString = self.store.units[self.filteredList[unitpointer]].source
    
            if (self._commentsearch and self._incomment):
                searchString = self.store.units[self.filteredList[unitpointer]].getnotes()
    
            if (self._targetsearch and self._intarget):
                searchString = self.store.units[self.filteredList[unitpointer]].target
                
            temp = self.searchedIndex(offset, searchString, text)
        # when found in source, comment or target, it will emit signal
        # in order to go to highlight place and put highlight.        
        if (temp != -1 and temp != None):
            self._offset = temp
            self._unitpointer = unitpointer
            if (self._insource):                            
                self.emitFoundInSource()
            if (self._incomment):                            
                self.emitFoundInComment()
            if (self._intarget):                                    
                self.emitFoundInTarget()                                        
            return None
        
        # when search not found, it will decrease/increase unit depending on search previous or next
        if (temp == -1 or temp == None):                     
            if (self._backward):                
                if (self._insource):                              
                    unitpointer -= 1
                self.setFlagsPrevious()                
                self._offset = 0
            else:
                if (self._intarget):
                    unitpointer += 1
                self.setFlagsNext()
                self._offset = -1
            return unitpointer
            
    def setFlagsPrevious(self):
        if (self._intarget):             
            self._incomment = True
            self._intarget = False                    
            self._insource = False            
        elif (self._incomment):                                
            self._insource = True
            self._incomment = False
            self._intarget = False                                                                
        else:                                           
            self._intarget = True
            self._incomment = False
            self._insource = False

    def setFlagsNext(self):
        if (self._insource):
            self._incomment = True
            self._insource = False
            self._intarget = False                    
        elif (self._incomment):                    
            self._intarget = True
            self._insource = False
            self._incomment = False                    
        else:                                    
            self._insource = True
            self._incomment = False
            self._intarget = False             

    def searchedIndex(self, offset, stringofunit, text):
        if (self._matchcase):
            regexp = QtCore.QRegExp(text)
        else:
            regexp = QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive)
        if (self._backward):
            temp = regexp. lastIndexIn(stringofunit, offset)                        
        else:                      
            temp = regexp.indexIn(stringofunit, offset)                                        
        self._matchlength = regexp.matchedLength()        
        return temp  
    
    def displayMessageBox(self, unit):        
        if (unit < 0 and unit != None):            
            ret = QtGui.QMessageBox.information(None, self.tr("Search Not Found"), self.tr("Not Found, Search Reached The Beginning of First String"), QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)                            

        if (unit > (len(self.filteredList) - 1)):
            ret = QtGui.QMessageBox.information(None, self.tr("Search Not Found"), self.tr("Not Found, Search Reached The End of Last String"), QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)                
    
    def toggleSourceSearch(self, bool):
        '''when source checkbox is checked, it will search in Source'''
        self._sourcesearch = bool        
             
    
    def toggleTargetSearch(self, bool):
        '''when target checkbox is checked, it will search in Target'''
        self._targetsearch = bool        
    
    def toggleCommentSearch(self, bool):
        '''when comment checkbox is checked, it will search in Comment'''
        self._commentsearch = bool        
        
    def toggleMatchCase(self, bool):
        '''set Default case insensitive, if match case checked box it will case sensitive'''
        self._matchcase = bool        
    
    def emitFoundInSource(self):        
        self.setCurrentUnit(self.filteredList[self._unitpointer])
        self.emit(QtCore.SIGNAL("foundInSource"))        
    
    def emitFoundInComment(self):        
        self.setCurrentUnit(self.filteredList[self._unitpointer])
        self.emit(QtCore.SIGNAL("foundInComment"))
    
    def emitFoundInTarget(self):        
        self.setCurrentUnit(self.filteredList[self._unitpointer])
        self.emit(QtCore.SIGNAL("foundInTarget"))
        
    def setHighLight(self, docPointer):               
        self.highlight = HighLight(docPointer)                
        self.highlight.setOffset(self._offset)
        self.highlight.setMatchLength(self._matchlength)            
       
class HighLight(QtGui.QSyntaxHighlighter):
    # TODO : Fix to unhighlight when not found
    # TODO : Fix wrong highlight when have space at the beginning of text.
    # TODO: Fix double highlight
    # TODO: Clear when not highlight, return to the last state    
    # TODO: Fix keyrelease Fixed
    # TODO: When Pressed Enter Key Search Next
    
    def __init__(self, searchstring):            
        QtGui.QSyntaxHighlighter.__init__(self, searchstring)                    
    
    def setOffset(self, offset):
        self._offset = offset
    
    def setMatchLength(self, matchedLength):
        self._matchlength = matchedLength
    
    def highlightBlock(self, searchstring):        
        #print self.previousBlockState()
        self.format = QtGui.QTextCharFormat ()
        self.format.setFontWeight(QtGui.QFont.Bold)
        self.format.setForeground(QtCore.Qt.darkMagenta)                
        self.setFormat(self._offset, self._matchlength, self.format)         
