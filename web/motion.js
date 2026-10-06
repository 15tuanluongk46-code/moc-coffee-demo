import { startAnimation } from './animation-clock.js?v=motion-3';
// Presentation only. app.js owns navigation, video seeks, accessibility and focus.
export function createMotion({ copies, dialog, reduce }) {
  const root = document.documentElement;
  const camera = document.querySelector('.scene-camera');
  const rail = document.querySelector('.rail');
  const groups = new Map();
  let enabled = false, introPlayed = false, hintStopped = false;
  let settleTimer, closeCallback, lastProgress = 0, arrival = null;
  const contents = copies.map(copy => {
    const content = document.createElement('div');
    content.className = 'copy-content';
    content.append(...copy.childNodes);
    copy.append(content);
    // Keep real text/emphasis and explicit line breaks; no per-letter ARIA noise.
    const heading = content.querySelector('h1,h2');
    let mask;
    [...heading.childNodes].forEach(node => {
      if (node.nodeName === 'BR') { mask = null; return; }
      if (!mask) {
        mask = document.createElement('span'); mask.className = 'line-mask';
        const line = document.createElement('span'); line.className = 'line-reveal';
        mask.append(line); heading.append(mask);
      }
      mask.firstChild.append(node);
    });
    heading.querySelectorAll('br').forEach(br => br.remove());
    return content;
  });

  function cancel(group) {
    groups.get(group)?.forEach(animation => animation.cancel());
    groups.delete(group);
  }
  function animate(element, frames, options, group, done) {
    if (!enabled || document.hidden || !element?.animate) { done?.(); return; }
    const animation = startAnimation(element, frames, {
      easing: 'cubic-bezier(.16,1,.3,1)', fill: 'backwards', ...options,
    });
    if (!groups.has(group)) groups.set(group, new Set());
    const bucket = groups.get(group); bucket.add(animation);
    animation.onfinish = () => {
      bucket.delete(animation);
      if (!bucket.size && groups.get(group) === bucket) groups.delete(group);
      animation.cancel(); done?.();
    };
    return animation;
  }
  function reveal(element, distance, duration, delay, id, group) {
    animate(element, [{ opacity: 0, transform: `translateY(${distance}px)` },
      { opacity: 1, transform: 'translateY(0)' }], { duration, delay, id }, group);
  }
  function revealCopy(index, direction, intro = false) {
    const content = contents[index], group = intro ? 'intro' : 'chapter';
    const id = intro ? 'moc-intro' : 'moc-chapter';
    const heading = content.querySelector('h1,h2');
    reveal(content.querySelector('.eyebrow'), direction * 12, 450, intro ? 150 : 0, id, group);
    heading.querySelectorAll('.line-reveal').forEach((line, i) => {
      animate(line, [{ transform: `translateY(${direction * 105}%)` }, { transform: 'translateY(0)' }],
        { duration: intro ? 850 : 580, delay: (intro ? 240 : 80) + i * 100, id }, group);
    });
    [...content.children].filter(el => el !== heading && !el.matches('.eyebrow')).forEach((el, i) => {
      reveal(el, direction * 16, intro ? 600 : 420, (intro ? 560 : 240) + i * 65, id, group);
    });
  }
  function clearChapters() { cancel('chapter'); copies.forEach(copy => copy.classList.remove('leaving')); }
  function stopHint() { hintStopped = true; cancel('hint'); }
  function syncBackground() { root.classList.toggle('motion-paused', document.hidden || dialog.open); }
  function finishClose() {
    const done = closeCallback; closeCallback = null;
    dialog.classList.remove('closing'); done?.();
  }
  function scrub(progress) {
    const activeLink = rail.querySelector('[aria-current]');
    if (activeLink) rail.style.setProperty('--rail-position', `${activeLink.offsetTop}px`);
    lastProgress = Math.max(0, Math.min(1, progress));
    const local = (lastProgress * 3) % 1;
    // Same stops as Blender's camera: hold until .28, travel .28–.83.
    const departure = Math.max(0, Math.min(1, (.36 - local) / .18));
    const approach = Math.max(0, Math.min(1, (local - .72) / .16));
    const clarity = lastProgress >= .999 ? 1 : Math.max(departure, approach);
    const arrived = arrival && Math.round(lastProgress * 3) === arrival.next && clarity >= .95;
    contents.forEach((content, index) => {
      const waiting = arrival?.next === index && !arrived;
      content.style.opacity = enabled ? String(waiting ? .12 : .12 + .88 * clarity) : '1';
    });
    if (arrived) {
      const {next, direction} = arrival; arrival = null;
      revealCopy(next, direction);
    }
  }
  function configure(still) {
    enabled = !still && !reduce.matches;
    root.classList.toggle('motion-enabled', enabled);
    if (!enabled) {
      arrival = null;
      [...groups.keys()].forEach(cancel); clearChapters(); stopHint(); finishClose();
      clearTimeout(settleTimer); root.classList.remove('motion-scrolling');
    }
    scrub(lastProgress); syncBackground();
  }
  function intro(copy) {
    if (introPlayed) return;
    introPlayed = true;
    if (!enabled || document.hidden) return;
    animate(camera, [{ transform: 'translateY(18px) scale(.94)', opacity: .55 },
      { transform: 'translateY(0) scale(1)', opacity: 1 }],
      { duration: 1400, id: 'moc-camera-intro' }, 'intro');
    reveal(document.querySelector('.wordmark'), 10, 650, 0, 'moc-intro', 'intro');
    revealCopy(copies.indexOf(copy), 1, true);
    if (!hintStopped) animate(document.querySelector('.scroll-hint'), [
      { transform: 'translateY(0)' }, { transform: 'translateY(5px)' }, { transform: 'translateY(0)' },
    ], { duration: 950, delay: 1500, iterations: 2, id: 'moc-hint' }, 'hint');
  }
  function chapter(previous, next) {
    rail.style.setProperty('--rail-position', `${rail.querySelectorAll('a')[next].offsetTop}px`);
    introPlayed = true; cancel('intro'); clearChapters(); stopHint(); arrival = null;
    if (!enabled || document.hidden || previous < 0) return;
    copies[previous].classList.add('leaving');
    animate(copies[previous], [{ opacity: 1 }, { opacity: 0 }],
      { duration: 160, id: 'moc-exit' }, 'chapter', () => copies[previous].classList.remove('leaving'));
    arrival = {next, direction: next > previous ? 1 : -1};
    scrub(lastProgress);
  }
  function scrolling() {
    if (!enabled) return;
    root.classList.add('motion-scrolling');
    clearTimeout(settleTimer);
    settleTimer = setTimeout(() => root.classList.remove('motion-scrolling'), 220);
  }
  function openDialog() {
    arrival = null;
    cancel('dialog'); cancel('intro'); clearChapters(); stopHint(); syncBackground();
    reveal(dialog, 16, 420, 0, 'moc-dialog', 'dialog');
    dialog.querySelectorAll('.notes > span').forEach((note, i) => reveal(note, 12, 380, 120 + i * 90, 'moc-note', 'dialog'));
  }
  function dismissDialog(done) {
    if (closeCallback) return;
    cancel('dialog');
    if (!enabled || document.hidden) { done(); return; }
    closeCallback = done; dialog.classList.add('closing');
    animate(dialog, [{ opacity: 1, transform: 'translateY(0) scale(1)' },
      { opacity: 0, transform: 'translateY(10px) scale(.99)' }],
      { duration: 220, easing: 'cubic-bezier(.4,0,1,1)', id: 'moc-dialog-exit' }, 'dialog', finishClose);
  }
  function closeDialog() { cancel('dialog'); closeCallback = null; dialog.classList.remove('closing'); syncBackground(); }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { [...groups.keys()].forEach(cancel); clearChapters(); stopHint(); finishClose(); }
    syncBackground();
  });
  return { configure, intro, chapter, scrub, scrolling, stopHint, openDialog, dismissDialog, closeDialog };
}
