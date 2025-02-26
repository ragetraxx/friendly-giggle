document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("video");
    const channelSelect = document.getElementById("channelSelect");
    const errorMessage = document.getElementById("errorMessage");
    const player = new shaka.Player(video);

    const channels = [
    { name: "A2Z", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/cg_a2z.mpd", keyId: "f703e4c8ec9041eeb5028ab4248fa094", key: "c22f2162e176eee6273a5d0b68d19530" },
    { name: "Bilyonaryo Channel", url: "https://qp-pldt-live-grp-05-prod.akamaized.net/out/u/bilyonaryoch.mpd", keyId: "227ffaf09bec4a889e0e0988704d52a2", key: "b2d0dce5c486891997c1c92ddaca2cd2" },
    { name: "IBC 13", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/ibc13_sd.mpd", keyId: "04e292bc99bd4ccba89e778651914254", key: "ff0a62bdf8920ce453fe680330b563a5" },
    { name: "Kapamilya Channel", url: "https://d1uf7s78uqso1e.cloudfront.net/out/v1/efa01372657648be830e7c23ff68bea2/index.mpd", keyId: "bd17afb5dc9648a39be79ee3634dd4b8", key: "3ecf305d54a7729299b93a3d69c02ea5" },
    { name: "NBA TV Philippines", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/pl_nba.mpd", keyId: "f36eed9e95f140fabbc88a08abbeafff", key: "0125600d0eb13359c28bdab4a2ebe75a" },
    { name: "One PH", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/oneph_sd.mpd", keyId: "92834ab4a7e1499b90886c5d49220e46", key: "a7108d9a6cfcc1b7939eb111daf09ab3" },
    { name: "One News HD", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/onenews_hd1.mpd", keyId: "d39eb201ae494a0b98583df4d110e8dd", key: "6797066880d344422abd3f5eda41f45f" },
    { name: "One Sports", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/cg_onesports_hd.mpd", keyId: "53c3bf2eba574f639aa21f2d4409ff11", key: "3de28411cf08a64ea935b9578f6d0edd" },
    { name: "One Sports Plus", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/cg_onesportsplus_hd1.mpd", keyId: "322d06e9326f4753a7ec0908030c13d8", key: "1e3e0ca32d421fbfec86feced0efefda" },
    { name: "PBA Rush", url: "https://qp-pldt-live-grp-01-prod.akamaized.net/out/u/cg_pbarush_hd1.mpd", keyId: "76dc29dd87a244aeab9e8b7c5da1e5f3", key: "95b2f2ffd4e14073620506213b62ac82" },
    { name: "PTV Four", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/cg_ptv4_sd.mpd", keyId: "71a130a851b9484bb47141c8966fb4a3", key: "ad1f003b4f0b31b75ea4593844435600" },
    { name: "RPTV", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/cnn_rptv_prod_hd.mpd", keyId: "1917f4caf2364e6d9b1507326a85ead6", key: "a1340a251a5aa63a9b0ea5d9d7f67595" },
    { name: "TRUETV", url: "https://qp-pldt-live-grp-08-prod.akamaized.net/out/u/truefm_tv.mpd", keyId: "0559c95496d44fadb94105b9176c3579", key: "40d8bb2a46ffd03540e0c6210ece57ce" },
    { name: "TV5", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/tv5_hd.mpd", keyId: "2615129ef2c846a9bbd43a641c7303ef", key: "07c7f996b1734ea288641a68e1cfdc4d" },
    { name: "UAAP Varsity", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/cg_uaap_cplay_sd.mpd", keyId: "95588338ee37423e99358a6d431324b9", key: "6e0f50a12f36599a55073868f814e81e" },
    { name: "Knowledge Channel", url: "https://qp-pldt-live-grp-13-prod.akamaized.net/out/u/dr_knowledgechannel.mpd", keyId: "0f856fa0412b11edb8780242ac120002", key: "783374273ef97ad3bc992c1d63e091e7" },
    { name: "Buko", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/cg_buko_sd.mpd", keyId: "d273c085f2ab4a248e7bfc375229007d", key: "7932354c3a84f7fc1b80efa6bcea0615" },
    { name: "Sari-Sari", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/cg_sari_sari_sd.mpd", keyId: "0a7ab3612f434335aa6e895016d8cd2d", key: "b21654621230ae21714a5cab52daeb9d" },
    { name: "DepEd Channel", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/depedch_sd.mpd", keyId: "0f853706412b11edb8780242ac120002", key: "2157d6529d80a760f60a8b5350dbc4df" }, 
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
