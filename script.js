document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("video");
  const channelSelect = document.getElementById("channelSelect");
  const errorMessage = document.getElementById("errorMessage");

  fetch("channels.json")
    .then(response => {
      if (!response.ok) {
        throw new Error(`Failed to load channels.json (${response.status})`);
      }
      return response.json();
    })
    .then(channels => {
      if (!Array.isArray(channels) || channels.length === 0) {
        throw new Error("No channels found in channels.json");
      }

      channels.forEach(channel => {
        const option = document.createElement("option");
        option.value = channel.src;
        option.textContent = channel.title;
        channelSelect.appendChild(option);
      });

      playChannel(channelSelect.value);

      channelSelect.addEventListener("change", () => {
        playChannel(channelSelect.value);
      });
    })
    .catch(error => {
      console.error(error);
      errorMessage.textContent = `Error loading channels: ${error.message}`;
    });

  function playChannel(url) {
    if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(url);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, function () {
        video.play();
      });
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = url;
      video.play();
    } else {
      errorMessage.textContent = "HLS is not supported in this browser.";
    }
  }
});
