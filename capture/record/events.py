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
        self.keycode = keycode
        
class KMEventsBase:
    def __init__(self):
        self.bindings = {'key':{},'mouse':{}}
        self.lastButton = None
        self.lastEvent = None
        self.lastTime = time.time()
        self.holdButton = None
        self.timer = None
        self.x = None
        self.y = None
    def getMouseXY(self):
        return (self.x,self.y)
        
    def setMouseXY(self,x,y):
        self.x = x
        self.y = y
    
    def bindMouse(self,types,callback):
        #eventTypes = 'mouseLeftPress', 'mouseLeftRelease','mouseLeftSlide',
        #             'mouseRightPress','mouseRightRelease','mouseRightSlide',
        #             'mouseMiddlePress','mouseMiddleRelease','mouseMiddleSlide',
        #             'mouseWheelUp','mouseWheelDown','mouseMove'
        for type in types:
            self.bindings['mouse'][type] = self.bindings.get(type,[]) + [callback]

    def bindKey(self,types,keycode,callback):
        for type in types:
            self.bindings['key'][(type,keycode)] = self.bindings.get((type,keycode),[]) + [callback]

    def executeMouseCallbacks(self,event):
       
        event.activeWindow = self.getActiveWindowGeometry()
        if event.type in self.bindings['mouse'].keys():
             # in a thread ?
            for callback in self.bindings['mouse'][event.type]:
                callback(event)
        if 'all' in self.bindings['mouse'].keys():
            for callback in self.bindings['mouse']['all']:
                callback(event)
