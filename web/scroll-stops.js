// Wheel detents are an input policy, not a global scroll snap: anchors, forms,
// scrollbar dragging and programmatic navigation keep their native behavior.
export function installScrollStops({ journey, isStill, onMove }) {
  const header = document.querySelector('.header');
  let frame = 0, destination = null, lastWheel = -Infinity, direction = 0;
  let accumulated = 0, consumed = false, settleTimer, nativeGesture = false, touching = false;
  const sections = ['.product-story','.product-viewer','.material-story','.advisor','.brew-guide','.site-footer'];
  const parts = '.product-intro,.product-hero,.viewer-copy,.viewer-stage,.spin-controls,.product-hotspots,.material-heading,.material-story figure,.barista-intro,.advisor-card,.guide-heading,.brew-cards article';
  const locked = () => Boolean(document.querySelector('dialog[open]'));
  const excluded = element => element instanceof Element && Boolean(element.closest('dialog,form,input,textarea,select,[contenteditable="true"],.advisor-card'));
  const top = element => element.getBoundingClientRect().top + scrollY;
  function stops() {
    const end = Math.max(1, journey.offsetHeight - innerHeight);
    const inset = header.getBoundingClientRect().height;
    const available = Math.max(120, innerHeight - inset);
    const maximum = document.documentElement.scrollHeight - innerHeight;
    const points = [0, end / 3, end * 2 / 3, end];
    for (const selector of sections) {
      const section = document.querySelector(selector);
      if (!section) continue;
      const start = top(section) - inset;
      points.push(start);
      if (section.offsetHeight > available + 2) {
        for (const part of section.querySelectorAll(parts)) points.push(top(part) - inset - 12);
        points.push(top(section) + section.offsetHeight - innerHeight);
      }
    }
    points.push(maximum);
    const sorted = [...new Set(points.map(y => Math.round(Math.max(0, Math.min(maximum,y)))))].sort((a,b)=>a-b);
    const result = [];
    for (const point of sorted) {
      if (result.length && point - result.at(-1) < 32) continue;
      // Long/mobile content is paged with overlap; no paragraph is skipped.
      if (point > end + 2 && result.length && result.at(-1) > end + 2) {
        const start = result.at(-1), gap = point - start;
        const pages = gap <= available + 2 ? 1 : Math.ceil(gap / (available * .9));
        for (let n=1; n<pages; n++) result.push(Math.round(start + gap*n/pages));
      }
      result.push(point);
    }
    return result;
  }
  function cancel() {
    cancelAnimationFrame(frame); frame = 0; destination = null;
    clearTimeout(settleTimer); nativeGesture = false;
  }
  function move(y) {
    cancel(); onMove(); destination = y;
    if (isStill()) { scrollTo({top:y,behavior:'instant'}); destination=null; return; }
    const from=scrollY, start=performance.now();
    const end=journey.offsetHeight-innerHeight;
    const duration=from<=end+2 && y<=end+2 ? 1200 : 850;
    function tick(now) {
      const t=Math.min(1,(now-start)/duration);
      const eased=(1-Math.cos(Math.PI*t))/2;
      scrollTo({top:from+(y-from)*eased,behavior:'instant'});
      if(t<1) frame=requestAnimationFrame(tick);
      else {frame=0;destination=null;}
    }
    frame=requestAnimationFrame(tick);
  }
  function nestedCanScroll(target, sign) {
    for (let element=target; element instanceof Element && element!==document.body; element=element.parentElement) {
      if (!/(auto|scroll)/.test(getComputedStyle(element).overflowY)) continue;
      if (element.scrollHeight <= element.clientHeight+2) continue;
      if (sign>0 ? element.scrollTop+element.clientHeight<element.scrollHeight-2 : element.scrollTop>2) return true;
    }
    return false;
  }
  addEventListener('wheel', event => {
    if(event.ctrlKey || event.metaKey || event.shiftKey || !event.cancelable || locked() || excluded(event.target)
      || Math.abs(event.deltaX)>Math.abs(event.deltaY) || !event.deltaY) return;
    const sign=Math.sign(event.deltaY);
    if(nestedCanScroll(event.target,sign)) { cancel(); return; }
    const now=performance.now();
    const fresh=now-lastWheel>240 || sign!==direction;
    if(fresh) {accumulated=0;consumed=false;}
    lastWheel=now;direction=sign;
    event.preventDefault();
    if(consumed) return;
    accumulated+=Math.abs(event.deltaY)*(event.deltaMode===1?16:event.deltaMode===2?innerHeight:1);
    if(accumulated<8) return;
    consumed=true;
    const position=destination ?? scrollY;
    const points=stops();
    const next=sign>0 ? points.find(y=>y>position+4) : points.findLast(y=>y<position-4);
    if(next!==undefined) move(next);
  },{passive:false});
  function settle() {
    clearTimeout(settleTimer);
    if(!nativeGesture || touching || frame || locked()) return;
    nativeGesture=false;
    const points=stops(), nearest=points.reduce((a,b)=>Math.abs(a-scrollY)<Math.abs(b-scrollY)?a:b);
    const end=journey.offsetHeight-innerHeight;
    // Journey has four discrete pictures. Long-form content uses proximity only,
    // so reading a paragraph or vertical-swiping the product never snaps backward far.
    if(scrollY<=end+2 || Math.abs(nearest-scrollY)<70) {
      if(Math.abs(nearest-scrollY)>2) move(nearest);
    }
  }
  addEventListener('touchstart',event=>{cancel();touching=true;nativeGesture=!excluded(event.target)&&!locked();},{passive:true});
  addEventListener('touchend',()=>{touching=false;if(nativeGesture)settleTimer=setTimeout(settle,200);},{passive:true});
  addEventListener('touchcancel',()=>{touching=false;cancel();},{passive:true});
  addEventListener('scroll',()=>{if(nativeGesture&&!frame){clearTimeout(settleTimer);settleTimer=setTimeout(settle,200);}},{passive:true});
  addEventListener('scrollend',settle);
  addEventListener('keydown',event=>{
    if(!['ArrowDown','ArrowUp','PageDown','PageUp','Home','End',' '].includes(event.key))return;
    cancel();nativeGesture=!excluded(event.target)&&!event.target.closest('button,a,#spin-surface')&&!locked();
  });
  addEventListener('pointerdown',event=>{if(event.pointerType!=='touch')cancel();},{passive:true});
  addEventListener('click',cancel,{capture:true});
  addEventListener('resize',cancel);
  addEventListener('popstate',cancel);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)cancel();});
}
