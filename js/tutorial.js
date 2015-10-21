
window.tutorial = (function () {
    function Tutorial(params) {
        this.params = params;
        this.image = t.image;
        this.sequence = [];
        this.steps = [];
        this.current = 0;
        
        
        function init() {
           currentStep = 0;
       for (i=0;i<sce.steps.length;i++) {
           s = sce.steps[i];
           if (s.action === 'step') {
               if (s.title) {
                   var title = s.title;
               } else {
                   var title = "Step "+(mySteps.length+1);
               }
               
               setStep(fullSequence, currentStep + 1);
               currentStep++;
               
               myStep = {'i':fullSequence.length, 'image':s.image,'title':title};
               addStepTitle(fullSequence,title);
           }

           if (s.action === 'loadImage' || s.action === 'step') {
               changeImage(fullSequence,s.image,300);
           }
           if (s.action === 'click') {
               maskWindow(fullSequence,s.active.x,s.active.y,s.active.w,s.active.h,1000);
               zoomWindow(fullSequence,s.active.x,s.active.y,s.active.w,s.active.h,1000);
               moveCursor(fullSequence,s.x,s.y,1500);
               startClick(fullSequence,s.button,s.count,true,150);
           }
           if (s.action === 'zoomTo') {
               console.log('zoom');
               zoomWindow(fullSequence,s.zone.x,s.zone.y,s.zone.w,s.zone.h,1000);
           }
           if (s.action === 'text') {
               changeText(fullSequence,s,300);
           }
           if (s.action === 'wait') {
               delay = s.time;
           }
           if (s.action === 'step') {
               myStep['zoom']={'x':zoom_x,'y':zoom_y, 'w':zoom_w,'h':zoom_h};
               myStep['mask']={'x':mask_x, 'y':mask_y, 'w':mask_w, 'h':mask_h};
               myStep['mouse'] = {'x':mouse_x,'y':mouse_y};
               mySteps.push(myStep);
           }
           if (s.wait) delay = s.wait;
       }
       maskWindow(fullSequence,0,0,im_w,im_h,1000);
       zoomWindow(fullSequence,0,0,im_w,im_h,1000);
       changeText(fullSequence,{ 'content':'Fin du tutorial !','type':'markdown'});
       
       mySteps[mySteps.length-1]['zoom']={'x':0,'y':0, 'w':im_w,'h':im_h};
       mySteps[mySteps.length-1]['mask']={'x':0, 'y':0, 'w':im_w, 'h':im_h};

   }
   function showImage(image) {
           console.log('showImage '+image);
           $("#im1").attr('src',image);
       }
   function showImageCallback(image) {
            console.log('showImageCallback '+image);
            return function() { showImage(image);};
       }
   function updateCursor(x,y) {
           im_x = x;
           im_y = y;
           viewport_x = (x /im_w) * viewport_w*zoom - viewport_x0;
           viewport_y = (y /im_h) * viewport_h*zoom - viewport_y0;
   }
       
   function updateMask(x,y,w,h) {
       v_x = (x /im_w) * viewport_w*zoom - viewport_x0;
       v_y = (y /im_h) * viewport_h*zoom - viewport_y0;
       v_w = (w / im_w) * viewport_w*zoom;
       v_h = (h / im_h) * viewport_h*zoom;         
    
       lm_w = v_x;
       if (lm_w<0) lm_w=0;
       rm_w = viewport_w-v_x-v_w;
       if (rm_w<0) rm_w=0;
       rm_x = v_x+v_w;
       if (rm_x<0) rm_x=0;
       tm_h = v_y;
       if (tm_h<0) tm_h=0;
       bm_h = viewport_h-v_y-v_h;
       if (bm_h<0) bm_h=0;
       bm_y = v_y+v_h;
       if (bm_y<0) bm_y=0;
   }
   function maskWindow(seq,x,y,w,h,speed,queue) {
           if (speed == undefined) {
            speed=15000;
           }
           if (queue == undefined) {
            queue = true;
           }
           updateMask(x,y,w,h);
           mask_x = x;
           mask_y = y;
           mask_w = w;
           mask_h = h;
           seq.push({ e: $('#leftmask'), p: {width: lm_w}, options: { sequenceQueue: queue, delay:delay, duration: speed,  easing:'easeInSine' } });
           seq.push({ e: $('#rightmask'), p: {width: rm_w,x:rm_x}, options: { delay:delay, duration: speed, sequenceQueue: false, easing:'easeInSine' } });
           seq.push({ e: $('#topmask'), p: {height: tm_h}, options: { delay:delay, duration: speed, sequenceQueue: false, easing:'easeInSine' } });
           seq.push({ e: $('#bottommask'), p: {height: bm_h,y:bm_y}, options: { delay:delay, duration: speed, sequenceQueue: false, easing:'easeInSine' } });

       }
       function updateZoom(_x,_y,_w,_h) {
         x = _x - _w * 0.01;
         y = _y - _h * 0.01;
         w = _w * 1.02;
         h = _h * 1.02;
         
         console.log('x='+x+', y='+y+', w='+w+', h='+h);
         var vx = x / im_w * viewport_w;
         var vy = y / im_h * viewport_h;
         var vw = w / im_w * viewport_w;
         var vh = h / im_h * viewport_h;
         console.log('vx='+vx+', vy='+vy+', vw='+vw+', vh='+vh);

         var zw = viewport_w/vw;
         var zh = viewport_h/vh;
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
         tx0 = viewport_w * (z-1) / 2;
         ty0 = viewport_h * (z-1) / 2;
         cw = (viewport_w - vw * z) /2 - vx*z;
         if (cw>0) cw=0;
         if (cw<-2*tx0) cw = -2*tx0;
         ch = (viewport_h - vh * z) /2 - vy*z;
         if (ch>0) ch=0;
         console.log('cw='+cw+', ch='+ch);
       
         var _tx = tx0 + cw; 

         var _ty = ty0 + ch;
         tx = _tx;
         ty = _ty;
         zoom = z;
         
         viewport_x0 = -cw;
         viewport_y0 = -ch;
       
       }
       function zoomWindow(seq,x,y,w,h,speed,queue) {
         if (speed == undefined) {
            speed=1500;
           }
           if (queue == undefined) {
            queue = true;
           }
         last_tx = tx;
         last_ty = ty;
         last_zoom = zoom;
         updateZoom(x,y,w,h);
         zoom_x = x;
         zoom_y = y;
         zoom_w = w;
         zoom_h = h;
         if ((last_tx != tx) && (last_ty != ty) && ( last_zoom != zoom)) {
             seq.push({ e: $('#im1'), p: {scale:zoom, marginLeft: tx+"px",marginTop:ty+"px"}, options: { delay:delay, duration: speed,  easing:'easeInSine',sequenceQueue:queue } });
             maskWindow(seq,x,y,w,h,speed,false);
             delay = 0;
         }

       }
       function changeImage(seq,image,speed) {
           if (speed == undefined) {
            speed=50;
           }
           console.log('viewport_x='+viewport_x+', viewport_y='+viewport_y);
           seq.push({ e: $('.cursor'), p: {left:(viewport_x)+'px',top:(viewport_y)+'px'}, options: { delay:delay, duration: speed, easing:'easeOutQuart', complete: showImageCallback(image) } });
           delay = 0;
       }
       function showText(s) {
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
           
           $('#info').velocity({ opacity: 0 }, { duration:750, complete: function () {              
               $('#info').html(content);
               if (s.background) $('#info').css('background-color',s.background)
               else $('#info').css('background-color','')
              
            }})
           .velocity(transition); //, { display: null, duration: 1250, stagger: 40  });
       }
       function showTextCallback(s) {
           return function() { showText(s);};
       }
       function changeText(seq,s,speed) {
           if (speed == undefined) {
            speed=50;
           }
           
           seq.push({ e: $('.cursor'), p: {left:(viewport_x)+'px',top:(viewport_y)+'px'}, options: { duration: speed, easing:'easeOutQuart', complete: showTextCallback(s) } });
       }
       function showMessage(seq,s,speed) {
       }          
       
       function moveCursor(seq,nx,ny,speed,complete) {
           if (speed == undefined) {
            speed=1500;
           }
           mouse_x = nx;
           mouse_y = ny;
           if (nx != 0 || ny != 0) {
               console.log('udateCursor '+nx+','+ny);
               updateCursor(nx,ny);
               
               seq.push({ e: $('.cursor'), p: {left:(viewport_x)+'px',top:(viewport_y)+'px'}, options: { delay:delay, duration: speed, easing:'easeOutQuart', complete: complete } });
               seq.push({e: $('.click'), p:{left:(viewport_x-clickcircle/4)+'px',top:(viewport_y-clickcircle/4)+'px',width:(clickcircle/2)+'px',height:(clickcircle/2)+'px'}, options: { delay:delay, duration:0, sequenceQueue: true }});

           }
           delay = 0;
       }
       function startClick(seq,btn,repeat,full,speed) {
           if (speed == undefined) {
            speed=400;
           }
           console.log(repeat);
           if (full == undefined) {
            full=true;
           }
           if (btn == 'Left') {
            var color = 'green';
           } else if (btn == 'Right') {
            var color = 'yellow';
           } else if (btn == 'Middle') {
            var color = 'red';
           }
           console.log(color);
           for (r=0;r<repeat;r++) {
               seq.push({e: $('.click'), p:{ left:(viewport_x-clickcircle/2)+'px',top:(viewport_y-clickcircle/2)+'px',width:(clickcircle)+'px',height:(clickcircle)+'px'}, options: { delay:delay, duration:0, complete: function () { $('.click').css('border-color',color).css('visibility','visible');} }});
               seq.push({ e: $('.click'), p: {left:(viewport_x-clickcircle/4)+'px',top:(viewport_y-clickcircle/4)+'px',width:(clickcircle/2)+'px',height:(clickcircle/2)+'px'}, options: { duration: speed/repeat}});
           }
           if (full) {
               seq.push({ e: $('.click'), p: {left:(viewport_x-2)+'px',top:(viewport_y-2)+'px',width:'4px',height:'4px'}, options: { duration: speed/repeat, complete: function () { $('.click').css('visibility','hidden');}}});
           }
           delay = 0;

       }
       
       function endClick(seq,speed) {
           if (speed == undefined) {
              speed=400;
           }
           seq.push({ e: $('.click'), p: {left:(viewport_x-2)+'px',top:(viewport_y-2)+'px',width:'4px',height:'4px'}, options: { duration: speed, complete: function () { $('.click').css('visibility','hidden');}}});
       }
      function addStepTitle(seq,title,speed) {
       if (speed == undefined) speed = 500;
       seq.push({ e: $('#step'), p: 'transition.slideUpOut', options:{ duration:500, complete: function () {
                   $('#step').html(title); }}});
       seq.push({ e: $('#step'), p: 'transition.slideUpIn',options: { duration: speed }});
   }







    
    var tutorial = {
        init: function (tuto) {
            return new Tutorial(tuto);
        }, 
    };
    return tutorial;
}());
