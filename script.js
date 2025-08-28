const channelSelect = document.getElementById("channelSelect");
const video = document.getElementById("video");
const errorMessage = document.getElementById("errorMessage");

// Load channels from channels.json
fetch("channels.json")
  .then(response => response.json())
  .then(channels => {
    if (channels.length === 0) {
      errorMessage.textContent = "No channels available.";
      return;
    }

    // Populate select options
    channels.forEach((channel, index) => {
      const option = document.createElement("option");
      option.value = channel.src;
      option.textContent = channel.title;
      channelSelect.appendChild(option);
    });

    // Play first channel by default
    playChannel(channelSelect.value);

    // Change channel on selection
    channelSelect.addEventListener("change", () => {
      playChannel(channelSelect.value);
    });
  })
  .catch(error => {
    errorMessage.textContent = "Failed to load channels.";
    console.error(error);
  });

// Function to play HLS stream
function playChannel(src) {
  errorMessage.textContent = "";

  if (Hls.isSupported()) {
    const hls = new Hls();
    hls.loadSource(src);
    hls.attachMedia(video);
    hls.on(Hls.Events.ERROR, function(event, data) {
      errorMessage.textContent = "Error loading stream.";
      console.error(data);
    });
  } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
    video.src = src;
  } else {
    errorMessage.textContent = "Your browser does not support HLS.";
  }
}
