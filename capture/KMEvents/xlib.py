
# key : actions:'press','release',keycode
# mouse : actions:'press','release','move'
#         button: 1,2,3
#
import time
import logging

from events import MouseEvent,KeyEvent

from threading import Timer,Thread
from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq
from Xlib.ext.xtest import fake_input



class XlibKMEvents(Thread):
    def __init__(self,eventCallback):
        Thread.__init__(self)
        self.local_dpy = display.Display()
        self.record_dpy = display.Display()
        if not self.record_dpy.has_extension("RECORD"):
            logging.error("RECORD extension not found")
            sys.exit(1)
        #self.r = self.record_dpy.record_get_version(0, 0)
        self.end = False
        self.eventCallback = eventCallback

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
        self.activeWindow = None
        self.mousex = -1
        self.mousey = -1
    
    def run(self):
        self.activeWindow = self.getActiveWindowGeometry()
        self.record_dpy.record_enable_context(self.ctx, self._record_callback)
        self.record_dpy.record_free_context(self.ctx)
        
    def stop(self):
        self.end = True

    def getMouseXY(self):
        return (self.mousex, self.mousey)    
    def getActiveWindowGeometry(self):
        window = self.local_dpy.get_input_focus().focus
        wmname = "unamed"
        root = window.query_tree().root.id
        while window.query_tree().parent.id != root:
           if not wmname:
               wmname = window.get_wm_name()
           window = window.query_tree().parent

        geo = window.get_geometry()
        
        self.activeWindow = dict(name=wmname.decode('utf8','ignore'),x=geo.x,y=geo.y,w=geo.width,h=geo.height)
        return self.activeWindow
    
    def _record_callback(self,reply):
        
        def lookup_keysym(keysym):
            for name in dir(XK):
                if name[:3] == "XK_" and getattr(XK, name) == keysym:
                    return name[3:]
            return "[%d]" % keysym

        if record and reply.category != record.FromServer:
            return
        if reply.client_swapped:
            logging.debug("* received swapped protocol data, cowardly ignored")
            return
        if not len(reply.data) or reply.data[0] < 2:
            # not an event
            return
        if self.end:
            self.local_dpy.record_disable_context(self.ctx)
            self.local_dpy.flush()
            return 

        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data,
                self.record_dpy.display, None, None)
            e = None
            self.mousex = event.root_x
            self.mousey = event.root_y
            if event.type in [X.KeyPress, X.KeyRelease]:
                pr = event.type == X.KeyPress and "Press" or "Release"
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
                if not keysym:
                    logging.debug("KeyCode%s %s" % (pr, event.detail))
                    code = "key%s%s" % (pr,event.detail)
                else:
                    logging.debug("KeyStr%s %s" % (pr, lookup_keysym(keysym)))
                    code = "key%s%s" % (pr,lookup_keysym(keysym))
                    
                e = KeyEvent(type=code,x=event.root_x,y=event.root_y,activeWindow=self.getActiveWindowGeometry())

            elif event.type == X.ButtonPress:
                if event.detail<4:
                    eventType = 'mousePress'+['Left','Middle','Right'][event.detail-1]
                #else:
                #   eventType = 'mouseWheel'+'Up' if event.detail==4 else 'Down'                    
                    logging.debug('ButtonPress %s' % eventType)
                    e = MouseEvent(type=eventType,x=event.root_x,y=event.root_y,button=['Left','Middle','Right'][event.detail-1],count=1,activeWindow=self.getActiveWindowGeometry())
                else:
                    e = None
            elif event.type == X.ButtonRelease:
                if event.detail<4:
                    eventType = 'mouseRelease'+['Left','Middle','Right'][event.detail-1]
                    button = ['Left','Middle','Right'][event.detail-1]
                else:
                    eventType = 'mouseWheel'+'Up' if event.detail==4 else 'Down'
                    button = None
                e = MouseEvent(type=eventType,x=event.root_x,y=event.root_y,button=button,count=1,activeWindow=self.getActiveWindowGeometry())
                logging.debug("ButtonRelease %s" % eventType)
            elif event.type == X.MotionNotify:
                eventType = 'mouseMove'
                e = MouseEvent(type=eventType,x=event.root_x,y=event.root_y,activeWindow=self.getActiveWindowGeometry())
                logging.debug("%s %i %i" % (eventType,event.root_x, event.root_y))
                
            if e:
                self.eventCallback(e)

