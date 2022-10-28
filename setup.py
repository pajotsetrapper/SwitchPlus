# setup.py

from distutils.core import setup
import py2exe

setup( name = "Switch+",
       version = "0.0.2",
       description="Switch+ wallpaper management tool",       
       author="Pieter Coppens",
       author_email="pieter_coppens@yahoo.com",
       url="http://www.geocities.com/pieter_coppens",      
       
       windows = [ 
        { 
            "script": "SwitchPlus.py", 
            "icon_resources": [(1, "juggler.ico")] 
        } 
       ],
       
       data_files = [
                     (".",["SwitchPlus.rsrc.py", "juggler.ico", "Switch+.ini"])
                    ]
       )
