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
        self.parameters.define(id='name',desc='Nom du tutorial',type='string',default='snap')
        self.parameters.define(id='title',desc='Titre du tutorial',type='string',default='snap tutorial')
        self.parameters.define(id="description", desc="Description du tutorial (markdown)",type="string", default="")
        self.parameters.define(id='autoDelay',desc='Delai entre les capture auto (en s)',type='float',default=0.5)
        self.parameters.define(id='toggleKey',desc='Touche debut/arrêt prise de snapshots', type='string', default='twosuperior')
        self.parameters.define(id='followActive',desc='Observer la fenêtre active uniquement', type='boolean', default=True)
        self.parameters.define(id='cropL',desc="Correction Left (crop)", type='integer',default=0)
        self.parameters.define(id='cropR',desc="Correction Right (crop)", type='integer',default=0)
        self.parameters.define(id='cropT',desc="Correction Top (crop)", type='integer',default=0)
        self.parameters.define(id='cropB',desc="Correction Bottom (crop)", type='integer',default=0)
        self.parameters.define(id='diffPct',desc="Ecart toléré entre les images (en %)", type='float',default=1)
        self.setProfile('default')
        self.init(title)
        self.km = KMEvents()
        self.km.bindCallback(('mousePressLeft', 'mouseReleaseLeft','mouseSlide',
                           'mousePressRight','mouseReleaseRight',
                           'mousePressMiddle','mouseReleaseMiddle',
                           'mouseWheelUp','mouseWheelDown'), self.takeSnap)
        self.km.bindCallback(('mouseMove'), self.cancelTimedSnap)
        #self.km.start()
        self.parameters.setHook('toggleKey',self.reload)

    
    def reload(self):
        print "reload %s" % self.params.toggleKey
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
        self.cancelSnap = False
        
    def status(self):
        return {'n':len(self.timeline),'on':self.snapOn}
    
    def captureToggleKey(self):
        return {'key': self.km.captureToggleKey() }
        
    def start(self):
        self.snapOn = True
        self.km.start()
        self.timer = Timer(self.params.autoDelay,self.takeTimedSnap,())
        self.timer.start()
        self.seq += 1
        if not self.starttime:
            self.starttime = time.time()
        
    def takeTimedSnap(self):
        if not self.cancelSnap:
            x,y = self.km.getMouseXY()
            self.takeSnap(Event(type="timed",x=x,y=y,activeWindow=self.km.getActiveWindowGeometry()),force=True)
        else:
            print 'cancelsnap'
        self.cancelSnap = False
        if self.snapOn:
            Timer(self.params.autoDelay,self.takeTimedSnap,()).start()
    
    def cancelTimedSnap(self,event=None):
        self.cancelSnap = True        

    def stop(self):
        self.snapOn = False
        self.cancelSnap = True
        
        self.km.end()
        
    def toggle(self,event=None):
        if self.snapOn:
            self.stop()
        else:
            self.start()
    

    def takeSnap(self,event=None,force=False):
        
        if not self.km.capture:
            return
            
        self.cancelTimedSnap()
        now = time.time()
        self.waiting = 0
        if not self.lock:
            self.lock = True
            self.img = ImageGrab.grab()
            if self.lastSnap and self.diffImage(self.img,self.lastSnap)<0.1:
                self.img = self.lastSnap
            self.lock = False
        else:
            self.waiting += 1
            while self.lock:
                pass
        if event.type != 'timed' or self.waiting == 0:
            self.timeline.append(dict(timestamp=now,event=event,image=self.img,active=event.activeWindow))
        self.waiting -= 1    
        
    
        
    def saveTimeline(self):
        import os

        self.savepath = os.path.join('snap',"%s" % self.params.title)
        if not os.path.exists(self.savepath):
            os.makedirs(self.savepath)

        last = None
        imnum = 0
        sorttl = sorted(self.timeline, key=lambda k: k['timestamp'])
        for i,elt in enumerate(sorttl):
            current = elt['image']
            active=elt['active']
            if self.params.followActive:
                currentcrop = current.crop((active['x'],active['y'],active['x']+active['w'],active['y']+active['h']))
                elt['imagecrop'] = currentcrop
            event = elt['event']
            if last:
                diff = self.diffImage(current,lastimage)
                if self.params.followActive:
                    diffcrop = self.diffImage(currentcrop,lastimagecrop)
            else:
                diff = 100
                diffcrop = 100
            if (diff>self.params.diffPct) and (not self.params.followActive 
                                               or (self.params.followActive and diffcrop>self.params.diffPct )): #or (last['active'] != active):# or ('Press' in elt['event'].type) 
                    imnum += 1
                    elt['iname'] = 'im%d' % imnum
                    lastimage = current
                    
                    lastimagecrop = currentcrop
                    #elt['image'].save(os.path.join(self.savepath,"tmp%d.png" % imnum),'PNG')
            else:
                elt['iname'] = last['iname']
            
            last = elt


        self.imagesnames = {}

        count = 0
        self.imsaved = 0
        self.lastimage = ""
        def save(elt):
            self.imsaved += 1
            active = elt['active']        
            crop = elt['image'].crop((active['x']+self.params.cropL,active['y']+self.params.cropT,active['x']+active['w']+self.params.cropR,active['y']+active['h']+self.params.cropB))
            crop.save(os.path.join(self.savepath,"%s-%03d-a.png" % (self.params.title,self.imsaved)),'PNG')
            impath = os.path.join(self.savepath,"%s-%03d.png" % (self.params.title,self.imsaved))
            elt['image'].save(impath,'PNG')            
            self.imagesnames[elt['iname']] = impath
        
        self.lastevt = sorttl[0]
        self.last = None
        def compare(t1,t2):
            if not t1 or not t2:
                return True
            return  ((t1['iname']!=t2['iname']) 
                    and (
                    ((not self.params.followActive) and self.diffImage(t1['image'],t2['image'])>self.params.diffPct)
                    or (self.params.followActive and self.diffImage(t1['imagecrop'],t2['imagecrop'])>self.params.diffPct)
                    )
                    )
        steps = []
        prevstep = []
        scenario = dict(name=self.params.name,title=self.params.title,desc=self.params.description,steps=[])
        currentzoom = []
        anchorid = 0
        for i,tlelt in enumerate(sorttl):
            if (tlelt['event'].type!='timed'):
                t = tlelt['timestamp']-self.starttime
                if 'Press' in tlelt['event'].type:
                    steps.append(dict(action="anchor",id="a%d" % anchorid,title="Step %d" % anchorid,image=""))
                    #steps.append(dict(action="loadImage",image=""))
                    anchorid += 1
                    if compare(self.lastevt,self.last):
                        if not self.lastevt['iname'] in self.imagesnames.keys():
                            save(self.lastevt)
                    steps[-1]['image'] = self.imagesnames[self.lastevt['iname']]
                    self.last = self.lastevt
                if compare(tlelt,self.last):
                    if not tlelt['iname'] in self.imagesnames.keys():
                        save(tlelt)
                    showimage = True
                    self.last = tlelt
                else:
                    showimage = False    
                    
                if 'Press' in tlelt['event'].type and count==0: 
                    if (tlelt['active'] != currentzoom):
                        steps.append(dict(action='zoom',
                                          x=tlelt['active']['x'],
                                          y=tlelt['active']['y'],
                                          w=tlelt['active']['w'],
                                          h=tlelt['active']['h'],
                                          mask=True
                                    ))
                    step = dict(action='click',
                                     button=tlelt['event'].button,
                                     x=tlelt['event'].x,
                                     y=tlelt['event'].y,
                                     count=tlelt['event'].count
                                     )
                    if showimage:
                        step['image'] = self.imagesnames[tlelt['iname']];

                    steps.append(step)
                    count = tlelt['event'].count

                if 'Release' in tlelt['event'].type:
                    count -= 1
                    
                if showimage:
                    steps.append(dict(action='loadImage',image=self.imagesnames[tlelt['iname']]))
                

                
            self.lastevt = tlelt

        if compare(self.last,self.lastevt):
            save(self.lastevt)
        steps.append({
            "action": "zoom",
            "h": -1,
            "mask": True,
            "w": -1,
            "x": 0,
            "y": 0
        })
        steps.append(dict(action='loadImage',
                          image=self.imagesnames[self.lastevt['iname']]))
#                          anchor=dict(id="a%d" % anchorid,title="Step %d" % anchorid),
#                          message=dict(type="markdown",content="# End of tuto")))
        steps.append(dict(action='zoom',x=0,y=0,w=-1,h=-1,mask=True,message=dict(type="markdown",content="# End of tuto")))
        steps[0]['message'] = dict(type='markdown',content="# Start of tuto")
        scenario['steps'] = steps
        scenario['image'] = dict(name=steps[0]['image'])
        import json
        js = "var sce=%s;" % json.dumps(scenario,sort_keys=True, indent=4, separators=(',', ': '))
        with open("data.js",'w') as f:
            f.write(js)
        
        self.init(self.title)
        
    def diffImage(self,image1,image2):
        diff = ImageChops.difference(image1,image2).histogram()
        diff = 100-float(100*diff.count(0))/len(diff)
        
        return diff
