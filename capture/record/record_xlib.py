import os
import sys
import time
import ImageChops
import math, operator
import logging
from PIL import Image
from PIL import ImageDraw


from PIL import ImageFont


#from record import Event  

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

# Change path so we find Xlib
#sys.path.insert(1, os.path.join(sys.path[0], '..'))

class recordEvents:
    def __init__(self,snap):
        self.S = snap
    def toggleSnap(self):
        self.S.toggle()
    def finishSnap(self):
        self.S.saveTimeline()
    def takeSnap(self,event,force=False):
        self.S.takeSnap(event=event,force=force)



from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq
from Xlib.ext.xtest import fake_input

class recordEventsXlib(recordEvents):
    def __init__(self,snap):
        recordEvents.__init__(self,snap)
        self.local_dpy = display.Display()
        self.record_dpy = display.Display()
        if not self.record_dpy.has_extension("RECORD"):
            logging.error("RECORD extension not found")
            sys.exit(1)
        self.r = self.record_dpy.record_get_version(0, 0)

    def _createcontext(self):
        # Create a recording context; we only want key and mouse events
        self.ctx = self.record_dpy.record_create_context(
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
    
    def startRecord(self):
        self._createcontext()
        self.record_dpy.record_enable_context(self.ctx, self._record_callback)
    def endRecord(self):
        self.record_dpy.record_free_context(self.ctx)
       
  
    def _record_callback(self,reply):
        def lookup_keysym(keysym):
            for name in dir(XK):
                if name[:3] == "XK_" and getattr(XK, name) == keysym:
                    return name[3:]
            return "[%d]" % keysym

        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            logging.debug("* received swapped protocol data, cowardly ignored")
            return
        if not len(reply.data) or reply.data[0] < 2:
            # not an event
            return

        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data,
                self.record_dpy.display, None, None)
            if event.type in [X.KeyPress, X.KeyRelease]:
                pr = event.type == X.KeyPress and "Press" or "Release"
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
                if not keysym:
                    logging.debug("KeyCode%s %s" % (pr, event.detail))
                else:
                    logging.debug("KeyStr%s %s" % (pr, lookup_keysym(keysym)))
            
            if event.type == X.KeyPress and keysym == XK.XK_Escape:
                self.local_dpy.record_disable_context(ctx)
                self.local_dpy.flush()
                return
            if event.type == X.KeyPress and keysym and lookup_keysym(keysym) == 'F8':
                self.toggleSnap()
            if event.type == X.KeyPress and keysym and lookup_keysym(keysym) == 'F6':
                self.finishSnap()
            if event.type == X.KeyPress and keysym and lookup_keysym(keysym) == 'Shift_R':
                self.takeSnap(Event(type='timed',force=True))

            
            elif event.type == X.ButtonPress:
                self.S.buttonHold = event.detail
                self.S.takeSnap(Event(type="press",x=event.root_x,y=event.root_y,button=event.detail))
            elif event.type == X.ButtonRelease:
                #print("ButtonRelease %s" % event.detail)
                #print("MotionNotify %i %i" % (event.root_x, event.root_y))
                self.S.takeSnap(Event(type="release",x=event.root_x,y=event.root_y,button=event.detail))
                self.S.buttonHold = None

            elif event.type == X.MotionNotify:
                #print("MotionNotify %i %i" % (event.root_x, event.root_y))
                
                self.S.setMousePosition(x=event.root_x,y=event.root_y)
                #getCurrentWindow()
  

# key : actions:'press','release',keycode
# mouse : actions:'press','release','move'
#         button: 1,2,3
#
import time
t = []
def press(event):
    print event.type,event.count
    t.append((event.type,event.count))

from threading import Timer
    
class XlibKMEvents():
    def __init__(self):
        self.local_dpy = display.Display()
        self.record_dpy = display.Display()
        if not self.record_dpy.has_extension("RECORD"):
            logging.error("RECORD extension not found")
            sys.exit(1)
        self.r = self.record_dpy.record_get_version(0, 0)
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
    
    def bindMouse(self,type,callback):
        #eventTypes = 'mouseLeftPress', 'mouseLeftRelease','mouseLeftSlide',
        #             'mouseRightPress','mouseRightRelease','mouseRightSlide',
        #             'mouseMiddlePress','mouseMiddleRelease','mouseMiddleSlide',
        #             'mouseWheelUp','mouseWheelDown','mouseMove'
        self.bindings['mouse'][type] = self.bindings.get(type,[]) + [callback]

    def bindKey(self,type,keycode,callback):
        self.bindings['key'][(type,keycode)] = self.bindings.get((type,keycode),[]) + [callback]

    def executeMouseCallbacks(self,event):
        if event.type in self.bindings['mouse']:
             # in a thread ?
             for callback in self.bindings['mouse'][event.type]:
                callback(event)

    def _createcontext(self):
        # Create a recording context; we only want key and mouse events
        self.ctx = self.record_dpy.record_create_context(
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
    
    def startRecord(self):
        self._createcontext()
        import thread
        #self.record_dpy.record_enable_context(self.ctx, self._record_callback)
        thread.start_new_thread(self.record_dpy.record_enable_context,(self.ctx, self._record_callback))
        
    def endRecord(self):
        self.local_dpy.record_disable_context(self.ctx)
        self.local_dpy.flush()
        self.record_dpy.record_free_context(self.ctx)
    
    def getActiveWindowGeometry(self):
        import Xlib.display
        display = Xlib.display.Display()
        window = display.get_input_focus().focus
        root = window.query_tree().root.id
        wmname = "noname"
        while window.query_tree().parent.id != root:
           if not wmname:
               wmname = window.get_wm_name()
           window = window.query_tree().parent

        geo = window.get_geometry()
        return dict(name=wmname.decode('utf8','ignore'),x=geo.x,y=geo.y,w=geo.width,h=geo.height)
    
    def _record_callback(self,reply):
            
        def lookup_keysym(keysym):
            for name in dir(XK):
                if name[:3] == "XK_" and getattr(XK, name) == keysym:
                    return name[3:]
            return "[%d]" % keysym

        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            logging.debug("* received swapped protocol data, cowardly ignored")
            return
        if not len(reply.data) or reply.data[0] < 2:
            # not an event
            return

        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data,
                self.record_dpy.display, None, None)
            
            now = time.time()
            
            if event.type in [X.KeyPress, X.KeyRelease]:
                pr = event.type == X.KeyPress and "Press" or "Release"
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
                if not keysym:
                    logging.debug("KeyCode%s %s" % (pr, event.detail))
                else:
                    logging.debug("KeyStr%s %s" % (pr, lookup_keysym(keysym)))
            
            if event.type == X.KeyPress and keysym == XK.XK_Escape:
                self.local_dpy.record_disable_context(self.ctx)
                self.local_dpy.flush()
                return
            if event.type == X.KeyPress and keysym and lookup_keysym(keysym) == 'F8':
                pass
            if event.type == X.KeyPress and keysym and lookup_keysym(keysym) == 'F6':
                pass
            if event.type == X.KeyPress and keysym and lookup_keysym(keysym) == 'Shift_R':
                pass

            
            elif event.type == X.ButtonPress:
                if event.detail<4:
                    eventType = 'mouse'+['Left','Middle','Right','WheelUp','WheelDown'][event.detail-1]+'Press'
                    
                    logging.debug('ButtonPress %s' % eventType)
                    if self.lastButton == event.detail and (now-self.lastTime)<0.3:
                        self.lastEvent.count += 1
                        e = self.lastEvent
                    else:
                        e = MouseEvent(type=eventType,x=event.root_x,y=event.root_y,button=event.detail,count=1)
                        self.lastEvent = e

                    self.executeMouseCallbacks(e)
                    self.lastTime = now
                    self.lastButton = event.detail
                    self.holdButton = event.detail
                    
                
                
            elif event.type == X.ButtonRelease:
                eventType = 'mouse'+['Left','Middle','Right','WheelUp','WheelDown'][event.detail-1]
                if event.detail<4:
                    eventType = eventType + 'Release'
                e = MouseEvent(type=eventType,x=event.root_x,y=event.root_y,button=event.detail,count=1)
                self.executeMouseCallbacks(e)

                logging.debug("ButtonRelease %s" % eventType)
                self.holdButton = None

            elif event.type == X.MotionNotify:
                self.setMouseXY(event.root_x,event.root_y)
                eventType = 'mouseSlide' if self.holdButton else 'mouseMove'
                e = MouseEvent(type=eventType,x=event.root_x,y=event.root_y)
                self.executeMouseCallbacks(e)
               
                
                logging.debug("%s %i %i" % (eventType,event.root_x, event.root_y))
  

  
x = XlibKMEvents()
x.bindMouse('mouseLeftPress',press)
x.startRecord()
time.sleep(10)
x.endRecord()
print t
