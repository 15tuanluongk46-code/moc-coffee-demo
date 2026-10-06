import {questions, recommend} from './advisor.js';
import {startAnimation} from './animation-clock.js?v=motion-3';

const image = document.querySelector('#spin-image');
const surface = document.querySelector('#spin-surface');
const spinStatus = document.querySelector('#spin-status');
const frames = new Map();
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const animations=new Set();
const motionAllowed=()=>!reduced.matches&&document.documentElement.classList.contains('motion-enabled')&&!document.hidden;
let sequence=0, touched=false;
function stopSequence() {sequence++;if(surface.dataset.intro==='running')surface.dataset.intro='done';}
function interact() {touched=true;stopSequence();}
function reveal(element,direction=1) {
  animations.forEach(a=>a.cancel());animations.clear();
  if(!motionAllowed())return;
  const a=startAnimation(element,[{opacity:.25,transform:`translateX(${direction*12}px)`},{opacity:1,transform:'translateX(0)'}],{id:'moc-advisor',duration:280,easing:'cubic-bezier(.2,.65,.3,1)'});
  animations.add(a);a.onfinish=()=>{a.cancel();animations.delete(a);};
}
function stopDecorations() {
  if(motionAllowed())return;
  stopSequence();animations.forEach(a=>a.cancel());animations.clear();
}
reduced.addEventListener('change',stopDecorations);
document.addEventListener('visibilitychange',stopDecorations);
new MutationObserver(stopDecorations).observe(document.documentElement,{attributes:true,attributeFilter:['class']});
let desired = 0, generation = 0, preloadStarted = false;
const frameBase = new URL('.', image.src);
const url = i => new URL(`${String(i).padStart(2,'0')}.webp`, frameBase).href;
function fetchFrame(i) {
  if (!frames.has(i)) {
    const promise = new Promise((resolve, reject) => {
      const candidate = new Image();
      candidate.onload = () => resolve(candidate);
      candidate.onerror = () => { frames.delete(i); reject(new Error('image unavailable')); };
      candidate.src = url(i);
    });
    frames.set(i, promise);
  }
  return frames.get(i);
}
async function showFrame(i) {
  desired = (i % 24 + 24) % 24;
  const requested = desired, ticket = ++generation;
  surface.setAttribute('aria-busy','true');
  try {
    const candidate = await fetchFrame(requested);
    if (ticket !== generation) return;
    image.src = candidate.src; image.dataset.frame = String(requested);
    image.alt = `Túi cà phê MỘC — góc nhìn ${requested * 15} độ`;
    spinStatus.textContent = `Góc ${requested * 15}° / 360° · Xoay theo tay bạn`;
  } catch {
    if (ticket === generation) spinStatus.textContent = 'Góc này chưa tải được. Ảnh hiện tại được giữ lại; bấm xoay để thử góc khác.';
  } finally {if(ticket===generation)surface.setAttribute('aria-busy','false');}
}
async function sequenceFrames(values,intro=false) {
  const token=++sequence;
  for(const value of values) {
    if(token!==sequence||!motionAllowed())break;
    await showFrame(value);
    await new Promise(resolve=>setTimeout(resolve,intro?170:90));
  }
  if(intro)surface.dataset.intro='done';
}
function reset() {
  interact();
  if(!motionAllowed())return showFrame(0);
  const start=desired, direction=start>12?1:-1, values=[];
  for(let i=start;i%24!==0;i+=direction)values.push((i+direction+24)%24);
  if(!values.length)return showFrame(0);
  sequenceFrames(values);
}
async function preload() {
  if (preloadStarted) return;
  preloadStarted = true;
  // A sequential queue keeps image decoding/network work bounded on phones.
  for (let i=0;i<24;i++) { try { await fetchFrame(i); } catch { /* Retry on explicit navigation. */ } }
}
const observer = new IntersectionObserver(entries => {
  if (entries.some(e=>e.isIntersecting)) { preload(); observer.disconnect(); }
},{rootMargin:'180px'});
observer.observe(surface);
new IntersectionObserver(entries=>{
  if(!entries.some(e=>e.isIntersecting)) {if(surface.dataset.intro==='running')stopSequence();return;}
  if(touched||surface.dataset.intro==='done')return;
  if(!motionAllowed()){surface.dataset.intro='done';return;}
  surface.dataset.intro='running';
  sequenceFrames([0,1,2,3,4,3,2,1,0],true);
},{threshold:.65}).observe(surface);

// One entry per section. Images decode before the reveal; content stays readable
// while loading, and scrolling away cancels rather than replaying a stale entrance.
const entries = new Map();
const entryObserver = new IntersectionObserver(async records => {
  for (const record of records) {
    const section=record.target;
    const state=entries.get(section);
    state.visible=record.isIntersecting;
    if(!state.visible){state.animations.forEach(a=>a.cancel());state.animations.clear();continue;}
    if(state.started || !motionAllowed())continue;
    state.started=true;
    await Promise.all([document.fonts.ready,...[...section.querySelectorAll('img')].map(img=>img.decode().catch(()=>{}))]);
    if(!state.visible || !motionAllowed())continue;
    const elements=section.matches('.product-story')
      ? [section.querySelector('.product-hero'),section.querySelector('#product-title'),section.querySelector('.product-intro>p:not(.section-kicker)'),section.querySelector('.product-links')]
      : [section.querySelector('figure'),section.querySelector('h2'),section.querySelector('.material-heading>p:last-child')];
    elements.filter(Boolean).forEach((element,i)=>{
      const a=startAnimation(element,[{opacity:.15,transform:`translateY(${i?18:26}px)`},{opacity:1,transform:'translateY(0)'}],
        {id:'moc-product-entry',duration:i?680:1000,delay:i*120,easing:'cubic-bezier(.16,1,.3,1)',fill:'backwards'});
      animations.add(a);state.animations.add(a);
      a.onfinish=()=>{a.cancel();animations.delete(a);state.animations.delete(a);};
    });
  }
},{threshold:.25});
document.querySelectorAll('.product-story,.material-story').forEach(section=>{
  entries.set(section,{visible:false,started:false,animations:new Set()});entryObserver.observe(section);
});
document.querySelector('#spin-prev').addEventListener('click',()=>{interact();showFrame(desired-1);});
document.querySelector('#spin-next').addEventListener('click',()=>{interact();showFrame(desired+1);});
document.querySelector('#spin-reset').addEventListener('click',reset);
surface.addEventListener('keydown',event=>{
  if (!['ArrowLeft','ArrowRight','Home'].includes(event.key)) return;
  event.preventDefault();
  if(event.key==='Home')reset();else {interact();showFrame(desired+(event.key==='ArrowRight'?1:-1));}
});
let drag;
surface.addEventListener('pointerdown',event=>{
  if (event.button!==0) return;
  interact();
  drag={id:event.pointerId,x:event.clientX,y:event.clientY,start:desired,horizontal:false};
});
surface.addEventListener('pointermove',event=>{
  if (!drag || event.pointerId!==drag.id) return;
  const dx=event.clientX-drag.x,dy=event.clientY-drag.y;
  if (!drag.horizontal && Math.abs(dy)>Math.abs(dx) && Math.abs(dy)>8) {drag=null;return;}
  if (Math.abs(dx)>8 && !drag.horizontal) {drag.horizontal=true;surface.classList.add('dragging');surface.setPointerCapture(event.pointerId);}
  if (drag.horizontal) {
    const next=(drag.start+Math.round(dx/14)+48)%24;
    if (next!==desired) showFrame(next);
  }
});
for (const type of ['pointerup','pointercancel']) surface.addEventListener(type,()=>{drag=null;surface.classList.remove('dragging');});
// Touch initially captures the image. Its bubbling lost-capture event during
// transfer to the surface must not cancel the gesture we just acquired.
surface.addEventListener('lostpointercapture',event=>{if(event.target===surface){drag=null;surface.classList.remove('dragging');}});
surface.addEventListener('dragstart',event=>event.preventDefault());
const details={origin:'Arabica Cầu Đất là nguồn cảm hứng cho dòng sản phẩm minh họa này.',roast:'Concept rang vừa: hướng đến độ cân bằng giữa hương thơm, độ chua và hậu vị. Hương vị thực tế còn tùy hạt và cách pha.',pack:'Túi 250 g với nếp gấp mềm và nhãn giấy kem. Đây là thiết kế bao bì minh họa, chưa phải cam kết vật liệu hoặc khả năng bảo quản.'};
const detail=document.querySelector('#product-detail');
function reserveDetailHeight() {
  const width=detail.getBoundingClientRect().width;
  if(!width)return;
  // Measure at the actual wrapping width; the probe is never announced or laid out.
  const probe=document.createElement('p');
  probe.className='product-detail-measure';probe.setAttribute('aria-hidden','true');
  Object.assign(probe.style,{position:'absolute',visibility:'hidden',pointerEvents:'none',width:`${width}px`,minHeight:'0',maxWidth:'none',margin:'0'});
  detail.parentElement.append(probe);
  let height=0;
  for(const text of Object.values(details)) {probe.textContent=text;height=Math.max(height,probe.getBoundingClientRect().height);}
  probe.remove();detail.style.minHeight=`${Math.ceil(height)}px`;
}
let detailWidth=0;
new ResizeObserver(entries=>{
  const width=entries[0].contentRect.width;
  if(Math.abs(width-detailWidth)>.5){detailWidth=width;reserveDetailHeight();}
}).observe(detail);
document.fonts.ready.then(reserveDetailHeight);
document.querySelectorAll('[data-detail]').forEach(button=>button.addEventListener('click',()=>{
  document.querySelectorAll('[data-detail]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  document.querySelector('#product-detail').textContent=details[button.dataset.detail];
}));

const welcome=document.querySelector('#advisor-welcome');
const form=document.querySelector('#advisor-form');
const result=document.querySelector('#advisor-result');
const restart=document.querySelector('#advisor-restart');
const fieldset=document.querySelector('#advisor-question');
const next=document.querySelector('#advisor-next');
let step=0, answers={};
function focusTitle(element) {
  element.tabIndex=-1;element.focus({preventScroll:true});
  const bounds=element.getBoundingClientRect();
  const inset=document.querySelector('.header').getBoundingClientRect().bottom+12;
  if(bounds.top<inset || bounds.bottom>innerHeight-12) {
    scrollTo({top:scrollY+bounds.top-inset,behavior:'instant'});
  }
}
function renderStep(direction=1) {
  welcome.hidden=true;form.hidden=false;result.hidden=true;restart.hidden=false;
  const question=questions[step];
  document.querySelector('#advisor-step').textContent=`Câu ${step+1} / 3`;
  document.querySelector('.advisor-progress i').style.width=`${(step+1)/3*100}%`;
  fieldset.replaceChildren();
  const legend=document.createElement('legend');legend.textContent=question.title;fieldset.append(legend);
  question.choices.forEach((choice,i)=>{
    const label=document.createElement('label');label.className='advisor-option';
    const input=document.createElement('input');input.type='radio';input.name=question.key;input.value=choice;input.required=true;input.checked=answers[question.key]===choice;
    input.addEventListener('change',()=>{answers[question.key]=choice;next.disabled=false;});
    label.append(input,document.createTextNode(choice));fieldset.append(label);
  });
  document.querySelector('#advisor-back').hidden=step===0;
  next.textContent=step===2?'Xem gợi ý':'Tiếp tục';next.disabled=!answers[question.key];
  focusTitle(legend);
  fieldset.dataset.direction=direction<0?'back':'forward';reveal(fieldset,direction);
}
function showResult() {
  form.hidden=true;result.hidden=false;result.replaceChildren();
  const suggestion=recommend(answers);
  const title=document.createElement('h3');title.textContent=suggestion.title;
  result.append(title);
  for(const [key,text] of Object.entries(suggestion)) {
    if(key==='title')continue;
    const p=document.createElement('p');p.textContent=text;if(key==='recipe')p.className='recipe';result.append(p);
  }
  const note=document.createElement('p');note.className='edition-note';note.textContent='Đây là điểm khởi đầu để thử. Hãy chỉnh tỉ lệ theo chiếc tách và khẩu vị của bạn.';result.append(note);
  const actions=document.createElement('div');actions.className='result-actions';
  const methods={'Phin':['brew-phin','Phin'],'Pour-over':['brew-pour-over','Pour-over'],'Máy espresso':['brew-espresso','Espresso']};
  const [anchor,label]=methods[answers.method];
  const link=document.createElement('a');link.href='#'+anchor;link.className='boutique-button';link.textContent=`Xem cách pha ${label}`;
  const edit=document.createElement('button');edit.className='result-edit';edit.type='button';edit.textContent='Chỉnh câu trả lời';edit.addEventListener('click',()=>{step=0;renderStep();});
  actions.append(link,edit);result.append(actions);focusTitle(title);reveal(result);
}
document.querySelector('#advisor-start').addEventListener('click',()=>{step=0;renderStep();});
document.querySelector('#advisor-back').addEventListener('click',()=>{if(step>0){step--;renderStep(-1);}});
form.addEventListener('submit',event=>{event.preventDefault();if(!answers[questions[step].key])return;if(step<2){step++;renderStep();}else showResult();});
restart.addEventListener('click',()=>{answers={};step=0;form.hidden=true;result.hidden=true;welcome.hidden=false;restart.hidden=true;document.querySelector('#advisor-start').focus({preventScroll:true});});
