document.addEventListener("DOMContentLoaded", async () => {
    const videoElement = document.getElementById("videoPlayer");
    const videoTitleElement = document.getElementById("videoTitle");
    const prevButton = document.getElementById("prevButton");
    const nextButton = document.getElementById("nextButton");
    const videoSelect = document.getElementById("videoSelect");

    let currentIndex = 0;
    let player;

    const videoSources = [
        { title: "Cracked", url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P02029_FF_FM_CRACKED/dash/hd.mpd", key: { keys: { "d4cdc45e32f4272bea5aac2cf4f47419": "1c4878a93b13dec518e98240baeeacb2" } } },
        { title: "Peninsula", url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P01241_FF_FM_PENINSULA/dash/hd.mpd", key: { keys: { "54c20cfed8345010bcb8fea65bfbb666": "e810f257c044656bc5e5b0b45b45e89f" } } },
        { title: "Parasite", url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P00709_FF_FM_PARASITE/dash/hd.mpd", key: { keys: { "89bc7e0b6f1487bf3532ac53b8fc31a1": "ad6b84cdccf82683a50ff49927f82dd2" } } }
    ];

    async function initializeShakaPlayer() {
        if (!shaka.Player.isBrowserSupported()) {
            console.error("Shaka Player is not supported on this browser.");
            return;
        }

        player = new shaka.Player(videoElement);
    }

    async function loadVideo(index) {
        currentIndex = index;
        const selectedVideo = videoSources[index];

        if (!player) {
            console.error("Shaka Player is not initialized.");
            return;
        }

        player.configure({ drm: { clearKeys: selectedVideo.key.keys } });

        try {
            await player.load(selectedVideo.url);
            console.log("Playing: " + selectedVideo.title);
            videoTitleElement.innerText = selectedVideo.title;
        } catch (error) {
            console.error("Error loading video", error);
        }
    }

    function nextVideo() {
        currentIndex = (currentIndex + 1) % videoSources.length;
        loadVideo(currentIndex);
    }

    function prevVideo() {
        currentIndex = (currentIndex - 1 + videoSources.length) % videoSources.length;
        loadVideo(currentIndex);
    }

    function selectVideo(event) {
        loadVideo(parseInt(event.target.value));
    }

    videoSources.forEach((video, index) => {
        const option = document.createElement("option");
        option.value = index;
        option.innerText = video.title;
        videoSelect.appendChild(option);
    });

    videoElement.addEventListener("ended", nextVideo);
    nextButton.addEventListener("click", nextVideo);
    prevButton.addEventListener("click", prevVideo);
    videoSelect.addEventListener("change", selectVideo);

    await initializeShakaPlayer();
    loadVideo(currentIndex);
});
