(function() {

    "use strict";

    var $body = document.querySelector('body');

    // Methods/polyfills.
    !function(){ 
        function t(t){ 
            this.el=t; 
            for(var n=t.className.replace(/^\s+|\s+$/g,"").split(/\s+/),i=0;i<n.length;i++)e.call(this,n[i])
        } 
        function n(t,n,i){ 
            Object.defineProperty?Object.defineProperty(t,n,{get:i}):t.__defineGetter__(n,i)
        }
        if(!("undefined"==typeof window.Element||"classList"in document.documentElement)){
            var i=Array.prototype,e=i.push,s=i.splice,o=i.join;
            t.prototype={ 
                add:function(t){ 
                    this.contains(t)||(e.call(this,t),this.el.className=this.toString())
                },
                contains:function(t){ 
                    return-1!=this.el.className.indexOf(t)
                },
                item:function(t){ 
                    return this[t]||null
                },
                remove:function(t){ 
                    if(this.contains(t)){
                        for(var n=0;n<this.length&&this[n]!=t;n++); 
                        s.call(this,n,1),this.el.className=this.toString()
                    }
                },
                toString:function(){ 
                    return o.call(this," ")
                },
                toggle:function(t){ 
                    return this.contains(t)?this.remove(t):this.add(t),this.contains(t)
                }
            },
            window.DOMTokenList=t,
            n(Element.prototype,"classList",function(){return new t(this)})
        }
    }();

    window.canUse=function(p){ 
        if(!window._canUse)window._canUse=document.createElement("div");
        var e=window._canUse.style,up=p.charAt(0).toUpperCase()+p.slice(1);
        return p in e||"Moz"+up in e||"Webkit"+up in e||"O"+up in e||"ms"+up in e;
    };

    window.addEventListener('load', function() {
        window.setTimeout(function() {
            $body.classList.remove('is-preload');
        }, 100);
    });

    // Slideshow Background (Modified to only show one background image).
    (function() {

        // Settings.
        var settings = {
            // Only one background image. 여기에서 경로 수정하면 됨
            images: {
                'images/background_image.jpg': 'center'
            },
            delay: 6000
        };

        // Vars.
        var $wrapper, $bg;

        // Create BG wrapper, BG.
        $wrapper = document.createElement('div');
        $wrapper.id = 'bg';
        $body.appendChild($wrapper);

        for (var k in settings.images) {
            // Create BG.
            $bg = document.createElement('div');
            $bg.style.backgroundImage = 'url("' + k + '")';
            $bg.style.backgroundPosition = settings.images[k];
            $wrapper.appendChild($bg);
        }

        // Display the only background.
        $bg.classList.add('visible');
        $bg.classList.add('top');

    })();

})();