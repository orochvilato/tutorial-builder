from threading import Timer,Thread
import time
#eventTypes = 'mousePressLeft', 'mouseReleaseLeft'
#             'mousePressRight','mouseReleaseRight'
#             'mousePressMiddle','mouseReleaseMiddle'
#             'mouseWheelUp','mouseWheelDown','mouseMove','mouseSlide'
class KMEvents:
    def __init__(self):
        import platform
        if platform.system() in ['Linux']:
            from xlib import XlibKMEvents
            self.platformKMEvt = XlibKMEvents
        elif platform.system() in ['Windows']:
            from windows import WindowsKMEvents
            self.platformKMEvt = WindowsKMEvents
        self.buttonLast = dict()
        self.buttonHold = dict()
        self.bindings = {}
        self.capture = False
        self.toggleKey = 'keyPressF8'
    def setToggleKey(self,tkey):
        self.toggleKey = tkey
    def toggleCapture(self):
        self.capture = not self.capture        
    def getMouseXY(self):
        return self.kme.getMouseXY()
    def getActiveWindowGeometry(self):
        return self.kme.activeWindow
    def start(self):
        self.kme = self.platformKMEvt(self.eventCallback)
        self.kme.start()
    def end(self):
        self.kme.stop()
    def eventCallback(self,event):
        now = time.time()
        if event.type == self.toggleKey:
            self.toggleCapture()
            return
        if not self.capture:
            return

       
        if 'mousePress' in event.type:
            self.buttonHold[event.button] = True
            if event.type in self.buttonLast.keys() and (now-self.buttonLast[event.type].time)<0.3:
                self.buttonLast[event.type].count += 1
                event = self.buttonLast[event.type]      
            else:
                self.buttonLast[event.type] = event
            
        elif 'mouseRelease' in event.type:
            self.buttonHold[event.button] = False
            
        elif 'mouseMove' in event.type:
            
            if any(self.buttonHold.values()) and (now-max([b.time for b in self.buttonLast.values()]))>0.3:
                event.type = "mouseSlide"

        self.executeCallbacks(event)
        
    def bindCallback(self,types,callback):
        if not isinstance(types,tuple):
            types = (types)
        self.bindings[types] = self.bindings.get(types,[]) + [callback]
                      
    def executeCallbacks(self,event):
        for binding,callbacks in self.bindings.iteritems():
            if event.type in binding:
                for callback in callbacks:
                    Thread(target=callback,args=(event,)).start()
                    
        
 

