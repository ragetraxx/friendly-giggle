document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("video");
    const channelSelect = document.getElementById("channelSelect");
    const player = new shaka.Player(video);

    const channels = [
        { name: "A2Z", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/cg_a2z.mpd", keyId: "f703e4c8ec9041eeb5028ab4248fa094", key: "c22f2162e176eee6273a5d0b68d19530" },
        { name: "Bilyonaryo Channel", url: "https://qp-pldt-live-grp-05-prod.akamaized.net/out/u/bilyonaryoch.mpd", keyId: "227ffaf09bec4a889e0e0988704d52a2", key: "b2d0dce5c486891997c1c92ddaca2cd2" },
        { name: "IBC 13", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/ibc13_sd.mpd", keyId: "04e292bc99bd4ccba89e778651914254", key: "ff0a62bdf8920ce453fe680330b563a5" },
        { name: "TVN Movies Pinoy", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/cg_tvnmovie.mpd", keyId: "2e53f8d8a5e94bca8f9a1e16ce67df33", key: "3471b2464b5c7b033a03bb8307d9fa35" },
        { name: "PBO", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/pbo_sd.mpd", keyId: "dcbdaaa6662d4188bdf97f9f0ca5e830", key: "31e752b441bd2972f2b98a4b1bc1c7a1" },
        { name: "VIVA Cinema", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/viva_sd.mpd", keyId: "07aa813bf2c147748046edd930f7736e", key: "3bd6688b8b44e96201e753224adfc8fb" },
        { name: "TMC", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/cg_tagalogmovie.mpd", keyId: "96701d297d1241e492d41c397631d857", key: "ca2931211c1a261f082a3a2c4fd9f91b" },
        { name: "HBO", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/cg_hbohd.mpd", keyId: "d47ebabf7a21430b83a8c4b82d9ef6b1", key: "54c213b2b5f885f1e0290ee4131d425b" },
        { name: "HBO Hits", url: "https://qp-pldt-live-grp-09-prod.akamaized.net/out/u/cg_hbohits.mpd", keyId: "b04ae8017b5b4601a5a0c9060f6d5b7d", key: "a8795f3bdb8a4778b7e888ee484cc7a1" },
        { name: "HBO Family", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/cg_hbofam.mpd", keyId: "872910c843294319800d85f9a0940607", key: "f79fd895b79c590708cf5e8b5c6263be" },
        { name: "HBO Signature", url: "https://qp-pldt-live-grp-01-prod.akamaized.net/out/u/cg_hbosign.mpd", keyId: "a06ca6c275744151895762e0346380f5", key: "559da1b63eec77b5a942018f14d3f56f" },
        { name: "Cinemax", url: "https://qp-pldt-live-grp-01-prod.akamaized.net/out/u/cg_cinemax.mpd", keyId: "b207c44332844523a3a3b0469e5652d7", key: "fe71aea346db08f8c6fbf0592209f955" }
    ];

    function populateDropdown() {
        channelSelect.innerHTML = "";
        channels.forEach((channel, index) => {
            let option = document.createElement("option");
            option.value = index;
            option.textContent = channel.name;
            channelSelect.appendChild(option);
        });
    }

    async function loadChannel(index) {
        if (index < 0 || index >= channels.length) return;

        const { name, url, keyId, key } = channels[index];

        try {
            player.configure({
                drm: { clearKeys: { [keyId]: key } }
            });

            await player.load(url);
            console.log(`Playing: ${name}`);
            channelSelect.value = index;
        } catch (e) {
            console.error('Error loading channel:', e);
        }
    }

    channelSelect.addEventListener("change", () => {
        loadChannel(parseInt(channelSelect.value));
    });

    shaka.polyfill.installAll();
    populateDropdown();
    loadChannel(0);
});
