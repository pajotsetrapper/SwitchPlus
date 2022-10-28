#!/usr/bin/python

"""
__version__ = "$Revision: 0.0.2 $"
__date__ = "$Date: 2004/11/30 21:30:00 $"

Switch+ 0.0.2 by Pieter Coppens - a tool to change your wallpaper periodically
Copyright (C) 2004-2005 Pieter Coppens
Mail: pieter_coppens@yahoo.com
URL: http://www.geocities.com/pieter_coppens

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""

import time, calendar, Image, os, string, random, ConfigParser, threading
import wx, win32gui, win32api, win32con, ctypes, imagefilters
from PythonCardPrototype import model, dialog, EXIF
from PythonCardPrototype.components import button
from PythonCardPrototype.components import textarea
from PythonCardPrototype.components import staticbox
from PythonCardPrototype.components import statictext
from PythonCardPrototype.components import spinner
import JpegImagePlugin, BmpImagePlugin
Image._initialized = 1
from wxPython.wx import *

class SwitchPlus(model.Background):        
    
    #-------------------------------------#
    #Event handlers for the user interface#
    #-------------------------------------#
        
    def on_openBackground(self, event):             
        
        # Set the default values        
        self.imageList = []        
        self.remainingImageList = []
        self.screenWidth = 0
        self.screenHeight = 0
        self.interval = 3600
        self.elapsedInterval = 0
        self.randomIndicator = '0'
        self.hideIconsIndicator = '0'
        self.autoStart = '1'
        self.highresonly = '1'
        self.effect = 'None'      
        self.resizeMethod = 'BILINEAR'
        self.tags = []
        self.imageInfo = {'imageWidth':'',
                          'imageHeight':'',
                          'imageMegapixel':'',
                          'imageDateTime':'',
                          'imageCameraModel':''
                         }       
                
        self.readSettings()
        self.prepareTaskbar()
        # Create the timer Object                          
        self.myTimer = threading.Timer(0.100, self.on_myTimer)        
        self.myTimer.start() #Will call on_myTimer after 100 ms
        
    def on_myTimer(self):                
        
        try:
            self.myTimer.cancel()
        except:
            pass
        self.interval = self.components.spnInterval.value
        self.elapsedInterval += 1                
        if ((self.elapsedInterval / 10) >= self.interval):
            self.nextWallpaper()            
        info = str(len(self.imageList)) + ' images in the imagelist\n' + str(len(self.remainingImageList)) + ' images in the remaining imagelist\n' + str(self.interval - self.elapsedInterval / 10) + ' seconds remaining\n\n'
        if self.imageInfo['imageWidth'] != '':
            info += 'Wallpaper info:\n'
            info += '  * Resolution = ' + self.imageInfo['imageWidth'] + ' by ' + self.imageInfo['imageHeight'] + ' pixels (' + self.imageInfo['imageMegapixel'] + ' Megapixel)\n'        
            info += '  * Date/time picture taken: ' + self.imageInfo['imageDateTime'] + '\n'
            info += '  * Camera make and model: ' + self.imageInfo['imageCameraModel'] + '\n\n'
            info += 'From the one and only Dr. Love for his one and only Ms. Sensitive'
        
        self.components.txtInfo.text = info                    
        self.myTimer = threading.Timer(0.100, self.on_myTimer)
        self.myTimer.start() #Will call on_myTimer after 100 ms
        
        
    def on_cmdNext_mouseClick(self, event):
        self.nextWallpaper()
    
    def on_close(self,event):

        try:
            self.myTimer.cancel()
        except:
            pass
            
        del self.myTimer
        
        self.saveSettings()
        
        #Make sure that the desktop icons are enabled when exiting...
        self.hideIconsIndicator = '0'
        self.toggleDesktopIcons()
        try:
            del self.tbIcon
        except:
            pass
        event.Skip()   
        
    def onWindowMinimize(self, event):        
        self.Iconize(true)        
        self.Show(false)
    
    def on_menuImageListNew_select(self, event):
        self.makeImageList()
        
    def on_menuImagelistHighres_select(self, event):
        if self.menuBar.getChecked('menuImagelistHighres') == True:
            self.highresonly = '1'
        else:
            self.highresonly = '0'
            
    def on_menuOptionsRandom_select(self, event):
        if self.menuBar.getChecked('menuOptionsRandom') == True:
            self.randomIndicator = '1'
        else:
            self.randomIndicator = '0'
        
    def on_menuOptionsHideIcons_select(self, event):
        if self.menuBar.getChecked('menuOptionsHideIcons') == True:
            self.hideIconsIndicator = '1'
        else:
            self.hideIconsIndicator = '0'    
        self.toggleDesktopIcons()
        
    def on_menuOptionsAutoStart_select(self,event):
        if self.menuBar.getChecked('menuOptionsAutoStart') == True:
            self.autoStart = '1'
        else:
            self.autoStart = '0'        
        
    def on_menuEffectsNone_select(self,event):
        self.effect = 'None'
        self.menuBar.setChecked('menuEffectsNone',True)      
        self.menuBar.setChecked('menuEffectsSunset',False)      
        self.menuBar.setChecked('menuEffectsSepia',False)      
        self.menuBar.setChecked('menuEffectsNegative',False)      
        self.menuBar.setChecked('menuEffectsGreyscale',False)      
        
    def on_menuEffectsSunset_select(self,event):
        self.effect = 'sunset'
        self.menuBar.setChecked('menuEffectsSunset',True)      
        self.menuBar.setChecked('menuEffectsNone',False)      
        self.menuBar.setChecked('menuEffectsSepia',False)      
        self.menuBar.setChecked('menuEffectsNegative',False)      
        self.menuBar.setChecked('menuEffectsGreyscale',False)      
    
    def on_menuEffectsSepia_select(self,event):
        self.effect = 'sepia'
        self.menuBar.setChecked('menuEffectsSepia',True)      
        self.menuBar.setChecked('menuEffectsSunset',False)      
        self.menuBar.setChecked('menuEffectsNone',False)      
        self.menuBar.setChecked('menuEffectsNegative',False)      
        self.menuBar.setChecked('menuEffectsGreyscale',False)      
        
    def on_menuEffectsNegative_select(self,event):
        self.effect = 'negative'
        self.menuBar.setChecked('menuEffectsNegative',True)      
        self.menuBar.setChecked('menuEffectsSunset',False)      
        self.menuBar.setChecked('menuEffectsSepia',False)      
        self.menuBar.setChecked('menuEffectsNone',False)      
        self.menuBar.setChecked('menuEffectsGreyscale',False)      
        
    def on_menuEffectsGreyscale_select(self,event):
        self.effect = 'greyscale'
        self.menuBar.setChecked('menuEffectsGreyscale',True)      
        self.menuBar.setChecked('menuEffectsSunset',False)      
        self.menuBar.setChecked('menuEffectsSepia',False)      
        self.menuBar.setChecked('menuEffectsNegative',False)      
        self.menuBar.setChecked('menuEffectsNone',False)
        
    def on_menuPerformanceNEAREST_select(self,event):   
        self.resizeMethod = 'NEAREST'        
        self.menuBar.setChecked('menuPerformanceNEAREST',True)          
        self.menuBar.setChecked('menuPerformanceBILINEAR',False)          
        self.menuBar.setChecked('menuPerformanceBICUBIC',False)          
        self.menuBar.setChecked('menuPerformanceANTIALIAS',False)          
        
    def on_menuPerformanceBILINEAR_select(self,event):   
        self.resizeMethod = 'BILINEAR'        
        self.menuBar.setChecked('menuPerformanceNEAREST',False)          
        self.menuBar.setChecked('menuPerformanceBILINEAR',True)          
        self.menuBar.setChecked('menuPerformanceBICUBIC',False)          
        self.menuBar.setChecked('menuPerformanceANTIALIAS',False)          
        
    def on_menuPerformanceBICUBIC_select(self,event):   
        self.resizeMethod = 'BICUBIC'        
        self.menuBar.setChecked('menuPerformanceNEAREST',False)          
        self.menuBar.setChecked('menuPerformanceBILINEAR',False)          
        self.menuBar.setChecked('menuPerformanceBICUBIC',True)          
        self.menuBar.setChecked('menuPerformanceANTIALIAS',False)          
        
    def on_menuPerformanceANTIALIAS_select(self,event):   
        self.resizeMethod = 'ANTIALIAS'        
        self.menuBar.setChecked('menuPerformanceNEAREST',False)          
        self.menuBar.setChecked('menuPerformanceBILINEAR',False)          
        self.menuBar.setChecked('menuPerformanceBICUBIC',False)          
        self.menuBar.setChecked('menuPerformanceANTIALIAS',True)          
    
    #----------------------------------------------#
    #Functions to manage the taskbar and its events#
    #----------------------------------------------#
    
    def prepareTaskbar(self):
        self.TBMENU_RESTORE = 1000
        self.TBMENU_MINIMIZE = 1001
        self.TBMENU_EXIT = 1002
        self.TBMENU_NEXT = 1003
        self.TBMENU_HIDEICONS = 1004
        self.TBMENU_SHOWICONS = 1005
        
        # handler for main window minimization                
        EVT_ICONIZE(self, self.onWindowMinimize)
        
        #make the TaskBar icon
        self.tbIcon = wxTaskBarIcon()
        icon = wxIcon('juggler.ico', wxBITMAP_TYPE_ICO)
        self.tbIcon.SetIcon(icon, "Switch+")
        
        # handlers for taskbar actions     
        
        wx.EVT_TASKBAR_LEFT_UP(self.tbIcon, self.taskBarEvent_showTaskBarMenu)
        wx.EVT_TASKBAR_RIGHT_UP(self.tbIcon, self.taskBarEvent_showTaskBarMenu)
        wx.EVT_MENU(self.tbIcon, self.TBMENU_RESTORE,self.taskBarEvent_restoreWindow)
        wx.EVT_MENU(self.tbIcon, self.TBMENU_MINIMIZE,self.taskBarEvent_minimizeWindow)
        wx.EVT_MENU(self.tbIcon, self.TBMENU_EXIT, self.taskBarEvent_OnEXIT)                        
        wx.EVT_MENU(self.tbIcon, self.TBMENU_NEXT, self.taskBarEvent_nextWallpaper)
        wx.EVT_MENU(self.tbIcon, self.TBMENU_HIDEICONS,self.taskBarEvent_toggleIcons)
        wx.EVT_MENU(self.tbIcon, self.TBMENU_SHOWICONS,self.taskBarEvent_toggleIcons)
        
    def taskBarEvent_showTaskBarMenu(self, event):        
        menu = wxMenu()        
        
        menu.Append(self.TBMENU_NEXT, '&Next wallpaper')    
        
        if self.hideIconsIndicator == '0':
            menu.Append(self.TBMENU_HIDEICONS, '&Hide desktop icons')
        else:
            menu.Append(self.TBMENU_SHOWICONS, '&Show desktop icons')
            
        menu.AppendSeparator()
        
        if self.IsIconized():
            menu.Append(self.TBMENU_RESTORE, '&Restore Switch+')       
        else:
            menu.Append(self.TBMENU_MINIMIZE, '&Minimize Switch+')        
            
        menu.AppendSeparator()
        
        menu.Append(self.TBMENU_EXIT, '&Exit')    
        self.tbIcon.PopupMenu(menu)
        menu.Destroy()
        wxGetApp().ProcessIdle()
        
    def taskBarEvent_toggleIcons(self, event):        
        if self.hideIconsIndicator == '1':
            self.hideIconsIndicator = '0'
            self.menuBar.setChecked('menuOptionsHideIcons',False)
        else:
            self.hideIconsIndicator = '1'
            self.menuBar.setChecked('menuOptionsHideIcons',True)
            
        self.toggleDesktopIcons()
    
    def taskBarEvent_restoreWindow(self, event):
        self.Show(true)
        self.Iconize(false)        
        
    def taskBarEvent_minimizeWindow(self, event):
        self.Iconize(true)        
        self.Show(false)
        
    def taskBarEvent_OnEXIT(self, event):        
        self.Close()       
        
    def taskBarEvent_nextWallpaper(self, event):
        self.nextWallpaper() 

        
    #-----------------------#
    #The workhorse functions#
    #-----------------------#
            
    def makeImageList(self):
        try:
            self.myTimer.cancel()
        except:
            pass
        
        self.screenWidth = win32api.GetSystemMetrics(0)
        self.screenHeight = win32api.GetSystemMetrics(1)
        
        map = dialog.directoryDialog(self, 'Select your wallpaper folder', 'a')
        if map['accepted']:                        
            
            map = map['path']                        
            self.imageList = []              
            
            hourGlass = wxBusyCursor()
            
            os.path.walk(map,self.findJPG,None)
            
            self.remainingImageList = []
            for i in self.imageList:
                self.remainingImageList.append(i)            
                    
            imageListFile = open(os.path.join(os.getcwd(),'imagelist.pco'),'w')
            for i in self.imageList:                
                imageListFile.write(i + '\n')
            imageListFile.close()
            del imageListFile            
            
            if len(self.imageList) == 0: #No valid images were found
                del hourGlass
                result = dialog.messageDialog(self, 'The folder you have chosen and its subfolders do not contain valid wallpapers...\nTry another folder or deselect the "Only highres images" option from the menu', 'No valid wallpapers found', dialog.ICON_INFORMATION, dialog.BUTTON_OK)
                self.makeImageList()
            
            if len(self.imageList) != 0:
                self.nextWallpaper()
                
        else:
            if len(self.imageList) == 0:
                result = dialog.messageDialog(self, 'Switch+ cannot work without an imagelist...\nSo I quit', 'I quit!', dialog.ICON_INFORMATION, dialog.BUTTON_OK)
                self.Close()
                return -1            
                                        
        del hourGlass
        self.myTimer = threading.Timer(0.100, self.on_myTimer)        
        self.myTimer.start() #Will call on_myTimer after 100 ms
        return 0
    
    def nextWallpaper(self): 
                        
        SPI_SETDESKWALLPAPER = 20
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDWININICHANGE = 0x02
        
        hourGlass = wxBusyCursor()
        
        try:
            self.myTimer.cancel()
        except:
            pass
        
        self.components.cmdNext.enabled = 0
        self.elapsedInterval = 0
        screenWidth = win32api.GetSystemMetrics(0)
        screenHeight = win32api.GetSystemMetrics(1)
                
        if len(self.remainingImageList) == 0:
            #Another round!            
            self.remainingImageList = []
            for i in self.imageList:
                self.remainingImageList.append(i)
                    
        if self.randomIndicator == '1':                    
            wpIndex = self.randomInteger(len(self.remainingImageList)-1)
        else:
            wpIndex = 0
                
        if os.path.exists(self.remainingImageList[wpIndex]):
            
            im = open(self.remainingImageList[wpIndex],'rb')        
            try:
                self.tags=EXIF.process_file(im)        
            except:
                self.imageInfo['imageDateTime'] = 'Info not available'
                self.imageInfo['imageCameraModel'] = 'Info not available'
            else:
                try:
                    datetime = str(self.tags['EXIF DateTimeDigitized'])
                    yyyy = int(datetime[:4])
                    MM = int(datetime[5:7])
                    dd = int(datetime[8:10])
                    hh = int(datetime[11:13])
                    mm = int(datetime[14:16])
                    ss = int(datetime[17:])
                    daynumber = calendar.weekday(yyyy,MM,dd)
                    datetime = (yyyy,MM,dd,hh,mm,ss,daynumber,0,0) 
                    
                    self.imageInfo['imageDateTime'] = time.strftime('%A %d %B %Y, %H:%M',datetime)
                except:
                    self.imageInfo['imageDateTime'] = 'Info not available'
                
                try:
                    self.imageInfo['imageCameraModel'] = str(self.tags['Image Make']) + ' - ' + str(self.tags['Image Model'])
                except:
                    self.imageInfo['imageCameraModel'] = 'Info not available'
            
            del im
            
            im = Image.open(self.remainingImageList[wpIndex])
            imWidth, imHeight = im.size
            self.imageInfo['imageWidth'] = str(imWidth)
            self.imageInfo['imageHeight'] = str(imHeight)
            self.imageInfo['imageMegapixel'] = str(imWidth * imHeight / 1000000.0)[:4]
           
            #Resize the image using the chosen method
            
            if self.resizeMethod == 'NEAREST':
                im.thumbnail((screenWidth, screenHeight),Image.NEAREST)
            elif self.resizeMethod == 'BILINEAR':
                im.thumbnail((screenWidth, screenHeight),Image.BILINEAR)
            elif self.resizeMethod == 'BICUBIC':
                im.thumbnail((screenWidth, screenHeight),Image.BICUBIC)
            elif self.resizeMethod == 'ANTIALIAS':
                im.thumbnail((screenWidth, screenHeight),Image.ANTIALIAS)            
            
            im.save(os.path.join(os.getcwd(),'wallpaper.bmp'))
            del im        
            del self.remainingImageList[wpIndex]        
            
            imagefilters.applyEffect(os.path.join(os.getcwd(),'wallpaper.bmp'),self.effect)
            
            #Set the registry keys so that the wallpaper will not be tiled (but centered) and not be stretched
            
            try:          
                magicKey = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,'Control Panel\\Desktop',0,win32con.KEY_ALL_ACCESS)
                win32api.RegSetValueEx(magicKey, 'WallpaperStyle', '0', win32con.REG_SZ, '0')
                win32api.RegSetValueEx(magicKey, 'TileWallpaper', '0', win32con.REG_SZ, '0')
                win32api.RegFlushKey(magicKey)
                win32api.RegCloseKey(magicKey)
                del magicKey
            except: #Can not write to the registry
                pass
            
            ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, os.path.join(os.getcwd(),'wallpaper.bmp'), SPIF_UPDATEINIFILE or SPIF_SENDWININICHANGE) 
            
            self.myTimer = threading.Timer(0.100, self.on_myTimer)
            self.myTimer.start() #Will call on_myTimer after 100 ms
            
            self.components.cmdNext.enabled = 1
            del hourGlass
            
            #Save the remaining imagelist
            #I put this here in stead of in the 'on exit' for stability reasons
            remainingImageListFile = open(os.path.join(os.getcwd(),'rimagelist.pco'),'w')
            for i in self.remainingImageList:
                remainingImageListFile.write(i + '\n')
            remainingImageListFile.close()
            del remainingImageListFile
        
        else: #The file that had to be displayed has been renamed, moved or removed => create new imagelist because it is corrupted
            result = dialog.messageDialog(self, 'An image has been renamed, moved or removed...\nThis caused your imagelist to expire,\nso you have to build a new one.', 'Image renamed, moved or removed', dialog.ICON_INFORMATION, dialog.BUTTON_OK)
            self.imageList = []
            self.remainingImageList = []
            self.makeImageList()            
            
    def readSettings(self):
        if os.path.exists(os.path.join(os.getcwd(),'Switch+.ini')):
            settings = ConfigParser.ConfigParser()
            settings.read(os.path.join(os.getcwd(),'Switch+.ini'))
            self.interval = int(settings.get('timers','interval'))
            self.elapsedInterval = int(settings.get('timers','elapsedInterval'))            
            self.randomIndicator = settings.get('options','randomIndicator')
            self.autoStart = settings.get('options','autoStart')
            self.hideIconsIndicator = settings.get('options','hideIconsIndicator')        
            self.effect = settings.get('options','effect')
            self.resizeMethod = settings.get('options','resizeMethod')
            self.highresonly = settings.get('options','highresonly')                    
            self.imageInfo['imageWidth'] = settings.get('current','width')
            self.imageInfo['imageHeight'] = settings.get('current','height')
            self.imageInfo['imageMegapixel'] = settings.get('current','megapixel')
            self.imageInfo['imageDateTime'] = settings.get('current','datetime')
            self.imageInfo['imageCameraModel'] = settings.get('current','cameramodel')            
            del settings        
            
        self.components.spnInterval.value = self.interval
        if self.randomIndicator == '1':
            self.menuBar.setChecked('menuOptionsRandom')            
        if self.hideIconsIndicator == '1':
            self.menuBar.setChecked('menuOptionsHideIcons')            
        if self.autoStart == '1':
            self.menuBar.setChecked('menuOptionsAutoStart')
        if self.highresonly == '1':
            self.menuBar.setChecked('menuImagelistHighres')            
        
        
        if self.effect == 'None':
            self.menuBar.setChecked('menuEffectsNone',True)      
        elif self.effect == 'sunset':
            self.menuBar.setChecked('menuEffectsSunset',True)      
        elif self.effect == 'sepia':
            self.menuBar.setChecked('menuEffectsSepia',True)      
        elif self.effect == 'negative':
            self.menuBar.setChecked('menuEffectsNegative',True)      
        elif self.effect == 'greyscale':
            self.menuBar.setChecked('menuEffectsGreyscale',True)                      
        
        if self.resizeMethod == "NEAREST":
            self.menuBar.setChecked('menuPerformanceNEAREST',True)
        elif self.resizeMethod == "BILINEAR":
            self.menuBar.setChecked('menuPerformanceBILINEAR',True)
        elif self.resizeMethod == "BICUBIC":
            self.menuBar.setChecked('menuPerformanceBICUBIC',True)
        elif self.resizeMethod == "ANTIALIAS":
            self.menuBar.setChecked('menuPerformanceANTIALIAS',True)
            
        self.toggleDesktopIcons()
        
        if os.path.exists(os.path.join(os.getcwd(),'imagelist.pco')):                    
            imageListFile = open(os.path.join(os.getcwd(),'imagelist.pco'),'r')
            wallpaper = 'dummy'
            while wallpaper != '':
                wallpaper = string.replace(imageListFile.readline(),'\n','')            
                if wallpaper != '':
                    self.imageList.append(wallpaper)
            imageListFile.close()        
                
            rwallpaper = 'dummy'
            
            if os.path.exists(os.path.join(os.getcwd(),'rimagelist.pco')):    
                remainingImageListFile = open(os.path.join(os.getcwd(),'rimagelist.pco'),'r')
                while rwallpaper != '':
                    rwallpaper = string.replace(remainingImageListFile.readline(),'\n','')            
                    if rwallpaper != '':
                        self.remainingImageList.append(rwallpaper)
                remainingImageListFile.close()
            
        missingImages = []
        cleanedImagelist = []
        index_adjust = 0
        
        #Remove non-existant images from the imagelist                
        for i in range(len(self.imageList)):             
            if not os.path.exists(self.imageList[i]):
                missingImages.append(i)
        for i in missingImages:
            del self.imageList[i - index_adjust]
            index_adjust += 1
            
        missingImages = []
        cleanedImagelist = []
        index_adjust = 0
                
        #Remove non-existant images from the remaining imagelist                
        for i in range(len(self.remainingImageList)):             
            if not os.path.exists(self.remainingImageList[i]):
                missingImages.append(i)
        for i in missingImages:
            del self.remainingImageList[i - index_adjust]
            index_adjust += 1            
                
        if len(self.imageList) <> 0:
            self.Iconize(true)        
            self.Show(false)
        else:
            result = dialog.messageDialog(self, 'You have to build a new imagelist...\nSelect the folder containg your images.', 'Make a new imagelist', dialog.ICON_INFORMATION, dialog.BUTTON_OK)
            result = self.makeImageList()            
        
    def saveSettings(self):            
        
        try:
            self.myTimer.cancel()
        except:
            pass
        self.components.cmdNext.enabled = 0
        #Write the Switch+.ini File
        settings = ConfigParser.ConfigParser()
        settings.add_section('timers')
        settings.set('timers','interval',self.interval)
        settings.set('timers','elapsedInterval',self.elapsedInterval)
        settings.add_section('options')
        settings.set('options','hideIconsIndicator',self.hideIconsIndicator)
        settings.set('options','randomIndicator',self.randomIndicator)
        settings.set('options','highresonly',self.highresonly)        
        settings.set('options','effect',self.effect)
        settings.set('options','resizeMethod',self.resizeMethod)
        settings.set('options','autoStart',self.autoStart)
        settings.add_section('current')
        settings.set('current','width',self.imageInfo['imageWidth'])
        settings.set('current','height',self.imageInfo['imageHeight'])
        settings.set('current','megapixel',self.imageInfo['imageMegapixel'])
        settings.set('current','datetime',self.imageInfo['imageDateTime'])
        settings.set('current','cameramodel',self.imageInfo['imageCameraModel'])
        iniFile = open(os.path.join(os.getcwd(),'Switch+.ini'),'w')
        settings.write(iniFile)
        iniFile.close()
        del iniFile
        
        #Save the imagelist
        imageListFile = open(os.path.join(os.getcwd(),'imagelist.pco'),'w')
        for i in self.imageList:                
            imageListFile.write(i + '\n')
        imageListFile.close()
        del imageListFile
        
        #Set the registry to startUp automatically (or not to start automatically)
        
        
        exec_path = os.path.join(os.getcwd(),'SwitchPlus.exe')
        
        if self.autoStart == '1':        
            try:          
                try:
                    startupKey = win32api.RegCreateKey(win32con.HKEY_CURRENT_USER,'Software\Microsoft\Windows\CurrentVersion\Run')
                except:
                    pass
                else:
                    del startupKey
                    
                startupKey = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,'Software\Microsoft\Windows\CurrentVersion\Run',0,win32con.KEY_ALL_ACCESS)            
                win32api.RegSetValueEx(startupKey, 'Switch+', '0', win32con.REG_SZ, exec_path)            
                win32api.RegFlushKey(startupKey)
                win32api.RegCloseKey(startupKey)
                del startupKey
            except:                
                pass #Can not set the autostart option, no rights to write to registry
        
        else:
            try:
                startupKey = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,'Software\Microsoft\Windows\CurrentVersion\Run',0,win32con.KEY_ALL_ACCESS)            
                win32api.RegDeleteValue(startupKey, 'Switch+')
                win32api.RegFlushKey(startupKey)
                win32api.RegCloseKey(startupKey)
            except:                
                pass
        
        #I put this in the Nextwallpaper function
        ##Save the remaining imagelist
        #remainingImageListFile = open(os.path.join(os.getcwd(),'rimagelist.pco'),'w')
        #for i in self.remainingImageList:
        #    remainingImageListFile.write(i + '\n')
        #remainingImageListFile.close()
        #del remainingImageListFile
        
    
    def randomInteger(self, maximum):
        return random.randint(0,maximum)
    
    def findJPG(self,arg,dirname,names):
        for name in names:            
            if string.upper(name).endswith('.JPG'):
                try:
                    im = Image.open(os.path.join(dirname, name))
                    imWidth, imHeight = im.size
                except:
                    pass #Not a valid JPEG => Don't add it to the list
                else:
                    del im
                    if self.highresonly == '1':
                        if ((imWidth < self.screenWidth) and (imHeight < self.screenHeight)):
                            pass #Do not add the JPG to the imagelist, it is too small!
                        else:
                            self.imageList.append(os.path.join(dirname, name))
                    else:                    
                        self.imageList.append(os.path.join(dirname, name))                           
                        
    def toggleDesktopIcons(self): 
        progman = win32gui.FindWindow('Progman',None)        
        if self.hideIconsIndicator == '1':
            tmp = win32gui.ShowWindow(progman,0)
        else:
            tmp = win32gui.ShowWindow(progman,1)

if __name__ == '__main__':
    app = model.PythonCardApp(SwitchPlus)
    app.MainLoop()
