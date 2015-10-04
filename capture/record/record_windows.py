
# key : actions:'press','release',keycode
# mouse : actions:'press','release','move'
#         button: 1,2,3
#
import time
import logging

from events import MouseEvent,KeyEvent

from threading import Timer,Thread
import pythoncom, pyHook
from win32gui import GetWindowRect, GetForegroundWindow, GetWindowText, IsWindow


class WindowsKMEvents(Thread):
    def __init__(self,eventCallback):
        Thread.__init__(self)
        self.equivtable = {'mouse move':'mouseMove','mouse left down':'mousePressLeft',
                  'mouse left up':'mouseReleaseLeft', 'mouse right down':'mousePressRight',
                  'mouse right up':'mouseReleaseRight', 'mouse middle down':'mousePressMiddle', 
                  'mouse middle up':'mouseReleaseMiddle'} 
        self.end = False
        self.eventCallback = eventCallback
  
        # Enable the context; this only returns after a call to record_disable_context,
        # while calling the callback function in the meantime
        self.activeWindow = None
        self.mousex = -1
        self.mousey = -1
    
    def run(self):
        self.hm = pyHook.HookManager()
        # watch for all mouse events
        self.hm.MouseAll = self._OnMouseEvent
        # set the hook
        self.hm.HookMouse()
        # watch for all mouse events
        self.hm.KeyDown = self._OnKeyboardEvent
        # set the hookl
        self.hm.HookKeyboard()

        self.activeWindow = self.getActiveWindowGeometry()
        while not self.end:
            pythoncom.PumpWaitingMessages()
        
    def stop(self):
        self.end = True

    def getMouseXY(self):
        return (self.mousex, self.mousey)    
    def getActiveWindowGeometry(self):
       
        window = GetForegroundWindow()
        if IsWindow(window):
            geo = GetWindowRect(window)
            name = GetWindowText(window)
            self.activeWindow = dict(name="none",x=geo[0],y=geo[1],w=geo[2]-geo[0],h=geo[3]-geo[1])
        return self.activeWindow
    
    def _OnMouseEvent(self,event):
        self.mousex = event.Position[0]
        self.mousey = event.Position[1]
        eventType = self.equivtable[event.MessageName]
        if 'mousePress' in eventType:
            button = eventType[10:]
        elif 'mouseRelease':
            button = eventType[12:]
        else:
            button = None
        
        e = MouseEvent(type=eventType,x=event.Position[0],y=event.Position[1],button=button,count=1,activeWindow=self.getActiveWindowGeometry())
        if e:
            self.eventCallback(e)
        return True
        
    def _OnKeyboardEvent(self,event):
        eventType = 'keyPress' + event.Key
        e = KeyEvent(type=eventType,x=self.mousex,y=self.mousey,activeWindow=self.getActiveWindowGeometry())
        self.eventCallback(e)
        return True