async function loadChannels() {
  const res = await fetch("channels.json");
  const channels = await res.json();
  const list = document.getElementById("channelList");
  list.innerHTML = "";

  channels.forEach((ch) => {
    const li = document.createElement("li");
    li.innerHTML = `<img src="${ch.logo}" alt=""> <span>${ch.title}</span>`;
    li.onclick = () => playChannel(ch);
    list.appendChild(li);
  });
}

function playChannel(channel) {
  const video = document.getElementById("video");
  const title = document.getElementById("nowTitle");
  const logo = document.getElementById("nowLogo");

  title.textContent = channel.title;
  logo.src = channel.logo;

  // Proxy the stream through Vercel
  const proxiedUrl = `/api/proxy?url=${encodeURIComponent(channel.src)}`;

  if (Hls.isSupported()) {
    const hls = new Hls();
    hls.loadSource(proxiedUrl);
    hls.attachMedia(video);
  } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
    video.src = proxiedUrl;
  }
}

document.addEventListener("DOMContentLoaded", loadChannels);
