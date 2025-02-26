const video = document.getElementById('video');
const channelSelect = document.getElementById('channelSelect');
const player = new shaka.Player(video);

// Channel List with DRM Configuration
const channels = [
    { name: "One News", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/oneph_sd.mpd", keyId: "92834ab4a7e1499b90886c5d49220e46", key: "a7108d9a6cfcc1b7939eb111daf09ab3" },
    { name: "PTV Four", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/cg_ptv4_sd.mpd", keyId: "71a130a851b9484bb47141c8966fb4a3", key: "ad1f003b4f0b31b75ea4593844435600" },
    { name: "TV5", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/tv5_hd.mpd", keyId: "2615129ef2c846a9bbd43a641c7303ef", key: "07c7f996b1734ea288641a68e1cfdc4d" },
    { name: "Kapamilya Channel", url: "https://d1uf7s78uqso1e.cloudfront.net/out/v1/efa01372657648be830e7c23ff68bea2/index.mpd", keyId: "bd17afb5dc9648a39be79ee3634dd4b8", key: "3ecf305d54a7729299b93a3d69c02ea5" },
    { name: "GMA", url: "http://143.44.136.111:6910/001/2/ch00000090990000001093/manifest.mpd?virtualDomain=001.live_hls.zte.com", license: "http://143.44.136.74:9443/widevine/?deviceId=02:00:00:00:00:00" },
    { name: "GTV", url: "http://143.44.136.113:6910/001/2/ch00000090990000001143/manifest.mpd?virtualDomain=001.live_hls.zte.com", license: "http://143.44.136.74:9443/widevine/?deviceId=02:00:00:00:00:00" }
];

// Populate the Dropdown Menu
function populateDropdown() {
    channels.forEach((channel, index) => {
        let option = document.createElement("option");
        option.value = index;
        option.textContent = channel.name;
        channelSelect.appendChild(option);
    });
}

// Load and Play Selected Channel
async function loadChannel(index) {
    const { name, url, keyId, key, license } = channels[index];

    console.log(`Loading channel: ${name}`);
    console.log(`Manifest URL: ${url}`);
    if (license) console.log(`License URL: ${license}`);

    try {
        let config = {};

        // Configure Clear Keys DRM
        if (keyId && key) {
            config.drm = { clearKeys: { [keyId]: key } };
        }

        // Configure Widevine DRM
        if (license) {
            config.drm = {
                servers: { 'com.widevine.alpha': license }
            };
        }

        player.configure(config);
        await player.load(url);
        console.log(`Now Playing: ${name}`);
        channelSelect.value = index;
    } catch (e) {
        console.error(`Error loading channel: ${name}`);
        console.error(e);
        alert(`Failed to load ${name}. Check the console (F12) for details.`);
    }
}

// Handle Channel Selection
function selectChannel() {
    loadChannel(parseInt(channelSelect.value));
}

// Shaka Player Initialization with Debugging
shaka.polyfill.installAll();
populateDropdown();
loadChannel(0); // Load First Channel by Default

// Debugging: Listen for Player Errors
player.addEventListener('error', (event) => {
    console.error("Shaka Player Error:", event.detail);
    alert("Playback error. Check the console for details.");
});
