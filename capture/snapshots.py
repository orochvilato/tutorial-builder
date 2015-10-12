# -*- coding: utf-8 -*-
import os
import sys
import time
import ImageChops
import math, operator

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from threading import Timer,Thread
from KMEvents.events import MouseEvent,KeyEvent,Event
from KMEvents.kmevents import KMEvents
import pyscreenshot as ImageGrab
import datetime
# Enable regular snapshots
import time

import json
from parameters import Parameters
          
class Snapshot():
    def __init__(self,parameters,title="test"):
        self.snapOn = False
        self.lastEvent = None
        self.lock = False
        self.parameters = parameters
        self.parameters.define(id='title',desc='Nom de la sequence',type='string',default='snap')
        self.parameters.define(id='autoDelay',desc='Delai entre les capture auto (en s)',type='float',default=0.5)
        self.parameters.define(id='toggleKey',desc='Touche debut/arrêt prise de snapshots', type='string', default='twosuperior')
        self.parameters.define(id='followActive',desc='Observer la fenêtre active uniquement', type='boolean', default=False)
        self.parameters.define(id='cropL',desc="Correction Left (crop)", type='integer',default=0)
        self.parameters.define(id='cropR',desc="Correction Right (crop)", type='integer',default=0)
        self.parameters.define(id='cropT',desc="Correction Top (crop)", type='integer',default=0)
        self.parameters.define(id='cropB',desc="Correction Bottom (crop)", type='integer',default=0)
        self.setProfile('default')
        self.init(title)
        self.km = KMEvents()
        self.km.bindCallback(('mousePressLeft', 'mouseReleaseLeft','mouseSlide',
                           'mousePressRight','mouseReleaseRight',
                           'mousePressMiddle','mouseReleaseMiddle',
                           'mouseWheelUp','mouseWheelDown'), self.takeSnap)
        #self.km.start()
        self.parameters.setHook('toggleKey',self.reload)

    
    def reload(self):
        self.km.setToggleKey('keyPress%s' % self.params.toggleKey)
    def setProfile(self,profile):
        self.params = self.parameters.profile(profile)
        
    def init(self,title):
        self.i = 0
        self.seq = 0
        self.starttime = None
        self.timeline = []
        self.scenario = []
        self.lastCall = time.time()
        self.lastSnap = None
        self.title = title
    def status(self):
        return {'n':len(self.timeline),'on':self.snapOn}
    
    def captureToggleKey(self):
        return {'key': self.km.captureToggleKey() }
        
    def start(self):
        self.snapOn = True
        self.km.start()
        Timer(self.params.autoDelay,self.takeTimedSnap,()).start()
        self.seq += 1
        if not self.starttime:
            self.starttime = time.time()
        
    def takeTimedSnap(self):
        x,y = self.km.getMouseXY()
        self.takeSnap(Event(type="timed",x=x,y=y,activeWindow=self.km.getActiveWindowGeometry()),force=True)
        if self.snapOn:
            Timer(self.params.autoDelay,self.takeTimedSnap,()).start()
    
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
            if self.lastSnap and self.diffImage(self.img,self.lastSnap)<0.1:
                self.img = self.lastSnap
            self.lock = False
        while self.lock:
            pass
        self.timeline.append(dict(timestamp=now,event=event,image=self.img,active=event.activeWindow))
        
        
    
        
    def saveTimeline(self):
        last = None
        imnum = 0
        for i,elt in enumerate(self.timeline):
            current = elt['image']
            active=elt['active']
            if self.params.followActive:
                current = current.crop((active['x'],active['y'],active['x']+active['w'],active['y']+active['h']))
            event = elt['event']
            if last:
                diff = self.diffImage(current,lastimage)
            else:
                diff = 100
            
            if not last or (diff>0.5) or (last['active'] != active) or ('Press' in elt['event'].type) :
                    imnum += 1
                    elt['iname'] = 'im%d' % imnum
            else:
                elt['iname'] = last['iname']
            
            last = elt
            lastimage = current

        self.imagesnames = {}
        import os
        self.savepath = os.path.join('snap',"%s" % self.params.title)
        os.makedirs(self.savepath)
        
        self.imsaved = 0
        self.lastimage = ""
        def save(elt):
            self.imsaved += 1
            active = elt['active']        
            crop = elt['image'].crop((active['x']+self.params.cropL,active['y']+self.params.cropT,active['x']+active['w']+self.params.cropR,active['y']+active['h']+self.params.cropB))
            crop.save(os.path.join(self.savepath,"%s-%03d-a.png" % (self.params.title,self.imsaved)),'PNG')
            elt['image'].save(os.path.join(self.savepath,"%s-%03d.png" % (self.params.title,self.imsaved)),'PNG')            
            self.imagesnames[elt['iname']] = "%s-%03d.png" % (self.params.title,self.imsaved)

        for i,tlelt in enumerate(self.timeline):
            if (tlelt['event'].type=='timed'):
                self.lasttimed = tlelt
            else:
                if not tlelt['iname'] in imagesnames.keys():
                    save(tlelt)
                
                t = tlelt['timestamp']-self.starttime
                if (self.lasttimed['iname']!=self.lastimage):
                    save(self.lasttimed)
                    print "%03.2d loadImage %s" % (t,self.imagesnames[self.lasttimed['iname']])
                    self.lastimage = self.lasttimed['iname']
                print "%03.2d %s" % (t,tlelt['event'].type)
                print "%03.2d loadImage %s" % (t,self.imagesnames[tlelt['iname']])
                self.lastimage = tlelt['iname']
                self.scenario.append(dict(sequence=self.seq,
                                  image=self.imagesnames[tlelt['iname']],
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
