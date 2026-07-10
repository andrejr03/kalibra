/* ============================================================
   KALIBRA — Portfolio Experience
   Static governed-data rendering for the portfolio surface.
   Vanilla JS only. No framework, no libraries, no CDN.
   ============================================================ */

/* ---- governed data-bind render pass ---- */
(function renderGovernedData(){
  var el = document.getElementById('kalibra-data');
  if(!el) return;
  var data;
  try{ data = JSON.parse(el.textContent); }catch(e){ return; }

  function resolve(path){
    return path.split('.').reduce(function(cur, part){
      if(cur == null) return null;
      if(Array.isArray(cur)) return cur[Number(part)];
      return cur[part];
    }, data);
  }

  function format(value, node){
    var mode = node.getAttribute('data-format');
    var text;
    if(mode === 'offline-mode'){
      text = value === true ? 'OFFLINE MODE' : 'OFFLINE MODE UNVERIFIED';
    }else if(mode === 'bool-check'){
      text = value === true ? '✓ true' : '✕ false';
    }else{
      text = String(value);
    }
    return (node.getAttribute('data-prefix') || '') + text + (node.getAttribute('data-suffix') || '');
  }

  document.querySelectorAll('[data-copy-bind]').forEach(function(node){
    var val = resolve(node.getAttribute('data-copy-bind'));
    if(val != null) node.setAttribute('data-copy', String(val));
  });
  document.querySelectorAll('[data-bind]').forEach(function(node){
    var val = resolve(node.getAttribute('data-bind'));
    if(val != null) node.textContent = format(val, node);
  });
})();

/* ---- copy to clipboard (the "verify it yourself" moment) ---- */
function kcopy(el, val){
  val = el.getAttribute('data-copy') || val;
  try{ navigator.clipboard && navigator.clipboard.writeText(val); }catch(e){}
  var o = el.querySelector('.k-copy-label');
  if(o){ var t=o.textContent; o.textContent='copied'; setTimeout(function(){o.textContent=t;},1200); }
}

/* ---- smooth scroll for CTAs + nav ---- */
function scrollToStation(id){
  var t=document.getElementById(id);
  if(t){ window.scrollTo({top:t.offsetTop-60, behavior:'smooth'}); }
}
document.querySelectorAll('[data-scroll]').forEach(function(a){
  a.addEventListener('click', function(){ scrollToStation(a.getAttribute('data-scroll')); });
});
document.querySelectorAll('.navitem').forEach(function(a){
  a.addEventListener('click', function(){ scrollToStation(a.getAttribute('data-target')); });
});

/* ---- scrollspy / reading-progress rail ---- */
var items = Array.prototype.slice.call(document.querySelectorAll('.navitem'));
var byId = {}; items.forEach(function(it){ byId[it.getAttribute('data-target')] = it; });
var obs = new IntersectionObserver(function(entries){
  entries.forEach(function(e){
    if(e.isIntersecting){
      items.forEach(function(it){ it.classList.remove('active'); });
      var it = byId[e.target.id]; if(it) it.classList.add('active');
    }
  });
}, {rootMargin:'-40% 0px -55% 0px', threshold:0});
document.querySelectorAll('section.stn').forEach(function(s){ obs.observe(s); });
