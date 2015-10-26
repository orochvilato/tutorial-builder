
window.tutorial = (function () {
    var globalparams = {
        'clickcircle': 50,
    }
    function Tutorial(params) {
        this.params = params;
        this.image = params.image;
        this.sequence = new Sequence(params);
        globalparams[params.name] = this
        
        image_elt = document.getElementById(this.params.name+'-image')
        image_elt.onload = ivp_callback(this);
        image_elt.src = this.image.name;
    }
    
    Tutorial.prototype.jump = function () {
        tutoid = '#'+this.params.name+'-';
        
       
       playon = false;
       if (force == undefined) {
           force = false;
       }
       
       if (force || (step<mySteps.length && step>=0 && step != currentStep)) {
               newSequence = [];
               currentStep = step;
               initStep(step);
               $.Velocity.RunSequence(newSequence);
       }
    }
    Tutorial.prototype.initFromContext = function(ctx) {
        console.log('initFromContext',ctx);
        tutoid = '#'+this.params.name+'-';
        $(tutoid+'leftmask').velocity('stop');
        $(tutoid+'rightmask').velocity('stop');
        $(tutoid+'topmask').velocity('stop');
        $(tutoid+'bottommask').velocity('stop');
        $(tutoid+'image').velocity('stop');
        $(tutoid+'cursor').velocity('stop');
        $(tutoid+'step').velocity('stop');
        $(tutoid+'click').velocity('stop').css('visibility','hidden');
        $(tutoid+'info').velocity('stop').css('visibility','hidden');
        $(tutoid+'msg').velocity('stop').css('visibility','hidden');
 
        newSequence = new Sequence(this.params);
        
        newSequence.current = JSON.parse(JSON.stringify(ctx));
        newSequence.changeImage({'image':ctx.image.name, 'speed':0});
        newSequence.zoomWindow({'x':ctx.zoom.x,'y':ctx.zoom.y,'w':ctx.zoom.w,'h':ctx.zoom.h,'speed':0});
        newSequence.maskWindow({'x':ctx.mask.x,'y':ctx.mask.y,'w':ctx.mask.w,'h':ctx.mask.h,'speed':0});
        newSequence.moveCursor({'x':ctx.mouse.x,'y':ctx.mouse.y,'speed':0});
        
        $.Velocity.RunSequence(newSequence.items);
    }

    Tutorial.prototype.play = function () {
       console.log(this.sequence.current.step);
       ctx = this.params.steps[this.sequence.current.step].context
       this.initFromContext(ctx);
       if (this.sequence.current.play == true) {
          this.sequence.current.play = false;
          return
       }
       this.sequence.current.play = true;
       seq = []
       
       start = ctx['i'];
       //var end = mySteps[currentStep+1]['i'];
       var end = this.sequence.items.length;

       for (i = start; i<end;i++) {
           seq.push(this.sequence.items[i]);
       }
       $.Velocity.RunSequence(seq);
    }
    function ivp_callback(tutorial) {
        return function() { initViewport(tutorial);}
    }
    function initViewport(tutorial) {
        console.log(tutorial);
        current = tutorial.sequence.current;

        current.image.w = document.getElementById(tutorial.params.name+'-image').naturalWidth;
        current.image.h = document.getElementById(tutorial.params.name+'-image').naturalHeight;
        current.image.tx = 0;
        current.image.ty = 0;
        current.image.x = 300;
        current.image.y = 200;
        viewport_elt = document.getElementById(tutorial.params.name+'-viewport');
        if (viewport_elt.clientWidth != current.viewport.w) {
            current.viewport.w = viewport_elt.clientWidth;
            current.viewport.h = viewport_elt.clientHeight;
            console.log('init',current.viewport);
            $('#'+tutorial.params.name+'-mask').attr('width',current.viewport.w).attr('height',current.viewport.h);
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
        console.log('viewport_w='+current.viewport.w+', viewport_h='+current.viewport.h);
        if (tutorial.sequence.items.length == 0) {
            tutorial.sequence.init(tutorial.params.steps);
            
        }


    }
    function Sequence(params) {
        this.params = {};
        for(var key in globalparams) {
            this.params[key] = globalparams[key];
        }
        this.current = { 'image':{ 'zoom':1},
                         'zoom':{},
                         'mouse':{},
                         'viewport': {},
                         'running':false,
                         'step': 0,
                         'mask':{'left':{},'right':{},'top':{},'bottom':{}}
                       };

        if (params != undefined) {
            this.current.image = params.image;
            this.params.name = params.name;
        }
        this.items = [];
        this.steps = [];
    }
    
    Sequence.prototype.init = function (scenario) {
           this.items = [];
           var currentStep = 0;
           for (i=0;i<scenario.length;i++) {
               s = scenario[i];
               this.setCurrentStep(i);
               s['context'] = JSON.parse(JSON.stringify(this.current));
               s['context']['i'] = this.items.length;
               if (s.action === 'stop') {
                   if (s.title == undefined) {
                       s.title = "Step "+(this.steps.length+1);
                   }
                   currentStep++;
                   this.setCurrentStep(currentStep);
                   myStep = {'i':this.items.length, 'image':s.image,'title':s.title};
                   this.addStepTitle(s);
                   if (s.message != undefined) { this.showMessage(s.message);}
               }

               if (s.action === 'loadImage' || s.action === 'step') {
                   current.image.name = s.image;
                   this.changeImage(s);
               }
               if (s.action === 'click') {
                   this.moveCursor(s);
                   if (s.image) this.changeImage(s);
                   this.startClick(s,true);
               }
               if (s.action === 'zoom') {
                   this.zoomWindow(s);
               }
               if (s.action === 'text') {
                   this.changeText(s);
               }
               if (s.action === 'wait') {
                   delay = s.time;
               }
               if (s.action === 'stop') {
                   myStep['zoom']={'x':this.current.zoom.x,'y':this.current.zoom.y, 'w':this.current.zoom.w,'h':this.current.zoom.h};
                   myStep['mask']={'x':this.current.mask.x, 'y':this.current.mask.y, 'w':this.current.mask.w, 'h':this.current.mask.h};
                   myStep['mouse'] = {'x':this.current.mouse.x,'y':this.current.mouse.y};
                   this.steps.push(myStep);
               }
               if (s.wait) delay = s.wait;
           }
           this.maskWindow({'x':0,'y':0,'w':this.current.image.w,'h':this.current.image.h});
           this.zoomWindow({'x':0,'y':0,'w':this.current.image.w,'h':this.current.image.h});
           this.changeText({'content':'Fin du tutorial !','type':'markdown'});
       
           //this.steps[currentStep-1]['zoom']={'x':0,'y':0, 'w':this.current.image.w,'h':this.current.image.h};
           //this.steps[currentStep-1]['mask']={'x':0, 'y':0, 'w':this.current.image.w, 'h':this.current.image.h};
           // Ajouter une derniere etape ???
           console.log(scenario);
           this.scenario = scenario;
       };
       
       function setCurrentStep_callback(currentobj,value) {
           console.log('setCurrentStep_callback',currentobj,value);
           return function () { currentobj.step = value };
       }
       Sequence.prototype.setCurrentStep = function (value) {
          console.log('value='+value);
          this.items.push({ e: $('#'+this.params.name+'-step'), p:{opacity:1}, options:{ duration:0, complete: 
             setCurrentStep_callback(this.current,value)}});
       };
       
       Sequence.prototype.updateCursor = function (x,y) {
           this.current.image.x = x;
           this.current.image.y = y;
           this.current.mouse.x = x;
           this.current.mouse.y = y;
           this.current.viewport.x = (x / this.current.image.w) * this.current.viewport.w * this.current.image.zoom - this.current.viewport.x0;
           this.current.viewport.y = (y / this.current.image.h) * this.current.viewport.h * this.current.image.zoom - this.current.viewport.y0;
       };
       
       Sequence.prototype.updateMask = function (x,y,w,h) {
           v_x = (x / this.current.image.w) * this.current.viewport.w*this.current.image.zoom - this.current.viewport.x0;
           v_y = (y / this.current.image.h) * this.current.viewport.h*this.current.image.zoom - this.current.viewport.y0;
           v_w = (w / this.current.image.w) * this.current.viewport.w*this.current.image.zoom;
           v_h = (h / this.current.image.h) * this.current.viewport.h*this.current.image.zoom;         
    
           this.current.mask.left.w = ((v_x < 0) ? 0 : v_x);

           rm_w = this.current.viewport.w-v_x-v_w;
           this.current.mask.right.w = ((rm_w < 0) ? 0 : rm_w);

           rm_x = v_x+v_w;
           this.current.mask.right.x = ((rm_x < 0) ? 0 : rm_x);

           this.current.mask.top.h = ((v_y < 0) ? 0 : v_y);

           bm_h = this.current.viewport.h-v_y-v_h;
           this.current.mask.bottom.h = ((bm_h < 0) ? 0 : bm_h);

           bm_y = v_y+v_h;
           this.current.mask.bottom.y = ((bm_y < 0) ? 0 : bm_y);
           
       };
       
       Sequence.prototype.maskWindow = function (s,queue) {
           speed = ((s.speed == undefined) ? 900 : s.speed);
           queue = ((queue == undefined) ? true : queue);
           this.updateMask(s.x,s.y,s.w,s.h);
           this.current.mask.x = s.x;
           this.current.mask.y = s.y;
           this.current.mask.w = s.w;
           this.current.mask.h = s.h;
           this.items.push({ e: $('#'+this.params.name+'-leftmask'), p: {width: this.current.mask.left.w}, options: { sequenceQueue: queue, delay:0, duration: speed,  easing:'easeInSine' } });
           this.items.push({ e: $('#'+this.params.name+'-rightmask'), p: {width: this.current.mask.right.w,x:this.current.mask.right.x}, options: { delay:0, duration: speed, sequenceQueue: false, easing:'easeInSine' } });
           this.items.push({ e: $('#'+this.params.name+'-topmask'), p: {height: this.current.mask.top.h}, options: { delay:0, duration: speed, sequenceQueue: false, easing:'easeInSine' } });
           this.items.push({ e: $('#'+this.params.name+'-bottommask'), p: {height: this.current.mask.bottom.h, y: this.current.mask.bottom.y}, options: { delay:0, duration: speed, sequenceQueue: false, easing:'easeInSine' } });

       };
       
       Sequence.prototype.updateZoom = function (_x,_y,_w,_h) {
           console.log(this);
           x = _x - _w * 0.01;
           y = _y - _h * 0.01;
           w = _w * 1.02;
           h = _h * 1.02;
         
           var vx = x / this.current.image.w * this.current.viewport.w;
           var vy = y / this.current.image.h * this.current.viewport.h;
           var vw = w / this.current.image.w * this.current.viewport.w;
           var vh = h / this.current.image.h * this.current.viewport.h;

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
         cw = (this.current.viewport.w - vw * z) /2 - vx*z;
         if (cw>0) cw=0;
         if (cw<-2*tx0) cw = -2*tx0;
         ch = (this.current.viewport.h - vh * z) /2 - vy*z;
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
           speed = ((s.speed == undefined) ? 900 : s.speed);
           queue = ((queue == undefined) ? true : queue);

         last_tx = this.current.image.tx;
         last_ty = this.current.image.ty;
         last_zoom = this.current.image.zoom;
         this.updateZoom(s.x,s.y,s.w,s.h);
         this.current.zoom.x = s.x;
         this.current.zoom.y = s.y;
         this.current.zoom.w = s.w;
         this.current.zoom.h = s.h;
         if ((last_tx == this.current.image.tx) && (last_ty == this.current.image.ty) && ( last_zoom == this.current.image.zoom))
             speed = 0 
         this.items.push({ e: $('#'+this.params.name+'-image'), 
                               p: {scale:this.current.image.zoom, marginLeft: this.current.image.tx+"px",marginTop:this.current.image.ty+"px"}, options: { delay:0, duration: speed,  easing:'easeInSine',sequenceQueue:queue } });
         if (s.mask == true) {                               
             this.maskWindow(s,false);
         }
       };
       
       
       function changeImage_callback(img_id,s) {
           return function() {
               console.log('changeImage_callback ',img_id,s);
               $(img_id).attr('src',s.image);
           }
       }
       Sequence.prototype.changeImage = function (s) {
           speed = ((s.speed == undefined) ? 50 : s.speed);
           this.items.push({ e: $('#'+this.params.name+'-image'), p: {opacity:1}, options: { delay:0, duration: speed, complete: changeImage_callback('#'+this.params.name+'-image',s) } });
       
       };
       function changeText_callback(info_id,s) {
           if (s.type === 'markdown') {
               var content = converter.makeHtml(s.content);
           } else {
               var content = s.content;
           }
           background = ((s.background == undefined) ? '' : s.background)
           return function () {
               $(info_id).html(content).css('background-color',background);
           }
       }
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
                                        complete: changeText_callback('#'+this.params.name+'-info',s)
                                       }
                           });
           this.items.push({ e: $('#'+this.params.name+'-info'), p: transition});
       };
       function showMessage_callback(msg_id,content,cssclass)
       {
           return function () { 
               if (cssclass != undefined) $(msg_id).addClass(cssclass);
               $(msg_id).html(content);
           }
       }
       Sequence.prototype.showMessage = function (m) {
           duration = ((m.duration == undefined) ? 3000 : duration)
           content = ((m.type == 'markdown') ? converter.makeHtml(m.content) : m.content)
           transitionin = ((m.transitionin == undefined) ? "transition.bounceUpIn" : m.transitionin)
           transitionout = ((m.transitionout == undefined) ? "transition.bounceDownOut" : m.transitionout)
           
           this.items.push({ e: $('#'+this.params.name+'-msg'), p: { opacity:0 }, 
                             options: { duration: 0, 
                                        complete: showMessage_callback('#'+this.params.name+'-msg',content,m.cssclass)
                                      }
                           });
           this.items.push({ e: $('#'+this.params.name+'-msg'), p: transitionin });
           this.items.push({ e: $('#'+this.params.name+'-msg'), p: transitionout, options: { delay:duration} });
           
       
       };         
       
       Sequence.prototype.moveCursor = function (s) {
           speed = ((s.speed == undefined) ? 1000 : s.speed);
           this.current.mouse.x = s.x;
           this.current.mouse.y = s.y;
           if (s.x != 0 || s.y != 0) {
               this.updateCursor(s.x,s.y);
               
               this.items.push({ e: $('#'+this.params.name+'-cursor'), p: {left:(this.current.viewport.x)+'px',top:(this.current.viewport.y)+'px'}, options: { delay:0, duration: speed, easing:'easeOutQuart'} });
               this.items.push({e: $('#'+this.params.name+'-click'), p:{left:(this.current.viewport.x-this.params.clickcircle/4)+'px',top:(this.current.viewport.y-this.params.clickcircle/4)+'px',width:(this.params.clickcircle/2)+'px',height:(this.params.clickcircle/2)+'px'}, options: { delay:0, duration:0, sequenceQueue: true }});

           }
       };
       function startClick_callback(click_id,s,visibility) {
           if (s.button == 'Left') {
            var color = 'green';
           } else if (s.button == 'Right') {
            var color = 'yellow';
           } else if (s.button == 'Middle') {
            var color = 'red';
           }
           console.log(color);
           return function () {
               $(click_id).css('border-color',color).css('visibility',visibility);
           }
       }
       Sequence.prototype.startClick = function (s,full) {
           speed = ((s.speed == undefined) ? 100 : s.speed);
           full = ((full == undefined) ? true : full)

           for (r=0;r<s.count;r++) {
               this.items.push({e: $('#'+this.params.name+'-click'), p:{ left:(this.current.viewport.x-this.params.clickcircle/2)+'px',top:(this.current.viewport.y-this.params.clickcircle/2)+'px',width:(this.params.clickcircle)+'px',height:(this.params.clickcircle)+'px'}, options: { delay:0, duration:0, complete: startClick_callback('#'+this.params.name+'-click',s,'visible')  }});
               this.items.push({ e: $('#'+this.params.name+'-click'), p: {left:(this.current.viewport.x-this.params.clickcircle/4)+'px',top:(this.current.viewport.y-this.params.clickcircle/4)+'px',width:(this.params.clickcircle/2)+'px',height:(this.params.clickcircle/2)+'px'}, options: { duration: speed/s.count}});
           }
           if (full) {
               this.items.push({ e: $('#'+this.params.name+'-click'), p: {left:(this.current.viewport.x-2)+'px',top:(this.current.viewport.y-2)+'px',width:'4px',height:'4px'}, options: { duration: speed/s.count, complete:startClick_callback('#'+this.params.name+'-click',s,'hidden') }});
           }

       };
       
       Sequence.prototype.endClick = function (s) {
           speed = ((s.speed == undefined) ? 400 : s.speed);
           
           this.items.push({ e: $('#'+this.params.name+'-click'), p: {left:(this.current.viewport.x-2)+'px',top:(this.current.viewport.y-2)+'px',width:'4px',height:'4px'}, options: { duration: speed, complete: function () { $('#'+this.params.name+'-click').css('visibility','hidden');}}});
       };
     
     function addStepTitle_callback(step_id,s) {
        return function () { $(step_id).html(s.title);}
     }  
     Sequence.prototype.addStepTitle =  function (s,speed) {
         speed = ((s.speed == undefined) ? 400 : s.speed);
         console.log('#'+this.params.name+'-step');
         this.items.push({ e: $('#'+this.params.name+'-step'), p: 'transition.slideUpOut', options:{ sequenceQueue:false, duration:500, complete: addStepTitle_callback('#'+this.params.name+'-step',s)
                    }});
         this.items.push({ e: $('#'+this.params.name+'-step'), p: 'transition.slideUpIn',options: { duration: speed }});
   }







    
    var tutorial = {
        Tutorial: function (params) {
            return new Tutorial(params);
        }, 
    };
    return tutorial;
}());
