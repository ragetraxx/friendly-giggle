let channels = [];
const videoElement = document.getElementById("video");
let player;

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const response = await fetch("./channels.json"); // load JSON
    channels = await response.json();
    renderChannels(channels);
    initPlayer();
    if (channels.length > 0) {
      loadChannel(channels[0]); // auto play first channel
    }
  } catch (err) {
    console.error("Error loading channels.json", err);
  }
});

// Initialize Shaka Player
function initPlayer() {
  shaka.polyfill.installAll();

  if (shaka.Player.isBrowserSupported()) {
    player = new shaka.Player(videoElement);
    player.addEventListener("error", onErrorEvent);
  } else {
    alert("Browser not supported!");
  }
}

// Load a channel
function loadChannel(channel) {
  if (!player) return;

  const clearkey = {};
  clearkey[channel.keyId] = channel.key;

  player.configure({
    drm: {
      clearKeys: clearkey
    }
  });

  player.load(channel.url).then(() => {
    console.log("Playing:", channel.name);
  }).catch(onError);
}

// Error handlers
function onErrorEvent(event) {
  onError(event.detail);
}
function onError(error) {
  console.error("Error code", error.code, "object", error);
}

// Render channel list
function renderChannels(channels) {
  const list = document.getElementById("channel-list");
  list.innerHTML = "";

  channels.forEach(channel => {
    const div = document.createElement("div");
    div.className = "channel";
    div.innerHTML = `
      <img src="${channel.logo}" alt="${channel.name}">
      <span>${channel.name}</span>
    `;
    div.addEventListener("click", () => loadChannel(channel));
    list.appendChild(div);
  });
}
