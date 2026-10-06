// Explicit document-timeline starts avoid compositor-pending starts observed in
// the headed Chrome session. Paused/hidden/reduced-motion effects are never resumed.
export function startAnimation(element, frames, options) {
  const animation = element.animate(frames, options);
  if (document.timeline.currentTime !== null) animation.startTime = document.timeline.currentTime;
  return animation;
}

export function watchAnimationClock() {
  const waiting = new Map();
  const owned = animation => animation.id?.startsWith('moc-')
    || ['moc-drift', 'moc-warmth'].includes(animation.animationName);
  const check = () => {
    if (document.hidden || !document.documentElement.classList.contains('motion-enabled')) {
      waiting.clear(); return;
    }
    const live = new Set(document.getAnimations().filter(owned));
    const now = performance.now();
    for (const animation of live) {
      if (animation.playState !== 'running' || !animation.pending || animation.startTime !== null) {
        waiting.delete(animation); continue;
      }
      if (!waiting.has(animation)) waiting.set(animation, now);
      else if (now - waiting.get(animation) >= 180 && document.timeline.currentTime !== null) {
        animation.startTime = document.timeline.currentTime - Number(animation.currentTime || 0);
        waiting.delete(animation);
      }
    }
    for (const animation of waiting.keys()) if (!live.has(animation)) waiting.delete(animation);
  };
  let timer = setInterval(check, 250);
  addEventListener('pagehide', () => { clearInterval(timer); timer=null; waiting.clear(); });
  addEventListener('pageshow', () => { if(timer===null)timer=setInterval(check,250); });
  document.addEventListener('visibilitychange', check);
}
