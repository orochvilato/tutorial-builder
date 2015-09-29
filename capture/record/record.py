import os
import sys
import time
import ImageChops
import math, operator

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
  
# Change path so we find Xlib
sys.path.insert(1, os.path.join(sys.path[0], '..'))
  
from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq
from Xlib.ext.xtest import fake_input
  
local_dpy = display.Display()
record_dpy = display.Display()

image_id = 1
lastim = None


import pyscreenshot as ImageGrab
import datetime
import time
# Enable regular snapshots
import time
from threading import Timer




class Event():
    def __init__(self,type=None,x=0,y=0,button=None):
        self.type = type
        self.x = x
        self.y = y
        self.button = button
        self.double = False
        self.time = time.time()
        
class Snapshot():
    def __init__(self,title="test",focus=True):
        self.buttonHold = False
        self.snapOn = False
        self.focus = focus
        self.lastEvent = None
        self.lock = False
        self.mousex = 0
        self.mousey = 0
        self.autodelay = 0.5
        self.init(title)
    
    def init(self,title):
        self.i = 0
        self.seq = 0
        self.starttime = None
        self.timeline = []
        self.scenario = []
        self.lastCall = time.time()
        self.title = title
        
    def start(self):
        self.snapOn = True
        Timer(self.autodelay,self.takeTimedSnap,()).start()
        self.seq += 1
        if not self.starttime:
            self.starttime = time.time()
    def setMousePosition(self,x,y):
        self.mousex = x;
        self.mousey = y;
        
    def takeTimedSnap(self):
        S.takeSnap(Event(type="timed"),force=True)
        if self.snapOn:
            Timer(self.autodelay,self.takeTimedSnap,()).start()
    
    def stop(self):
        self.snapOn = False
        self.takeSnap(event=Event(type='end'),force=True)

        
    def toggle(self):
        if self.snapOn:
            self.stop()
        else:
            self.start()
            
    def getActiveWindow(self):
        import Xlib.display
        display = Xlib.display.Display()
        window = display.get_input_focus().focus
        root = window.query_tree().root.id
        wmname = "ok"
        while window.query_tree().parent.id != root:
           if not wmname:
               #wmname = window.get_wm_name()
               wmname="ok"
           window = window.query_tree().parent

        geo = window.get_geometry()
        return dict(name=wmname.decode('utf8','ignore'),x=geo.x,y=geo.y,w=geo.width,h=geo.height)

    def takeSnap(self,event=None,force=False):
        if self.lock:
            print "locked",event.type
        while self.lock:
            pass
        self.lock = True
        if not event.button:
            event.x = self.mousex
            event.y = self.mousey
            event.button = self.buttonHold
                
        now = time.time()
        if event.type=='press' and event.button and self.lastEvent and self.lastEvent.button:
            self.autodelay = 0.25
            if event.time-self.lastEvent.time<0.25:
                self.lastEvent.double = True
        if event.type=='release':
            self.autodelay = 0.5
            
        if force or (self.snapOn and S.buttonHold and now-self.lastCall>0.25):
            aw = self.getActiveWindow()
            img = ImageGrab.grab()
            self.timeline.append(dict(timestamp=time.time(),event=event,image=img,active=aw))
            if event.type != 'timed':
                self.lastCall = now
        if event.button and event.type=='press':
            self.lastEvent = event
        self.lock = False
        
    
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
        self.seq = 0
        drag = False
        for i,elt in enumerate(self.timeline):
            current = elt['image']
            
            if elt['event'].type=='released' and drag==True:
                elt['event'].type = 'dragEnd'
                drag = False

            if elt['event'].type=='timed' and elt['event'].button and elt['timestamp']-last['timestamp']>0.5:
                if last['event'].type=='press':
                    last['event'].type='dragStart'
                    drag = True
                if drag:
                    elt['event'].type = 'drag'
            if self.focus:
                active=elt['active']
                
                current = current.crop((active['x'],active['y'],active['x']+active['w'],active['y']+active['h']))
            event = elt['event']
            if last:
                diff = self.diffImage(current,lastimage)
            else:
                diff = 100
            
            if not last or (diff>0.5) or (last['active'] != active) or (elt['event'].type == 'press') :
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
                                  mousebtn=tlelt['event'].button,
                                  btndouble=tlelt['event'].double,
                                  activewindow=tlelt['active']))

        import json
        js = "var sce=%s;" % json.dumps(self.scenario,sort_keys=True, indent=4, separators=(',', ': '))
        with open("data.js",'w') as f:
            f.write(js)
        
    def diffImage(self,image1,image2):
        diff = ImageChops.difference(image1,image2).histogram()
        diff = 100-float(100*diff.count(0))/len(diff)
        
        return diff                
            

  
def lookup_keysym(keysym):
    for name in dir(XK):
        if name[:3] == "XK_" and getattr(XK, name) == keysym:
            return name[3:]
    return "[%d]" % keysym
  
def record_callback(reply):
    global S
    if reply.category != record.FromServer:
        return
    if reply.client_swapped:
        print("* received swapped protocol data, cowardly ignored")
        return
    if not len(reply.data) or reply.data[0] < 2:
        # not an event
        return

    data = reply.data
    while len(data):
        event, data = rq.EventField(None).parse_binary_value(data,
                record_dpy.display, None, None)
        if event.type in [X.KeyPress, X.KeyRelease]:

            pr = event.type == X.KeyPress and "Press" or "Release"
  
            keysym = local_dpy.keycode_to_keysym(event.detail, 0)
            if not keysym:
                print("KeyCode%s %s" % (pr, event.detail))
            else:
                print("KeyStr%s %s" % (pr, lookup_keysym(keysym)))
            
            if event.type == X.KeyPress and keysym == XK.XK_Escape:
                local_dpy.record_disable_context(ctx)
                local_dpy.flush()
                return
            if event.type == X.KeyPress and keysym and lookup_keysym(keysym) == 'F8':
                S.toggle()
            if event.type == X.KeyPress and keysym and lookup_keysym(keysym) == 'F6':
                S.saveTimeline()
            if event.type == X.KeyPress and keysym and lookup_keysym(keysym) == 'Shift_R':
                S.takeSnap(Event(type="timed"),force=True)

            
        elif event.type == X.ButtonPress:
            S.buttonHold = event.detail
            
            #print("MotionNotify %i %i" % (event.root_x, event.root_y))
            S.takeSnap(Event(type="press",x=event.root_x,y=event.root_y,button=event.detail))
        elif event.type == X.ButtonRelease:
            #print("ButtonRelease %s" % event.detail)
            #print("MotionNotify %i %i" % (event.root_x, event.root_y))
            S.takeSnap(Event(type="release",x=event.root_x,y=event.root_y,button=event.detail))
            S.buttonHold = None

        elif event.type == X.MotionNotify:
            pass
            #print("MotionNotify %i %i" % (event.root_x, event.root_y))
            
            S.setMousePosition(x=event.root_x,y=event.root_y)
            #getCurrentWindow()
  
  
# Check if the extension is present







if not record_dpy.has_extension("RECORD"):
    print("RECORD extension not found")
    sys.exit(1)
r = record_dpy.record_get_version(0, 0)
print("RECORD extension version %d.%d" % (r.major_version, r.minor_version))

S = Snapshot()
# Create a recording context; we only want key and mouse events
ctx = record_dpy.record_create_context(
        0,
        [record.AllClients],
        [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.KeyPress, X.MotionNotify),
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }])
  
# Enable the context; this only returns after a call to record_disable_context,
# while calling the callback function in the meantime



record_dpy.record_enable_context(ctx, record_callback)
# Finally free the context
record_dpy.record_free_context(ctx)

  
  

