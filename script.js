document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("video");
    const channelSelect = document.getElementById("channelSelect");
    const errorMessage = document.getElementById("errorMessage");

    let channels = [];
    let hls;

    async function loadChannels() {
        try {
            const response = await fetch("channels.json");
            if (!response.ok) throw new Error("Failed to load channels.json");
            channels = await response.json();
            populateDropdown();
            loadChannel(0); // Load first channel
        } catch (err) {
            console.error("Error fetching channels:", err);
            errorMessage.textContent = "Failed to load channel list.";
        }
    }

    function populateDropdown() {
        channelSelect.innerHTML = "";
        channels.forEach((channel, index) => {
            const option = document.createElement("option");
            option.value = index;
            option.textContent = channel.name;
            channelSelect.appendChild(option);
        });
    }

    function loadChannel(index) {
        if (index < 0 || index >= channels.length) return;

        const { name, url } = channels[index];
        errorMessage.textContent = "";

        if (hls) {
            hls.destroy();
            hls = null;
        }

        try {
            console.log(`Loading channel: ${name}`);
            if (video.canPlayType("application/vnd.apple.mpegurl")) {
                video.src = url; // Native support (Safari)
            } else if (Hls.isSupported()) {
                hls = new Hls();
                hls.loadSource(url);
                hls.attachMedia(video);
            } else {
                errorMessage.textContent = "HLS is not supported in this browser.";
            }
        } catch (e) {
            console.error(`Error loading ${name}:`, e);
            errorMessage.textContent = `Error loading ${name}. Please try another channel.`;
        }
    }

    channelSelect.addEventListener("change", () => {
        loadChannel(parseInt(channelSelect.value));
    });

    loadChannels();
});
