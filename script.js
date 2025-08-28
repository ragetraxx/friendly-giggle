const videoPlayer = document.getElementById('videoPlayer');
const errorMessage = document.getElementById('errorMessage');
const channelList = document.getElementById('channelList');
const searchInput = document.getElementById('searchInput');

let channels = [];

// Load channels.json
fetch('channels.json')
  .then(response => response.json())
  .then(data => {
    channels = data;
    renderChannels();
    if (channels.length > 0) playChannel(channels[0].src);
  });

// Render channels
function renderChannels(filter = "") {
  channelList.innerHTML = "";
  channels
    .filter(ch => ch.title.toLowerCase().includes(filter.toLowerCase()))
    .forEach(channel => {
      const div = document.createElement('div');
      div.className = 'channel-item';
      div.innerHTML = `
        <img src="${channel.logo}" class="channel-logo" alt="${channel.title}">
        <p class="channel-title">${channel.title}</p>
      `;
      div.addEventListener('click', () => playChannel(channel.src));
      channelList.appendChild(div);
    });
}

// Search filter
searchInput.addEventListener('input', e => {
  renderChannels(e.target.value);
});

// Play channel
function playChannel(url) {
  if (Hls.isSupported()) {
    const hls = new Hls();
    hls.loadSource(url);
    hls.attachMedia(videoPlayer);
    hls.on(Hls.Events.MANIFEST_PARSED, () => {
      videoPlayer.play();
      errorMessage.textContent = "";
    });
    hls.on(Hls.Events.ERROR, () => {
      errorMessage.textContent = "Error loading stream.";
    });
  } else if (videoPlayer.canPlayType('application/vnd.apple.mpegurl')) {
    videoPlayer.src = url;
    videoPlayer.play();
  } else {
    errorMessage.textContent = "HLS not supported in this browser.";
  }
}
