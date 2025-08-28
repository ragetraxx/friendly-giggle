async function loadChannels() {
  try {
    const res = await fetch("channels.json");
    const channels = await res.json();
    renderChannelList(channels);
  } catch (err) {
    console.error("Failed to load channels.json:", err);
    document.getElementById("status").textContent = "Error loading channels.json";
  }
}

function renderChannelList(channels) {
  const list = document.getElementById("channelList");
  list.innerHTML = "";

  channels.forEach((ch, i) => {
    const li = document.createElement("li");
    li.className = "channel-item";
    li.innerHTML = `
      <img src="${ch.logo}" alt="${ch.title}" />
      <span>${ch.title}</span>
    `;
    li.addEventListener("click", () => playChannel(ch));
    list.appendChild(li);

    if (i === 0) playChannel(ch); // auto-play first channel
  });
}

function playChannel(ch) {
  const video = document.getElementById("video");
  const nowTitle = document.getElementById("nowTitle");
  const nowLogo = document.getElementById("nowLogo");
  const status = document.getElementById("status");

  nowTitle.textContent = ch.title;
  nowLogo.src = ch.logo;
  status.textContent = "Loading " + ch.title + "...";

  if (ch.type === "hls" && Hls.isSupported()) {
    const hls = new Hls({ debug: true });
    hls.loadSource(ch.src);
    hls.attachMedia(video);

    hls.on(Hls.Events.MANIFEST_PARSED, () => {
      video.play().catch(err => console.error("Autoplay failed:", err));
    });

    hls.on(Hls.Events.ERROR, (event, data) => {
      console.error("HLS error:", data);
      status.textContent = "Playback error (" + data.type + ")";
    });

  } else if (ch.type === "dash" && typeof dashjs !== "undefined") {
    const player = dashjs.MediaPlayer().create();
    player.initialize(video, ch.src, true);

  } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
    video.src = ch.src;
    video.play();

  } else {
    console.error("Stream not supported:", ch);
    status.textContent = "Stream not supported";
  }
}

document.addEventListener("DOMContentLoaded", loadChannels);
