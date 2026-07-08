/* ============================================================
   KALIBRA — Portfolio Experience · Design Handoff v1.0
   Behaviour is identical to the approved v0.2 prototype.
   Vanilla JS only. No framework, no libraries, no CDN.
   ============================================================ */

/* ---- copy to clipboard (the "verify it yourself" moment) ---- */
function kcopy(el, val){
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
