import time
import logging

class Event:
    def __init__(self,type=None,x=None,y=None,activeWindow=None):
        self.type = type
        self.x = x
        self.y = y
        self.time = time.time()
        self.activeWindow = activeWindow

class MouseEvent(Event):
    def __init__(self,type=None,x=None,y=None,button=None,count=None,activeWindow=None):
        Event.__init__(self,type,x,y,activeWindow)
        self.button = button
        self.count = count

class KeyEvent(Event):
    def __init__(self,type=None,x=None,y=None,keycode=None,activeWindow=None):
        Event.__init__(self,type,x,y,activeWindow)
       

