document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("video");
    const channelSelect = document.getElementById("channelSelect");
    const errorMessage = document.getElementById("errorMessage");
    const player = new shaka.Player(video);

    const channels = [
        { name: "Bilyonaryo Channel", url: "https://qp-pldt-live-grp-05-prod.akamaized.net/out/u/bilyonaryoch.mpd", keyId: "227ffaf09bec4a889e0e0988704d52a2", key: "b2d0dce5c486891997c1c92ddaca2cd2" },
        { name: "One Sports Plus", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/cg_onesportsplus_hd1.mpd", keyId: "322d06e9326f4753a7ec0908030c13d8", key: "1e3e0ca32d421fbfec86feced0efefda" },
        { name: "UAAP Varsity", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/cg_uaap_cplay_sd.mpd", keyId: "95588338ee37423e99358a6d431324b9", key: "6e0f50a12f36599a55073868f814e81e" },
        { name: "Knowledge Channel", url: "https://qp-pldt-live-grp-13-prod.akamaized.net/out/u/dr_knowledgechannel.mpd", keyId: "0f856fa0412b11edb8780242ac120002", key: "783374273ef97ad3bc992c1d63e091e7" }
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
            console.log(`Loading channel: ${name}`);
            errorMessage.textContent = "";

            player.configure({
                drm: {
                    clearKeys: {
                        [keyId]: key
                    }
                }
            });

            await player.load(url);
            console.log(`Now playing: ${name}`);
            channelSelect.value = index;
        } catch (e) {
            console.error(`Error loading ${name}:`, e);
            errorMessage.textContent = `Error loading ${name}. Please try another channel.`;
        }
    }

    channelSelect.addEventListener("change", () => {
        loadChannel(parseInt(channelSelect.value));
    });

    shaka.polyfill.installAll();
    populateDropdown();
    loadChannel(0); // Load first channel by default
});
