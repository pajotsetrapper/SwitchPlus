#!/usr/bin/python

"""
__version__ = "$Revision: 0.0.1 $"
__date__ = "$Date: 2004/11/30 21:30:00 $"

Switch+ 0.0.1 by Pieter Coppens - a tool to change your wallpaper periodically
Copyright (C) 2004 Pieter Coppens
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

import Image

def applyEffect(filename,effect):
    if effect == 'sepia':
        convertToSepia(filename)
    elif effect == 'sunset':
        convertToSunset(filename)
    elif effect == 'negative':
        convertToNegative(filename)
    elif effect == 'greyscale':
        convertToGreyscale(filename)

def sepiaCalculateHighlightsRedValue(i):
    retval = i * 1.08
    if retval > 255:
        retval = 255
    return retval

def convertToGreyscale(filename):
    try:
        source = Image.open(filename).convert('L') #Bestand openen en naar grijswaarden converteren
    except:
        pass
    else:
        R, G, B = 0, 1, 2        
        
        RGBchannels = source.split() # Splitsen in R,G & B component (G&B zullen leeg zijn)
        del source
        greyscale = Image.merge("RGB", (RGBchannels[R],RGBchannels[R],RGBchannels[R])) # G & B invullen
        del RGBchannels
        greyscale.save(filename)      
        del greyscale
    

def convertToSepia(filename):
    try:
        source = Image.open(filename).convert('L') #Bestand openen en naar grijswaarden converteren
    except:
        pass
    else:
        R, G, B = 0, 1, 2        
        
        RGBchannels = source.split() # Splitsen in R,G & B component (G&B zullen leeg zijn)
        del source
        greyscale = Image.merge("RGB", (RGBchannels[R],RGBchannels[R],RGBchannels[R])) # G & B invullen
        del RGBchannels
        
        greyscaleRGB = greyscale.split()
        
        #Schaduwen converteren
        
        mask = greyscaleRGB[R].point(lambda i: (i < 63) and 255)
        Rout = greyscaleRGB[R].point(lambda i: i * 1.1)
        Bout = greyscaleRGB[R].point(lambda i: i * 0.9)
        greyscaleRGB[R].paste(Rout, None, mask)
        greyscaleRGB[B].paste(Bout, None, mask)
        del Rout
        del Bout
        
        #Middentonen converteren
        
        mask = greyscaleRGB[R].point(lambda i: ((i > 62) and (i < 192)) and 255)
        Rout = greyscaleRGB[R].point(lambda i: i * 1.15)
        Bout = greyscaleRGB[R].point(lambda i: i * 0.85)
        greyscaleRGB[R].paste(Rout, None, mask)
        greyscaleRGB[B].paste(Bout, None, mask)        
        del Rout
        del Bout
        
        #Highlights converteren
        
        mask = greyscaleRGB[R].point(lambda i: (i > 191) and 255)
        Rout = greyscaleRGB[R].point(sepiaCalculateHighlightsRedValue)        
        Bout = greyscaleRGB[R].point(lambda i: i * 0.93)
        greyscaleRGB[R].paste(Rout, None, mask)
        greyscaleRGB[B].paste(Bout, None, mask)
        del Rout
        del Bout
        
        result = Image.merge("RGB", greyscaleRGB)
        del greyscaleRGB
        
        result.save(filename)      
        del result  
        
def convertToSunset(filename):    
    try:
        source = Image.open(filename)
    except:
        pass
    else:
        R, G, B = 0, 1, 2
        RGBchannels = source.split()        
        del source
        Gout = RGBchannels[G].point(lambda i: i * 0.7)
        Bout = RGBchannels[B].point(lambda i: i * 0.7)
        RGBchannels[G].paste(Gout, None)
        RGBchannels[B].paste(Bout, None)
        result = Image.merge("RGB", RGBchannels)
        del RGBchannels
        del Gout
        del Bout
        
        result.save(filename)
        del result
        
def convertToNegative(filename):
    try:
        source = Image.open(filename)
    except:
        pass
    else:
        R, G, B = 0, 1, 2
        RGBchannels = source.split()
        Rout = RGBchannels[R].point(lambda i: 255 - i)
        Gout = RGBchannels[G].point(lambda i: 255 - i)
        Bout = RGBchannels[B].point(lambda i: 255 - i)
    
        RGBchannels[R].paste(Rout, None)
        RGBchannels[G].paste(Gout, None)
        RGBchannels[B].paste(Bout, None)
        result = Image.merge("RGB", RGBchannels)
        del RGBchannels
        del Rout
        del Gout
        del Bout
        
        result.save(filename)
        del result