
window.tutorial = (function () {
    var globalparams = {
        'clickcircle': 50,
    }
    function Tutorial(params) {
        this.params = params;
        this.image = params.image;
        this.sequence = new Sequence();
        this.sequence.current.image = params.image;
        image_elt = document.getElementById(this.params.name+'-image')
        image_elt.onload = function() { initViewport(this); };
        image_elt.src = this.image.name;
    }
    function initViewport(tutorial) {
        current = tutorial.sequence.current;

        current.image.w = document.getElementById(tutorial.params.name+'-image').naturalWidth;
        current.image.h = document.getElementById(tutorial.params.name+'-image').naturalHeight;
        viewport_elt = document.getElementById(tutorial.params.name+'-viewport');
        if (viewport_elt.clientWidth != current.viewport.w) {
            current.viewport.w = viewport_elt.clientWidth;
            current.viewport.h = viewport_elt.clientHeight;
            $('#'+tutorial.params.name+'-leftmask').attr('width',current.viewport.w).attr('height',current.viewport.h);
            $('#'+tutorial.params.name+'-leftmask').attr('x',0).attr('y',0).attr('width',0).attr('height',current.viewport.h);
            $('#'+tutorial.params.name+'-rightmask').attr('x',current.viewport.w).attr('y',0).attr('width',0).attr('height',current.viewport.h);
            $('#'+tutorial.params.name+'-topmask').attr('x',0).attr('y',0).attr('width',current.viewport.w).attr('height',0);
            $('#'+tutorial.params.name+'-bottommask').attr('x',0).attr('y',current.viewport.h).attr('width',current.viewport.w).attr('height',0);
            current.image.zoom = 1;
            current.zoom.x = 0;
            current.zoom.y = 0;
            current.zoom.w = current.image.w;
            current.zoom.h = current.image.h;
            current.mask.x = 0;
            current.mask.y = 0;
            current.mask.w = current.image.w;
            current.mask.h = current.image.h;
            current.mouse.x = 300;
            current.mouse.y = 200;
        }
        $('#'+tutorial.params.name+'-viewport').css('height',current.viewport.h);
        tutorial.sequence.init(params.steps);
        console.log('viewport_w='+current.viewport.w+', viewport_h='+current.viewport.h);

    }
    function Sequence() {
        this.params = {};
        for(var key in globalparams) {
            this.params[key] = globalparams[key];
        }
        this.items = [];
        this.steps = [];
        this.current = { 'image':{ 'zoom':1},
                         'zoom':{},
                         'mouse':{},
                         'viewport': {},
                         'step': {},
                         'mask':{'left':{},'right':{},'top':{},'bottom':{}}
                       };
    }            
    Sequence.prototype.init = function (scenario) {
           this.items = [];
           var currentStep = 0;
           for (i=0;i<scenario.length;i++) {
               s = scenario[i];
               if (s.action === 'step') {
                   if (s.title == undefined) {
                       s.title = "Step "+(this.steps.length+1);
                   }
                   currentStep++;
                   this.setCurrentStep(currentStep);
                   myStep = {'i':this.items.length, 'image':s.image,'title':s.title};
                   this.addStepTitle(s);
               }

               if (s.action === 'loadImage' || s.action === 'step') {
                   this.changeImage(s);
               }
               if (s.action === 'click') {
                   this.maskWindow(s);
                   this.zoomWindow(s);
                   this.moveCursor(s);
                   this.startClick(s,true);
               }
               if (s.action === 'zoomTo') {
                   this.zoomWindow(s);
               }
               if (s.action === 'text') {
                   this.changeText(s);
               }
               if (s.action === 'wait') {
                   delay = s.time;
               }
               if (s.action === 'step') {
                   myStep['zoom']={'x':zoom_x,'y':zoom_y, 'w':zoom_w,'h':zoom_h};
                   myStep['mask']={'x':mask_x, 'y':mask_y, 'w':mask_w, 'h':mask_h};
                   myStep['mouse'] = {'x':mouse_x,'y':mouse_y};
                   this.steps.push(myStep);
               }
               if (s.wait) delay = s.wait;
           }
           this.maskWindow({'x':0,'y':0,'w':this.current.image.w,'h':this.current.image.h});
           this.zoomWindow({'x':0,'y':0,'w':this.current.image.w,'h':this.current.image.h});
           this.changeText({'content':'Fin du tutorial !','type':'markdown'});
       
           this.steps[currentStep-1]['zoom']={'x':0,'y':0, 'w':this.current.image.w,'h':this.current.image.h};
           this.steps[currentStep-1]['mask']={'x':0, 'y':0, 'w':this.current.image.w, 'h':this.current.image.h};

       };
       
       Sequence.prototype.setCurrentStep = function (value) {
          console.log('value='+value);
          this.items.push({ e: $('#'+this.params.name+'-step'), p:{opacity:1}, options:{ duration:0, complete: function () {
             this.current.step = value;
             console.log("currentStep :"+this.current.step);
          }}});
       };
       
       Sequence.prototype.updateCursor = function (x,y) {
           this.current.image.x = x;
           this.current.image.x = y;
           this.current.viewport.x = (x / this.current.image.w) * this.current.viewport.w * this.current.image.zoom - this.current.viewport.x0;
           this.current.viewport.y = (y / this.current.image.h) * this.current.viewport.h * this.current.image.zoom - this.current.viewport.y0;
       };
       
       Sequence.prototype.updateMask = function (x,y,w,h) {
           v_x = (x / this.current.image.w) * this.current.viewport.w*this.current.image.zoom - this.current.viewport.x0;
           v_y = (y / this.current.image.h) * this.current.viewport.h*this.current.image.zoom - this.current.viewport.y0;
           v_w = (w / this.current.image.w) * this.current.viewport.w*this.current.image.zoom;
           v_h = (h / this.current.image.h) * this.current.viewport.h*this.current.image.zoom;         
    
           this.current.mask.left.w = ((v_x < 0) ? 0 : v_x);
           rm_w = viewport_w-v_x-v_w;

           this.current.mask.right.w = ((rm_w < 0) ? 0 : rm_w);
           rm_x = v_x+v_w;
           this.current.mask.right.x = ((rm_x < 0) ? 0 : rm_x);

           this.current.mask.top.h = ((v_y < 0) ? 0 : v_y);

           bm_h = viewport_h-v_y-v_h;
           this.current.mask.bottom.h = ((bm_h < 0) ? 0 : bm_h);
           bm_y = v_y+v_h;
           this.current.mask.bottom_y = ((bm_y <<0) ? 0 : bm_y);
           
       };
       
       Sequence.prototype.maskWindow = function (s,queue) {
           speed = ((s.speed == undefined) ? 1500 : s.speed);
           queue = ((queue == undefined) ? true : queue);

           this.updateMask(s.x,s.y,s.w,s.h);
           this.current.mask.x = s.x;
           this.current.mask.y = s.y;
           this.current.mask.w = s.w;
           this.current.mask.h = s.h;
           this.items.push({ e: $('#'+this.params.name+'-leftmask'), p: {width: this.current.mask.left.w}, options: { sequenceQueue: queue, delay:delay, duration: speed,  easing:'easeInSine' } });
           this.items.push({ e: $('#'+this.params.name+'-rightmask'), p: {width: this.current.mask.right.w,x:this.current.mask.right.x}, options: { delay:delay, duration: speed, sequenceQueue: false, easing:'easeInSine' } });
           this.items.push({ e: $('#'+this.params.name+'-topmask'), p: {height: this.current.mask.top.h}, options: { delay:delay, duration: speed, sequenceQueue: false, easing:'easeInSine' } });
           this.items.push({ e: $('#'+this.params.name+'-bottommask'), p: {height: this.current.mask.bottom.h, y: this.current.mask.bottom.y}, options: { delay:delay, duration: speed, sequenceQueue: false, easing:'easeInSine' } });

       };
       
       Sequence.prototype.updateZoom = function (_x,_y,_w,_h) {
       
           x = _x - _w * 0.01;
           y = _y - _h * 0.01;
           w = _w * 1.02;
           h = _h * 1.02;
         
           var vx = x / im_w * this.current.viewport.w;
           var vy = y / im_h * this.current.viewport.h;
           var vw = w / im_w * this.current.viewport.w;
           var vh = h / im_h * this.current.viewport.h;

           var zw = this.current.viewport.w/vw;
           var zh = this.current.viewport.h/vh;
           console.log('zw='+zw,' zh='+zh);
           if (zw>zh) {
              var z = zh;
           } else {
            var z = zw;
         }
         if (z>2) {
            z = 2;
         }
         if (z<1) {
            z = 1;
         }
         
         // Pour centrer la fenetre
         tx0 = this.current.viewport.w * (z-1) / 2;
         ty0 = this.current.viewport.h * (z-1) / 2;
         cw = (viewport_w - vw * z) /2 - vx*z;
         if (cw>0) cw=0;
         if (cw<-2*tx0) cw = -2*tx0;
         ch = (viewport_h - vh * z) /2 - vy*z;
         if (ch>0) ch=0;
         console.log('cw='+cw+', ch='+ch);
       
         var _tx = tx0 + cw; 

         var _ty = ty0 + ch;
         this.current.image.tx = _tx;
         this.current.image.ty = _ty;
         this.current.image.zoom = z;
         
         this.current.viewport.x0 = -cw;
         this.current.viewport.y0 = -ch;
       
       };
       
       Sequence.prototype.zoomWindow = function (s,queue) {
           speed = ((s.speed == undefined) ? 1500 : s.speed);
           queue = ((queue == undefined) ? true : queue);

         last_tx = this.current.image.tx;
         last_ty = this.current.image.ty;
         last_zoom = this.current.image.zoom;
         this.updateZoom(s.x,s.y,s.w,s.h);
         this.current.zoom.x = s.x;
         this.current.zoom.y = s.y;
         this.current.zoom.w = s.w;
         this.current.zoom.h = s.h;
         if ((last_tx != this.current.image.tx) && (last_ty != this.current.image.ty) && ( last_zoom != this.current.image.zoom)) {
             this.items.push({ e: $('#'+this.params.name+'-image'), 
                               p: {scale:this.current.image.zoom, marginLeft: this.current.image.tx+"px",marginTop:this.current.image.ty+"px"}, options: { delay:0, duration: speed,  easing:'easeInSine',sequenceQueue:queue } });
             this.maskWindow(s,false);
         }

       };
       
       

       Sequence.prototype.changeImage = function (s) {
           speed = ((s.speed == undefined) ? 50 : s.speed);
           this.items.push({ e: $('.cursor'), p: {left:(this.current.viewport.x)+'px',top:(this.current.viewport.y)+'px'}, options: { delay:0, duration: speed, easing:'easeOutQuart', complete: function () {
                  console.log('showImage '+s.image);
                  $('#'+this.params.name+'-image').attr('src',s.image); }} });
       };
       
       Sequence.prototype.changeText = function (s) {
           if (s.type === 'markdown') {
               var content = converter.makeHtml(s.content);
           } else {
               var content = s.content;
           }
           if (s.transition) {
               var transition = s.transition;
           } else {
               var transition = "transition.slideUpBigIn";
           }
           
           this.items.push({ e: $('#'+this.params.name+'-info'), p: { opacity:0 }, 
                             options: { duration: 750, 
                                        easing:'easeOutQuart', 
                                        complete: function () {              
                                               $('#'+this.params.name+'-info').html(content);
                                               if (s.background) $('#'+this.params.name+'-info').css('background-color',s.background)
                                               else $('#'+this.params.name+'-info').css('background-color','')
                                        }
                                       }
                           });
           this.items.push({ e: $('#'+this.params.name+'-info'), p: transition});
       };
       
       Sequence.prototype.showMessage = function (s) {
       };         
       
       Sequence.prototype.moveCursor = function (s) {
           speed = ((s.speed == undefined) ? 50 : s.speed);
           this.current.mouse.x = s.x;
           this.current.mouse.y = s.y;
           if (s.x != 0 || s.y != 0) {
               this.updateCursor(s.x,s.y);
               
               this.items.push({ e: $('#'+this.params.name+'-cursor'), p: {left:(this.current.viewport.x)+'px',top:(this.current.viewport.y)+'px'}, options: { delay:0, duration: speed, easing:'easeOutQuart'} });
               this.items.push({e: $('#'+this.params.name+'-click'), p:{left:(this.current.viewport.x-this.params.clickcircle/4)+'px',top:(this.current.viewport.y-this.params.clickcircle/4)+'px',width:(this.params.clickcircle/2)+'px',height:(this.params.clickcircle/2)+'px'}, options: { delay:0, duration:0, sequenceQueue: true }});

           }
       };
       
       Sequence.prototype.startClick = function (s,full) {
           speed = ((s.speed == undefined) ? 400 : s.speed);
           full = ((full == undefined) ? true : full)

           if (s.button == 'Left') {
            var color = 'green';
           } else if (s.button == 'Right') {
            var color = 'yellow';
           } else if (s.button == 'Middle') {
            var color = 'red';
           }
           console.log(color);
           for (r=0;r<s.count;r++) {
               this.items.push({e: $('#'+this.params.name+'-click'), p:{ left:(this.current.viewport.x-this.params.clickcircle/2)+'px',top:(this.current.viewport.y-this.params.clickcircle/2)+'px',width:(this.params.clickcircle)+'px',height:(this.params.clickcircle)+'px'}, options: { delay:0, duration:0, complete: function () { $('#'+this.params.name+'-click').css('border-color',color).css('visibility','visible');} }});
               this.items.push({ e: $('#'+this.params.name+'-click'), p: {left:(this.current.viewport.x-this.params.clickcircle/4)+'px',top:(this.current.viewport.y-this.params.clickcircle/4)+'px',width:(this.params.clickcircle/2)+'px',height:(this.params.clickcircle/2)+'px'}, options: { duration: speed/s.count}});
           }
           if (full) {
               this.items.push({ e: $('#'+this.params.name+'-click'), p: {left:(this.current.viewport.x-2)+'px',top:(this.current.viewport.y-2)+'px',width:'4px',height:'4px'}, options: { duration: speed/s.count, complete: function () { $('#'+this.params.name+'-click').css('visibility','hidden');}}});
           }

       };
       
       Sequence.prototype.endClick = function (s) {
           speed = ((s.speed == undefined) ? 400 : s.speed);
           
           this.items.push({ e: $('#'+this.params.name+'-click'), p: {left:(this.current.viewport.x-2)+'px',top:(this.current.viewport.y-2)+'px',width:'4px',height:'4px'}, options: { duration: speed, complete: function () { $('#'+this.params.name+'-click').css('visibility','hidden');}}});
       };
       
     Sequence.prototype.addStepTitle =  function (s,speed) {
         speed = ((s.speed == undefined) ? 400 : s.speed);

         this.items.push({ e: $('#'+this.params.name+'-step'), p: 'transition.slideUpOut', options:{ duration:500, complete: function () {
                   $('#'+this.params.name+'-step').html(s.title); }}});
         this.items.push({ e: $('#'+this.params.name+'-step'), p: 'transition.slideUpIn',options: { duration: speed }});
   }







    
    var tutorial = {
        Tutorial: function (params) {
            return new Tutorial(params);
        }, 
    };
    return tutorial;
}());
