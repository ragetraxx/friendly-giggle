const video = document.getElementById('videoPlayer');
const errorMessage = document.getElementById('errorMessage');
const channelList = document.getElementById('channelList');
let hls;

async function loadChannels() {
    try {
        const response = await fetch('channels.json');
        const channels = await response.json();
        renderChannels(channels);
        if (channels.length > 0) {
            playStream(channels[0].src); // Auto play first channel
        }
    } catch (error) {
        errorMessage.textContent = "Failed to load channels.";
    }
}

function renderChannels(channels) {
    channelList.innerHTML = '';
    channels.forEach(channel => {
        const div = document.createElement('div');
        div.className = 'channel';
        div.innerHTML = `
            <img src="${channel.logo}" alt="${channel.title}">
            <div class="channel-title">${channel.title}</div>
        `;
        div.addEventListener('click', () => playStream(channel.src));
        channelList.appendChild(div);
    });
}

function playStream(url) {
    if (hls) {
        hls.destroy();
    }
    if (Hls.isSupported()) {
        hls = new Hls();
        hls.loadSource(url);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function () {
            video.play();
        });
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = url;
        video.play();
    } else {
        errorMessage.textContent = "Your browser does not support HLS streaming.";
    }
}

loadChannels();
