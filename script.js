const video = document.getElementById('video');
const channelSelect = document.getElementById('channelSelect');
const player = new shaka.Player(video);

// Updated Channel List with BILYONARYO CHANNEL
const channels = [
    { name: "One News", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/oneph_sd.mpd", keyId: "92834ab4a7e1499b90886c5d49220e46", key: "a7108d9a6cfcc1b7939eb111daf09ab3" },
    { name: "PTV Four", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/cg_ptv4_sd.mpd", keyId: "71a130a851b9484bb47141c8966fb4a3", key: "ad1f003b4f0b31b75ea4593844435600" },
    { name: "TV5", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/tv5_hd.mpd", keyId: "2615129ef2c846a9bbd43a641c7303ef", key: "07c7f996b1734ea288641a68e1cfdc4d" },
    { name: "RPTV", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/cnn_rptv_prod_hd.mpd", keyId: "1917f4caf2364e6d9b1507326a85ead6", key: "a1340a251a5aa63a9b0ea5d9d7f67595" },
    { name: "IBC 13", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/ibc13_sd.mpd", keyId: "04e292bc99bd4ccba89e778651914254", key: "ff0a62bdf8920ce453fe680330b563a5" },
    { name: "TRUETV", url: "https://qp-pldt-live-grp-08-prod.akamaized.net/out/u/truefm_tv.mpd", keyId: "0559c95496d44fadb94105b9176c3579", key: "40d8bb2a46ffd03540e0c6210ece57ce" },
    { name: "A2Z", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/cg_a2z.mpd", keyId: "f703e4c8ec9041eeb5028ab4248fa094", key: "c22f2162e176eee6273a5d0b68d19530" },
    { name: "ONE News HD", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/onenews_hd1.mpd", keyId: "d39eb201ae494a0b98583df4d110e8dd", key: "6797066880d344422abd3f5eda41f45f" },
    { name: "NBA TV Philippines", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/pl_nba.mpd", keyId: "f36eed9e95f140fabbc88a08abbeafff", key: "0125600d0eb13359c28bdab4a2ebe75a" },
    { name: "PBA Rush", url: "https://qp-pldt-live-grp-01-prod.akamaized.net/out/u/cg_pbarush_hd1.mpd", keyId: "76dc29dd87a244aeab9e8b7c5da1e5f3", key: "95b2f2ffd4e14073620506213b62ac82" },
    { name: "One Sports", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/cg_onesports_hd.mpd", keyId: "53c3bf2eba574f639aa21f2d4409ff11", key: "3de28411cf08a64ea935b9578f6d0edd" },
    { name: "Kapamilya Channel", url: "https://d1uf7s78uqso1e.cloudfront.net/out/v1/efa01372657648be830e7c23ff68bea2/index.mpd", keyId: "bd17afb5dc9648a39be79ee3634dd4b8", key: "3ecf305d54a7729299b93a3d69c02ea5" },
    { name: "BILYONARYO CHANNEL", url: "https://qp-pldt-live-grp-05-prod.akamaized.net/out/u/bilyonaryoch.mpd", keyId: "227ffaf09bec4a889e0e0988704d52a2", key: "b2d0dce5c486891997c1c92ddaca2cd2" }
];

function populateDropdown() {
    channels.forEach((channel, index) => {
        let option = document.createElement("option");
        option.value = index;
        option.textContent = channel.name;
        channelSelect.appendChild(option);
    });
}

async function loadChannel(index) {
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

function selectChannel() {
    loadChannel(parseInt(channelSelect.value));
}

shaka.polyfill.installAll();
populateDropdown();
loadChannel(0);
