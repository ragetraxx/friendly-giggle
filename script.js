/* global Hls, dashjs */
const els = {
  list: document.getElementById('channelList'),
  search: document.getElementById('search'),
  clearSearch: document.getElementById('clearSearch'),
  sortAZ: document.getElementById('sortAZ'),
  sortZA: document.getElementById('sortZA'),
  shuffle: document.getElementById('shuffle'),
  video: document.getElementById('video'),
  nowTitle: document.getElementById('nowTitle'),
  nowLogo: document.getElementById('nowLogo'),
  nowInfo: document.getElementById('nowInfo'),
  status: document.getElementById('status'),
};

let channels = [];
let filtered = [];
let selectedIndex = -1;
let hls = null;
let dash = null;

async function loadChannels(){
  const res = await fetch('channels.json');
  channels = await res.json();
  normalize();
  applySearchFromURL();
  renderList();
  restoreLast();
}
function normalize(){
  channels = channels.map((c, i) => ({
     id: i,
     title: c.title || c.name || `Channel ${i+1}`,
     logo: c.logo || '',
     src: c.src || c.url || c.link || '',
     type: (c.type || '').toLowerCase(),
     group: c.group || c['group-title'] || ''
  }));
  filtered = [...channels];
}
function renderList(){
  els.list.innerHTML = '';
  filtered.forEach((c, i) => {
    const li = document.createElement('li');
    li.className = 'channel-item';
    li.setAttribute('role', 'option');
    li.dataset.index = i;
    li.innerHTML = `
      <img alt="" src="${c.logo || ''}" onerror="this.style.visibility='hidden'"/>
      <div class="title">${escapeHtml(c.title)}</div>`;
    li.addEventListener('click', () => selectAndPlay(i));
    els.list.appendChild(li);
  });
  updateSelection();
}
function escapeHtml(s){
  return s?.replace(/[&<>\"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])) || '';
}
function selectAndPlay(i){
  selectedIndex = i;
  updateSelection();
  const item = filtered[i];
  if(!item) return;
  playSource(item);
  saveLast(item);
}
function updateSelection(){
  Array.from(els.list.children).forEach((li, idx) => {
    li.setAttribute('aria-selected', idx === selectedIndex ? 'true':'false');
  });
}
function clearPlayers(){
  if(hls){ hls.destroy(); hls = null; }
  if(dash){ dash.reset(); dash = null; }
  els.video.pause();
  els.video.removeAttribute('src');
  els.video.load();
}
function playSource(item){
  clearPlayers();
  const url = item.src;
  const lower = url.toLowerCase();
  els.nowTitle.textContent = item.title;
  els.nowLogo.src = item.logo || '';
  els.nowInfo.textContent = item.group ? item.group : '';
  els.status.textContent = 'Loading…';

  // HLS
  if(lower.includes('.m3u8') || item.type === 'hls'){
    if(Hls.isSupported()){
      hls = new Hls({ maxBufferLength: 30 });
      hls.attachMedia(els.video);
      hls.on(Hls.Events.MEDIA_ATTACHED, () => hls.loadSource(url));
      hls.on(Hls.Events.MANIFEST_PARSED, () => els.video.play().catch(()=>{}));
      hls.on(Hls.Events.ERROR, (_, data) => statusError(data?.details || 'HLS error'));
    } else if(els.video.canPlayType('application/vnd.apple.mpegurl')) {
      els.video.src = url;
      els.video.play().catch(()=>{});
    } else {
      statusError('HLS not supported by this browser.');
    }
    return;
  }

  // DASH
  if(lower.includes('.mpd') || item.type === 'dash'){
    dash = dashjs.MediaPlayer().create();
    dash.initialize(els.video, url, true);
    dash.on(dashjs.MediaPlayer.events.ERROR, e => statusError(e?.event?.message || 'DASH error'));
    return;
  }

  // Fallback
  els.video.src = url;
  els.video.play().catch(()=>{});
}
function statusError(msg){
  els.status.textContent = 'Error: ' + msg;
  console.warn(msg);
}
function doSearch(){
  const q = els.search.value.trim().toLowerCase();
  filtered = channels.filter(c => (c.title+' '+(c.group||'')).toLowerCase().includes(q));
  renderList();
  selectedIndex = filtered.length ? 0 : -1;
  updateSelection();
  updateURLWithQuery(q);
}
function updateURLWithQuery(q){
  const params = new URLSearchParams(location.search);
  if(q) params.set('q', q); else params.delete('q');
  history.replaceState(null, '', '?' + params.toString());
}
function applySearchFromURL(){
  const params = new URLSearchParams(location.search);
  const q = params.get('q') || '';
  els.search.value = q;
  if(q){ doSearch(); }
}
function restoreLast(){
  const last = localStorage.getItem('lastChannel');
  if(!last) return;
  try {
    const saved = JSON.parse(last);
    const i = filtered.findIndex(c => c.src === saved.src);
    if(i >= 0){ selectAndPlay(i); }
  } catch {}
}
function saveLast(item){
  localStorage.setItem('lastChannel', JSON.stringify({ title:item.title, src:item.src }));
}
function sortAZ(){ filtered.sort((a,b)=>a.title.localeCompare(b.title)); renderList(); }
function sortZA(){ filtered.sort((a,b)=>b.title.localeCompare(a.title)); renderList(); }
function shuffle(){ for(let i=filtered.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [filtered[i],filtered[j]]=[filtered[j],filtered[i]]} renderList(); }

// Keyboard navigation
document.addEventListener('keydown', (e)=>{
  if(e.target === els.search) return;
  if(['ArrowDown','ArrowUp','Enter','f','m','F','M'].includes(e.key)){
    e.preventDefault();
  }
  if(e.key==='ArrowDown'){ selectedIndex = Math.min(filtered.length-1, (selectedIndex<0?0:selectedIndex+1)); updateSelection(); scrollIntoViewIfNeeded(); }
  if(e.key==='ArrowUp'){ selectedIndex = Math.max(0, (selectedIndex<=0?0:selectedIndex-1)); updateSelection(); scrollIntoViewIfNeeded(); }
  if(e.key==='Enter' && selectedIndex>=0){ selectAndPlay(selectedIndex); }
  if(e.key==='f' || e.key==='F'){ if(document.fullscreenElement){ document.exitFullscreen(); } else { document.documentElement.requestFullscreen().catch(()=>{});} }
  if(e.key==='m' || e.key==='M'){ els.video.muted = !els.video.muted; }
});
function scrollIntoViewIfNeeded(){
  const li = els.list.children[selectedIndex];
  if(!li) return;
  const r = li.getBoundingClientRect();
  const pr = els.list.getBoundingClientRect();
  if(r.top < pr.top || r.bottom > pr.bottom) li.scrollIntoView({block:'nearest'});
}

// Hook up UI
els.search.addEventListener('input', doSearch);
els.clearSearch.addEventListener('click', ()=>{ els.search.value=''; doSearch(); });
els.sortAZ.addEventListener('click', sortAZ);
els.sortZA.addEventListener('click', sortZA);
els.shuffle.addEventListener('click', shuffle);

loadChannels().catch(err => {
  console.error(err);
  els.status.textContent = 'Failed to load channels.json';
});
