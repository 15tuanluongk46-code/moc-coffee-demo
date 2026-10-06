/** A separate, lazy studio loop; the journey video remains the scroll clock. */
export function createExtraction() {
  const root=document.documentElement, panel=document.querySelector('#extraction');
  const video=document.querySelector('#extraction-loop'), image=document.querySelector('#extraction-poster');
  const controls=document.querySelector('#extraction-controls'), detail=document.querySelector('#extraction-detail');
  const steam=panel.querySelector('.steam');
  const reduce=matchMedia('(prefers-reduced-motion: reduce)'), fine=matchMedia('(hover: hover) and (pointer: fine)');
  let active=false, still=true, view='', loaded='', request, objectURL, version=0, moving=false, timer;
  const texts={group:'Đầu chiết xuất dẫn dòng cà phê xuống tách. Chuyển động trong cảnh là minh họa, không phải thông số pha thực tế.',cup:'Lớp crema và gợn mặt cà phê bắt ánh sáng. Một khoảnh khắc nhỏ để bạn ngắm trước khi đi tiếp.'};
  function positionSteam() {
    const portrait=view==='mobile', width=portrait?720:1280, height=portrait?1440:800;
    const pw=panel.clientWidth, ph=panel.clientHeight, scale=Math.min(pw/width,ph/height);
    // Measured Blender camera projection, adjusted for object-fit: contain.
    const x=portrait?.458354:.669081, y=portrait?.727957:.606176;
    steam.style.left=`${(pw-width*scale)/2+x*width*scale-24}px`;
    steam.style.top=`${(ph-height*scale)/2+y*height*scale-65}px`;
  }
  function sync() {
    const play=active&&!still&&!reduce.matches&&!moving&&!document.hidden&&!root.classList.contains('modal-lock');
    panel.classList.toggle('playing',play&&loaded===view&&video.readyState>=2);
    if(play&&loaded===view) video.play().catch(()=>panel.classList.remove('playing'));
    else video.pause();
    if(!play) panel.style.transform='';
  }
  function release() {
    version++;request?.abort();request=null;video.pause();video.removeAttribute('src');video.load();
    if(objectURL)URL.revokeObjectURL(objectURL);objectURL=null;loaded='';panel.classList.remove('ready');
  }
  async function load() {
    if(request||loaded===view||!active||still||reduce.matches)return;
    const ticket=version, requested=view;request=new AbortController();
    const timeout=setTimeout(()=>request?.abort(),12000);
    try {
      const response=await fetch(`media/extraction/${requested}.mp4`,{signal:request.signal});
      if(!response.ok)throw new Error('loop unavailable');
      const blob=await response.blob();
      if(ticket!==version||still||reduce.matches)return;
      objectURL=URL.createObjectURL(blob);video.src=objectURL;video.load();loaded=requested;
    } catch { /* The studio poster remains visible when the loop is unavailable. */ }
    finally {clearTimeout(timeout);if(ticket===version)request=null;}
  }
  video.addEventListener('loadeddata',()=>{panel.classList.add('ready');sync();});
  video.addEventListener('error',()=>{panel.classList.remove('ready');video.pause();});
  controls.querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>{
    controls.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    detail.textContent=texts[button.dataset.extraction];
  }));
  addEventListener('pointermove',event=>{
    if(!active||still||reduce.matches||moving||!fine.matches||document.hidden||root.classList.contains('modal-lock'))return;
    panel.style.transform=`translate(${(event.clientX/innerWidth-.5)*8}px,${(event.clientY/innerHeight-.5)*6}px)`;
  },{passive:true});
  addEventListener('scroll',()=>{moving=true;clearTimeout(timer);sync();timer=setTimeout(()=>{moving=false;sync();},180);},{passive:true});
  document.addEventListener('visibilitychange',sync);
  new MutationObserver(sync).observe(root,{attributes:true,attributeFilter:['class']});
  return { update(progress,isStill,nextView,browsing) {
    still=isStill;
    if(nextView!==view) {release();view=nextView;image.src=`media/extraction/${view}.webp`;}
    positionSteam();
    active=!browsing&&Math.abs(progress-2/3)<.035;
    panel.classList.toggle('active',active);controls.hidden=!active;controls.inert=!active;
    root.classList.toggle('extraction-active',active);
    if(still||reduce.matches){if(request||objectURL)release();}else load();
    sync();
  }};
}
