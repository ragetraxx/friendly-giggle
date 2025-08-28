const video = document.getElementById("videoPlayer");
const errorMessage = document.getElementById("errorMessage");
const searchInput = document.getElementById("searchInput");
const channelsContainer = document.getElementById("channelsContainer");

let channels = [];

// Load channels.json
fetch("channels.json")
  .then(res => res.json())
  .then(data => {
    channels = data;
    renderChannels(channels);
  })
  .catch(() => {
    errorMessage.textContent = "Failed to load channels.";
  });

// Render Channels
function renderChannels(list) {
  channelsContainer.innerHTML = "";
  list.forEach(channel => {
    const div = document.createElement("div");
    div.classList.add("channel-card");
    div.innerHTML = `
      <img src="${channel.logo}" alt="${channel.title}" class="channel-logo">
      <div class="channel-title">${channel.title}</div>
    `;
    div.addEventListener("click", () => playChannel(channel.src, channel.type));
    channelsContainer.appendChild(div);
  });
}

// Play selected channel
function playChannel(src, type) {
  errorMessage.textContent = "";
  if (Hls.isSupported() && type === "hls") {
    const hls = new Hls();
    hls.loadSource(src);
    hls.attachMedia(video);
    hls.on(Hls.Events.ERROR, (event, data) => {
      errorMessage.textContent = "Error playing stream.";
    });
  } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
    video.src = src;
  } else {
    errorMessage.textContent = "HLS not supported on this browser.";
  }
}

// Search Functionality
searchInput.addEventListener("input", (e) => {
  const query = e.target.value.toLowerCase();
  const filtered = channels.filter(ch => ch.title.toLowerCase().includes(query));
  renderChannels(filtered);
});
