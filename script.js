const video = document.getElementById("video");
const channelList = document.getElementById("channelList");
const nowTitle = document.getElementById("nowTitle");
const nowLogo = document.getElementById("nowLogo");
const statusEl = document.getElementById("status");
const search = document.getElementById("search");
const clearSearch = document.getElementById("clearSearch");

let channels = [];
let currentChannel = null;

// Load channels.json
fetch("channels.json")
  .then(r => r.json())
  .then(data => {
    channels = data;
    renderChannels(channels);
  })
  .catch(err => {
    statusEl.textContent = "Error loading channels.json";
    console.error(err);
  });

// Render list
function renderChannels(list) {
  channelList.innerHTML = "";
  list.forEach(ch => {
    const li = document.createElement("li");
    li.textContent = ch.title;
    li.tabIndex = 0;
    li.onclick = () => playChannel(ch);
    channelList.appendChild(li);
  });
}

// Play a channel
function playChannel(ch) {
  currentChannel = ch;
  nowTitle.textContent = ch.title;
  nowLogo.src = ch.logo || "";
  statusEl.textContent = "Loading " + ch.title + "…";

  if (Hls.isSupported() && (ch.type === "hls" || ch.src.endsWith(".m3u8"))) {
    const hls = new Hls();
    hls.loadSource(ch.src);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, () => {
      video.play().catch(() => {});
    });
  } else if (ch.type === "dash" || ch.src.endsWith(".mpd")) {
    const player = dashjs.MediaPlayer().create();
    player.initialize(video, ch.src, true);
  } else {
    video.src = ch.src;
    video.play().catch(() => {});
  }

  statusEl.textContent = "Now playing: " + ch.title;
}

// Search
search.addEventListener("input", () => {
  const term = search.value.toLowerCase();
  const filtered = channels.filter(c => c.title.toLowerCase().includes(term));
  renderChannels(filtered);
});
clearSearch.onclick = () => {
  search.value = "";
  renderChannels(channels);
};
