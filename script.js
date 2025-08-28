document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("videoPlayer");
    const channelList = document.getElementById("channelList");
    const errorMessage = document.getElementById("errorMessage");

    // Load channels from channels.json
    fetch("channels.json")
        .then(response => response.json())
        .then(channels => {
            renderChannels(channels);

            // Autoplay first channel
            if (channels.length > 0) {
                playChannel(channels[0].src);
            }
        })
        .catch(error => console.error("Error loading channels:", error));

    function renderChannels(channels) {
        channels.forEach(channel => {
            const div = document.createElement("div");
            div.className = "channel-item";
            div.innerHTML = `
                <img src="${channel.logo}" alt="${channel.title}">
                <p>${channel.title}</p>
            `;
            div.addEventListener("click", () => playChannel(channel.src));
            channelList.appendChild(div);
        });
    }

    function playChannel(url) {
        errorMessage.textContent = "";

        if (Hls.isSupported()) {
            const hls = new Hls();
            hls.loadSource(url);
            hls.attachMedia(video);
            hls.on(Hls.Events.ERROR, function (event, data) {
                console.error("HLS Error:", data);
                errorMessage.textContent = "Error loading stream.";
            });
        } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
            video.src = url;
        } else {
            errorMessage.textContent = "Your browser does not support HLS streaming.";
        }
    }
});
