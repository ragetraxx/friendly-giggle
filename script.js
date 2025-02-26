const video = document.getElementById('video');
const channelNameDisplay = document.getElementById('channel-name');
const player = new shaka.Player(video);

const channels = [
    { name: "One News", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/oneph_sd.mpd", keyId: "92834ab4a7e1499b90886c5d49220e46", key: "a7108d9a6cfcc1b7939eb111daf09ab3" },
    { name: "PTV Four", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/cg_ptv4_sd.mpd", keyId: "71a130a851b9484bb47141c8966fb4a3", key: "ad1f003b4f0b31b75ea4593844435600" },
    { name: "TV5", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/tv5_hd.mpd", keyId: "2615129ef2c846a9bbd43a641c7303ef", key: "07c7f996b1734ea288641a68e1cfdc4d" },
    { name: "RPTV", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/cnn_rptv_prod_hd.mpd", keyId: "1917f4caf2364e6d9b1507326a85ead6", key: "a1340a251a5aa63a9b0ea5d9d7f67595" },
    { name: "IBC 13", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/ibc13_sd.mpd", keyId: "04e292bc99bd4ccba89e778651914254", key: "ff0a62bdf8920ce453fe680330b563a5" },
    { name: "TRUETV", url: "https://qp-pldt-live-grp-08-prod.akamaized.net/out/u/truefm_tv.mpd", keyId: "0559c95496d44fadb94105b9176c3579", key: "40d8bb2a46ffd03540e0c6210ece57ce" },
    { name: "A2Z", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/cg_a2z.mpd", keyId: "f703e4c8ec9041eeb5028ab4248fa094", key: "c22f2162e176eee6273a5d0b68d19530" },
    { name: "ONE News HD", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/onenews_hd1.mpd", keyId: "d39eb201ae494a0b98583df4d110e8dd", key: "6797066880d344422abd3f5eda41f45f" }
];

let currentChannel = 0;
let fadeTimeout;

async function loadChannel(index) {
    if (index < 0 || index >= channels.length) return;

    currentChannel = index;
    const { name, url, keyId, key } = channels[currentChannel];

    try {
        player.configure({
            drm: {
                clearKeys: { [keyId]: key }
            }
        });

        await player.load(url);
        showChannelName(name);
        console.log(`Playing: ${name}`);
    } catch (e) {
        console.error('Error loading channel:', e);
    }
}

function nextChannel() {
    loadChannel((currentChannel + 1) % channels.length);
}

function prevChannel() {
    loadChannel((currentChannel - 1 + channels.length) % channels.length);
}

function showChannelName(name) {
    channelNameDisplay.textContent = name;
    channelNameDisplay.style.opacity = "1";
    clearTimeout(fadeTimeout);
    fadeTimeout = setTimeout(() => {
        channelNameDisplay.style.opacity = "0";
    }, 10000);
}

shaka.polyfill.installAll();
if (shaka.Player.isBrowserSupported()) {
    loadChannel(0);
} else {
    console.error('Shaka Player is not supported!');
}
