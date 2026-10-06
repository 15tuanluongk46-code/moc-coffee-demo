import { createMotion } from './motion.js?v=motion-3';
import { installScrollStops } from './scroll-stops.js?v=motion-3';
import { watchAnimationClock } from './animation-clock.js?v=motion-3';

const film = document.querySelector('#film');
const poster = document.querySelector('#poster');
const portraitPoster = document.querySelector('#portrait-poster');
const stage = document.querySelector('.stage');
const status = document.querySelector('#status');
const motion = document.querySelector('#motion');
const dialog = document.querySelector('#flavors');
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
const portrait = matchMedia('(max-aspect-ratio: 1/1)');
const copies = [...document.querySelectorAll('.copy')];
const links = [...document.querySelectorAll('.rail a, .header nav a')];
const ids = ['origin', 'roast', 'brew', 'ritual'];
const effects = createMotion({ copies, dialog, reduce });
let still = reduce.matches;
let ready = false;
let chapter = -1;
let progress = 0;
let target = 0;
let view = portrait.matches ? 'mobile' : 'desktop';
let pending = false;
let width = innerWidth;
let height = innerHeight;
let navigating = null;
let loadTimer;
let videoRequest;
let videoObjectURL;
let loadVersion = 0;
let lockedProgress = null;
let browsing = false;
let contentNavigation = false;
let presentedTime = 0, frameCallback = null;
let fontsReady = false, posterReady = false, posterDeadline = false, introEligible = true;
const journey = document.querySelector('#journey');

document.documentElement.classList.add('js');
watchAnimationClock();
copies.forEach(copy => copy.querySelector('h1,h2').tabIndex = -1);
history.scrollRestoration = 'manual';

function range() { return Math.max(1, journey.offsetHeight - innerHeight); }
function writeHistory(mode, i) {
  history[mode]({ chapter: i }, '', '#' + ids[i]);
}
function focusHeading(i) { copies[i].querySelector('h1,h2').focus({ preventScroll: true }); }

function updateChapter(next) {
  if (chapter === next) return;
  const previous = chapter;
  chapter = next;
  copies.forEach((copy, i) => {
    copy.classList.toggle('active', i === chapter);
    copy.inert = i !== chapter;
    copy.setAttribute('aria-hidden', String(i !== chapter));
  });
  links.forEach(link => {
    if (link.hash === '#' + ids[chapter]) link.setAttribute('aria-current', 'step');
    else link.removeAttribute('aria-current');
  });
  document.querySelector('#chapter-number').textContent = String(chapter + 1).padStart(2, '0');
  const suffix = String(chapter + 1).padStart(2, '0');
  portraitPoster.srcset = `media/journey-v2/mobile-${suffix}.webp`;
  poster.src = `media/journey-v2/desktop-${suffix}.webp`;
  document.querySelector('.scroll-hint').textContent = chapter === 3
    ? '✓ Bạn đã đến trạm cuối' : '↓ CUỘN ĐỂ KHÁM PHÁ';
  if (navigating === null && !browsing && !contentNavigation) writeHistory('replaceState', chapter);
  if (previous >= 0) effects.chapter(previous, next);
}

function seek() {
  if (!ready || still || film.seeking || !Number.isFinite(film.duration)) return;
  const desired = Math.min(film.duration - 1 / 24, Math.max(0, target));
  if (Math.abs(film.currentTime - desired) > 1 / 48) film.currentTime = desired;
}

function update() {
  pending = false;
  // Resize can dispatch scroll before resize; compare geometry before sampling scrollY.
  if (width !== innerWidth || height !== innerHeight) {
    width = innerWidth; height = innerHeight;
    if (!browsing && !contentNavigation) scrollTo({ top: progress * range(), behavior: 'instant' });
  }
  if (lockedProgress !== null) return;
  browsing = scrollY > range() + 4;
  document.documentElement.classList.toggle('browsing', browsing);
  copies.forEach((copy,i)=>{copy.inert=browsing || i!==chapter;copy.setAttribute('aria-hidden',String(browsing || i!==chapter));});
  progress = Math.max(0, Math.min(1, scrollY / range()));
  if (progress > .002) effects.stopHint();
  target = progress * (287 / 24);
  updateChapter(Math.min(3, Math.floor(progress * 3 + .5)));
  if (browsing) copies.forEach(copy=>{copy.inert=true;copy.setAttribute('aria-hidden','true');});
  document.querySelector('#progress').style.transform = `scaleX(${progress})`;
  seek();
  effects.scrub(ready && !still ? presentedTime / (287 / 24) : progress);
  if (navigating !== null && Math.abs(progress - navigating / 3) < 1 / range()) {
    const destination = navigating;
    navigating = null;
    focusHeading(destination);
  }
}
function schedule() { if (!pending) { pending = true; requestAnimationFrame(update); } }

function navigate(i, push = true, smooth = true) {
  if (i < 0) return;
  contentNavigation = false;
  navigating = i;
  if (push && location.hash !== '#' + ids[i]) writeHistory('pushState', i);
  scrollTo({ top: i / 3 * range(), behavior: smooth && !still ? 'smooth' : 'instant' });
  update();
}

function updateMotionLabel() {
  effects.configure(still);
  if (still || reduce.matches) document.querySelectorAll('.brew-cards article').forEach(card => {
    card.getAnimations().forEach(animation => animation.cancel());
  });
  motion.setAttribute('aria-pressed', String(still));
  motion.setAttribute('aria-label', still ? 'Bật lại video chuyển động' : 'Bật chế độ ảnh tĩnh');
  motion.innerHTML = `${still ? 'Bật video' : 'Chế độ tĩnh'} <span aria-hidden="true">${still ? '▶' : '◌'}</span>`;
}
function fallback() {
  clearTimeout(loadTimer);
  releaseVideo();
  ready = false; still = true;
  stage.classList.remove('video-ready');
  film.pause(); film.removeAttribute('src'); film.load();
  updateMotionLabel();
  status.textContent = 'Video chưa tải được · Ảnh tĩnh sẵn sàng. Bấm “Bật video” để thử lại.';
}
function releaseVideo() {
  if (frameCallback !== null && film.cancelVideoFrameCallback) film.cancelVideoFrameCallback(frameCallback);
  frameCallback = null; presentedTime = 0;
  loadVersion++;
  videoRequest?.abort();
  videoRequest = null;
  film.pause(); film.removeAttribute('src'); film.load();
  if (videoObjectURL) URL.revokeObjectURL(videoObjectURL);
  videoObjectURL = null;
}
async function load() {
  clearTimeout(loadTimer);
  releaseVideo();
  const version = loadVersion;
  ready = false;
  stage.classList.remove('video-ready');
  updateMotionLabel();
  if (still) {
    film.pause(); film.removeAttribute('src'); film.load();
    status.textContent = 'Chế độ ảnh tĩnh · Cuộn để đổi cảnh';
    return;
  }
  status.textContent = 'Đang tải video · Bạn vẫn có thể khám phá bằng ảnh';
  film.preload = 'auto';
  film.dataset.view = view;
  videoRequest = new AbortController();
  loadTimer = setTimeout(fallback, 12000);
  try {
    // Small, fully downloaded clips remain seekable even on hosts without Range.
    const response = await fetch(`media/journey-v2/journey-${view}.mp4`, { signal: videoRequest.signal });
    if (!response.ok) throw new Error(`Video HTTP ${response.status}`);
    const blob = await response.blob();
    if (version !== loadVersion || still) return;
    videoObjectURL = URL.createObjectURL(blob);
    film.src = videoObjectURL;
    film.load();
  } catch (error) {
    if (version === loadVersion && error.name !== 'AbortError') fallback();
  }
}
film.addEventListener('loadeddata', () => {
  if (still) return;
  clearTimeout(loadTimer);
  ready = true;
  stage.classList.add('video-ready');
  status.textContent = 'Một hành trình, bốn điểm chạm.';
  presentedTime = film.currentTime;
  if (film.requestVideoFrameCallback) {
    const version = loadVersion;
    const presented = (_, metadata) => {
      if (version !== loadVersion || still) return;
      presentedTime = metadata.mediaTime;
      effects.scrub(presentedTime / (287 / 24));
      frameCallback = film.requestVideoFrameCallback(presented);
    };
    frameCallback = film.requestVideoFrameCallback(presented);
  }
  maybeIntro();
  schedule();
});
film.addEventListener('seeked', () => {
  if (!film.requestVideoFrameCallback) { presentedTime = film.currentTime; effects.scrub(presentedTime / (287 / 24)); }
  seek();
});
film.addEventListener('error', () => { if (film.hasAttribute('src')) fallback(); });
motion.addEventListener('click', () => { still = !still; load(); });
reduce.addEventListener('change', () => { still = reduce.matches; load(); });
addEventListener('scroll', () => { effects.scrolling(); schedule(); }, { passive: true });
addEventListener('resize', () => {
  update();
  const nextView = portrait.matches ? 'mobile' : 'desktop';
  if (nextView !== view) { view = nextView; load(); }
});
addEventListener('pageshow', schedule);
function navigateContent(hash, push = true) {
  const destination = document.getElementById(hash.slice(1));
  if (!destination) return;
  navigating = null; contentNavigation = true;
  if (push && location.hash !== hash) history.pushState({section:hash},'',hash);
  destination.scrollIntoView({behavior:'instant',block:'start'});
  const heading=destination.querySelector('h2,h3') || destination;
  heading.tabIndex=-1;heading.focus({preventScroll:true});
  if(destination.matches('.brew-cards article') && !still && !reduce.matches) {
    destination.getAnimations().forEach(animation=>animation.cancel());
    const highlight=destination.animate([{backgroundColor:'#c5c9ac70'},{backgroundColor:'transparent'}],{duration:1400,easing:'ease-out'});
    highlight.onfinish=()=>highlight.cancel();
  }
  update();contentNavigation=false;
}
addEventListener('popstate', () => {
  const i=ids.indexOf(location.hash.slice(1));
  if(i>=0 || !location.hash) navigate(Math.max(0,i),false,false);
  else navigateContent(location.hash,false);
});
function interruptNavigation() {
  if (navigating === null || dialog.open) return;
  navigating = null;
  scrollTo({ top: scrollY, behavior: 'instant' });
  writeHistory('replaceState', chapter);
}
addEventListener('wheel', interruptNavigation, { passive: true });
addEventListener('touchstart', interruptNavigation, { passive: true });
addEventListener('keydown', event => {
  if (['ArrowDown','ArrowUp','PageDown','PageUp','Home','End',' '].includes(event.key)) interruptNavigation();
});
document.addEventListener('click', event => {
  const link=event.target.closest('a[href^="#"]');
  if(!link || link.hash==='#journey' || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  const i=ids.indexOf(link.hash.slice(1));
  if(i>=0) navigate(i);else navigateContent(link.hash);
});
document.querySelector('#discover').addEventListener('click', () => {
  navigating = null;
  scrollTo({ top: scrollY, behavior: 'instant' });
  update(); lockedProgress = progress;
  document.documentElement.classList.add('modal-lock');
  dialog.showModal();
  effects.openDialog();
});
dialog.addEventListener('close', () => {
  effects.closeDialog();
  const saved = lockedProgress;
  document.documentElement.classList.remove('modal-lock');
  lockedProgress = null;
  if (saved !== null) { progress = saved; scrollTo({ top: progress * range(), behavior: 'instant' }); }
  update();
  document.querySelector('#discover').focus({ preventScroll: true });
});
const dismissDialog = () => effects.dismissDialog(() => dialog.close());
dialog.addEventListener('cancel', event => { event.preventDefault(); dismissDialog(); });
dialog.querySelector('.close').addEventListener('click', dismissDialog);
dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const r = dialog.getBoundingClientRect();
  if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dismissDialog();
});
const initialHash=location.hash;
const initialContent=initialHash && !ids.includes(initialHash.slice(1)) && document.getElementById(initialHash.slice(1));
const initial = Math.max(0, ids.indexOf(initialHash.slice(1)));
contentNavigation=Boolean(initialContent);
navigating = initial;
if(!initialContent) writeHistory('replaceState', initial);
scrollTo({ top: initial / 3 * range(), behavior: 'instant' });
function maybeIntro() {
  if (!introEligible || document.hidden || !fontsReady || (!ready && !(posterDeadline && posterReady))) return;
  introEligible = false;
  if (!browsing && !still && chapter === initial && Math.abs(progress-initial/3)<.002) effects.intro(copies[initial]);
}
for (const name of ['wheel','pointerdown','keydown','touchstart']) addEventListener(name,()=>{introEligible=false;},{once:true,passive:true});
document.addEventListener('visibilitychange',maybeIntro);
document.fonts.ready.then(()=>{fontsReady=true;maybeIntro();});
poster.decode().then(()=>{posterReady=true;maybeIntro();}).catch(()=>{});
setTimeout(()=>{posterDeadline=true;maybeIntro();},2000);
update(); load();
if(initialContent) {
  navigateContent(initialHash,false);
  document.fonts.ready.then(()=>{if(location.hash===initialHash)navigateContent(initialHash,false);});
}
installScrollStops({ journey, isStill: () => still, onMove: () => {
  navigating = null; contentNavigation = false;
} });
