const channelSelect = document.getElementById('channelSelect');
const video = document.getElementById('video');
const errorMessage = document.getElementById('errorMessage');

async function loadChannels() {
  try {
    const response = await fetch('channels.json');
    const channels = await response.json();

    channels.forEach((channel, index) => {
      const option = document.createElement('option');
      option.value = index;
      option.textContent = channel.title;
      channelSelect.appendChild(option);
    });

    if (channels.length > 0) {
      playChannel(channels[0].src);
    }

    channelSelect.addEventListener('change', () => {
      const selectedChannel = channels[channelSelect.value];
      playChannel(selectedChannel.src);
    });
  } catch (error) {
    errorMessage.textContent = 'Failed to load channels.';
  }
}

function playChannel(src) {
  video.src = src;
  video.play().catch(err => {
    errorMessage.textContent = 'Tap play to start the video.';
  });
}

loadChannels();
