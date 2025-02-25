document.addEventListener("DOMContentLoaded", async () => {
    const videoElement = document.getElementById("videoPlayer");

    // List of 10 DRM-protected MPD videos with ClearKey
    const videoSources = [
        { url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P02029_FF_FM_CRACKED/dash/hd.mpd", key: { keys: { "d4cdc45e32f4272bea5aac2cf4f47419": "1c4878a93b13dec518e98240baeeacb2" } } },
        { url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P01241_FF_FM_PENINSULA/dash/hd.mpd", key: { keys: { "54c20cfed8345010bcb8fea65bfbb666": "e810f257c044656bc5e5b0b45b45e89f" } } },
        { url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P00709_FF_FM_PARASITE/dash/hd.mpd", key: { keys: { "89bc7e0b6f1487bf3532ac53b8fc31a1": "ad6b84cdccf82683a50ff49927f82dd2" } } },
        { url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P01441_FF_FM_THE%20MONKEY%20KING%20THE%20LEGEND%20BEGINS/dash/hd.mpd", key: { keys: { "80f68e3cbb240fe8056a634e1ae1fb56": "cd5a12ee719f7cef8bade6ed2b599ac7" } } },
        { url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P01442_FF_FM_THE%20MONKEY%20KING%202/dash/hd.mpd", key: { keys: { "0c44c55f19e144f4f1611b4066bcaa76": "41859ff109d02ea97fd1cd9546862f9b" } } },
        { url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P01234_FF_FM_ESCAPE%20FROM%20MOGADISHU/dash/hd.mpd", key: { keys: { "a47181615593db444b5043bcbcd0bf53": "47c3b5d32d917d61dc0aef32e2865422" } } },
        { url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P01183_FF_FM_DEW/dash/hd.mpd", key: { keys: { "5c51aae71898f4425f623ed17c57a63d": "a4c866083ad3275c1d282f5a3a8899d0" } } },
        { url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P02046_FF_FM_GET%20IN%20THE%20DARK/dash/hd.mpd", key: { keys: { "63554e0d61c329fd5cccd3684bdc0b98": "f5da35af531d662f63b304b8a541aaff" } } },
        { url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P02019_FF_FM_TALES%20FROM%20THE%20OCCULT/dash/hd.mpd", key: { keys: { "fda8dbdba913bfde36e4c7599c031a77": "2ece5d10bcec59b73f818fd79f45d59a" } } },
        { url: "https://d1qfpvemzhsbpm.cloudfront.net/video/P02149_FF_FM_THE%20NARROW%20ROAD/dash/hd.mpd", key: { keys: { "87921d7471e57c7f1f2049eb2f9427eb": "ace4e45cc71b37934e1e999bcf895834" } } }
    ];

    async function playRandomVideo() {
        const randomVideo = videoSources[Math.floor(Math.random() * videoSources.length)];

        if (!shaka.Player.isBrowserSupported()) {
            console.error("Shaka Player is not supported on this browser.");
            return;
        }

        const player = new shaka.Player(videoElement);

        player.configure({ drm: { clearKeys: randomVideo.key.keys } });

        try {
            await player.load(randomVideo.url);
            console.log("Playing: " + randomVideo.url);
        } catch (error) {
            console.error("Error loading video", error);
        }
    }

    videoElement.addEventListener("ended", playRandomVideo);

    await playRandomVideo();
});
