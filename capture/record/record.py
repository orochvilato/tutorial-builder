import os
import sys
import time
import ImageChops
import math, operator

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from events import MouseEvent,KeyEvent,Event
import pyscreenshot as ImageGrab
import datetime
# Enable regular snapshots
import time
from threading import Timer
import json

def cb(event):
    print event.type,event.count
          
class Snapshot():
    def __init__(self,title="test",focus=True):
        self.snapOn = False
        self.focus = focus
        self.lastEvent = None
        self.lock = False
        self.parameters = dict(autodelay=0.5)
        self.init(title)
        self.km = KMEvents()
        self.km.bindCallback(('mousePressLeft', 'mouseReleaseLeft','mouseSlide',
                           'mousePressRight','mouseReleaseRight',
                           'mousePressMiddle','mouseReleaseMiddle',
                           'mouseWheelUp','mouseWheelDown'), self.takeSnap)
        #self.km.start()

    def init(self,title):
        self.i = 0
        self.seq = 0
        self.starttime = None
        self.timeline = []
        self.scenario = []
        self.lastCall = time.time()
        self.title = title
    def status(self):
        return {'n':len(self.timeline),'on':self.snapOn}
        
    def start(self):
        self.snapOn = True
        self.km.start()
        Timer(self.parameters['autodelay'],self.takeTimedSnap,()).start()
        self.seq += 1
        if not self.starttime:
            self.starttime = time.time()
        
    def takeTimedSnap(self):
        x,y = self.km.getMouseXY()
        self.takeSnap(Event(type="timed",x=x,y=y,activeWindow=self.km.getActiveWindowGeometry()),force=True)
        if self.snapOn:
            Timer(self.parameters['autodelay'],self.takeTimedSnap,()).start()
    
    def stop(self):
        self.snapOn = False
        self.km.end()
        
    def toggle(self,event=None):
        if self.snapOn:
            self.stop()
        else:
            self.start()
    

    def takeSnap(self,event=None,force=False):
        if not self.km.capture:
            return
        now = time.time()
        if not self.lock:
            self.lock = True
            self.img = ImageGrab.grab()
            self.lock = False
        while self.lock:
            pass
        self.timeline.append(dict(timestamp=now,event=event,image=self.img,active=event.activeWindow))
        
        
    
    def saveElement(self,tlelt):
        self.i += 1
        iname = 'im-%03d-%d.png'% (self.i,self.seq)
        inameactive = 'im-%03d-active.png'% (self.i)
        #im = self.timeline[i]['image']
        #event = self.timeline[i]['event']
        #font = ImageFont.truetype("arial.ttf", 25)

        #draw = ImageDraw.Draw(im)
        #draw.ellipse((event.x-5, event.y-5, event.x+5, event.y+5), fill=(255,255,255))
        #draw.text((event.x,event.y),event.type,(0,0,0),font=font)

        tlelt['iname'] = iname
        tlelt['inameactive'] = inameactive
            
        
    def saveTimeline(self):
        last = None
        for i,elt in enumerate(self.timeline):
            current = elt['image']
            print i,elt['event'].type
            if self.focus:
                active=elt['active']
                
                current = current.crop((active['x'],active['y'],active['x']+active['w'],active['y']+active['h']))
            event = elt['event']
            if last:
                diff = self.diffImage(current,lastimage)
            else:
                diff = 100
            
            if not last or (diff>0.5) or (last['active'] != active) or ('Press' in elt['event'].type) :
                    self.saveElement(elt)
                    elt['saved'] = True
            else:
                elt['iname'] = last['iname']
                elt['inameactive'] = last['inameactive']
            
            last = elt
            lastimage = current
        imagesnames = []
        for i,tlelt in enumerate(self.timeline):

            
            if (tlelt['event'].type!='timed') or (i+1<len(self.timeline) and self.timeline[i+1]['event'].type!='timed'):
                if not tlelt['iname'] in imagesnames:
                    active = tlelt['active']        
                    crop = tlelt['image'].crop((active['x'],active['y'],active['x']+active['w'],active['y']+active['h']))
                    #crop.save(inameactive,'PNG')
                    tlelt['image'].save(tlelt['iname'],'PNG')            

                self.scenario.append(dict(sequence=self.seq,
                                  image=tlelt['iname'],
                                  imageactive=tlelt['inameactive'],
                                  i=i,
                                  zoom=1,
                                  type=tlelt['event'].type,
                                  time=tlelt['timestamp']-self.starttime,
                                  mousex=tlelt['event'].x,
                                  mousey=tlelt['event'].y,
                                  mousebtn=tlelt['event'].button if hasattr(tlelt['event'],'button') else 0,
                                  btnccount=tlelt['event'].count if hasattr(tlelt['event'],'count') else 0,
                                  activewindow=tlelt['active']))

        import json
        js = "var sce=%s;" % json.dumps(self.scenario,sort_keys=True, indent=4, separators=(',', ': '))
        with open("data.js",'w') as f:
            f.write(js)
        
        self.init(self.title)
        
    def diffImage(self,image1,image2):
        diff = ImageChops.difference(image1,image2).histogram()
        diff = 100-float(100*diff.count(0))/len(diff)
        
        return diff                



#eventTypes = 'mousePressLeft', 'mouseReleaseLeft'
#             'mousePressRight','mouseReleaseRight'
#             'mousePressMiddle','mouseReleaseMiddle'
#             'mouseWheelUp','mouseWheelDown','mouseMove','mouseSlide'
class KMEvents:
    def __init__(self):
        import platform
        if platform.system() in ['Linux']:
            from record_xlib import XlibKMEvents
            self.platformKMEvt = XlibKMEvents
        elif platform.system() in ['Windows']:
            from record_windows import WindowsKMEvents
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
            if any(self.buttonHold.values()):
                event.type = "mouseSlide"

        self.executeCallbacks(event)
        
    def bindCallback(self,types,callback):
        if not isinstance(types,tuple):
            types = (types)
        self.bindings[types] = self.bindings.get(types,[]) + [callback]
                      
    def executeCallbacks(self,event):
        import threading
        for binding,callbacks in self.bindings.iteritems():
            if event.type in binding:
                for callback in callbacks:
                    threading.Thread(target=callback,args=(event,)).start()
                    
        
 

