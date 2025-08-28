document.addEventListener("DOMContentLoaded", function() {
    const video = document.getElementById("video");
    const channelList = document.getElementById("channelList");
    const errorMessage = document.getElementById("errorMessage");

    fetch("channels.json")
        .then(response => response.json())
        .then(channels => {
            channels.forEach((channel, index) => {
                const div = document.createElement("div");
                div.classList.add("channel-item");
                div.innerHTML = `
                    <img src="${channel.logo}" alt="${channel.title}">
                    <p>${channel.title}</p>
                `;
                div.addEventListener("click", () => {
                    playChannel(channel.src);
                });
                channelList.appendChild(div);
            });

            // Auto play the first channel
            if (channels.length > 0) {
                playChannel(channels[0].src);
            }
        })
        .catch(error => {
            errorMessage.textContent = "Error loading channels.";
            console.error(error);
        });

    function playChannel(src) {
        if (Hls.isSupported()) {
            const hls = new Hls();
            hls.loadSource(src);
            hls.attachMedia(video);
            hls.on(Hls.Events.ERROR, (event, data) => {
                console.error("HLS error:", data);
                errorMessage.textContent = "Error playing stream.";
            });
        } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
            video.src = src;
        } else {
            errorMessage.textContent = "Your browser does not support HLS playback.";
        }
    }
});
