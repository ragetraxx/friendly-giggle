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

// Render channel list
function renderChannels(list) {
  channelList.innerHTML = "";
  list.forEach(ch => {
    const li = document.createElement("li");
    li.textContent = ch.name;
    li.onclick = () => playChannel(ch);
    channelList.appendChild(li);
  });
}

// Play channel
function playChannel(ch) {
  currentChannel = ch;
  nowTitle.textContent = ch.name;
  nowLogo.src = ch.logo || "";
  statusEl.textContent = "Loading " + ch.name + "…";

  if (Hls.isSupported() && ch.url.includes(".m3u8")) {
    const hls = new Hls();
    hls.loadSource(ch.url);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, () => {
      video.play().catch(() => {});
    });
  } else if (ch.url.includes(".mpd")) {
    const player = dashjs.MediaPlayer().create();
    player.initialize(video, ch.url, true);
  } else {
    video.src = ch.url;
    video.play().catch(() => {});
  }

  statusEl.textContent = "Now playing: " + ch.name;
}

// Search
search.addEventListener("input", () => {
  const term = search.value.toLowerCase();
  const filtered = channels.filter(c => c.name.toLowerCase().includes(term));
  renderChannels(filtered);
});
clearSearch.onclick = () => {
  search.value = "";
  renderChannels(channels);
};
