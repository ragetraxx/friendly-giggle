document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("video");
    const channelSelect = document.getElementById("channelSelect");
    const errorMessage = document.getElementById("errorMessage");
    const player = new shaka.Player(video);

    const channels = [
    { name: "MYX", url: "https://d24xfhmhdb6r0q.cloudfront.net/out/v1/e897a7b6414a46019818ee9f2c081c4f/index.mpd", keyId: "5ce1bc7f06b494c276252b4d13c90e51", key: "f40a52a3ac9b4702bdd5b735d910fd2f" },
    { name: "A2Z", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/cg_a2z.mpd", keyId: "f703e4c8ec9041eeb5028ab4248fa094", key: "c22f2162e176eee6273a5d0b68d19530" },
    { name: "Bilyonaryo Channel", url: "https://qp-pldt-live-grp-05-prod.akamaized.net/out/u/bilyonaryoch.mpd", keyId: "227ffaf09bec4a889e0e0988704d52a2", key: "b2d0dce5c486891997c1c92ddaca2cd2" },
    { name: "IBC 13", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/ibc13_sd_new.mpd", keyId: "16ecd238c0394592b8d3559c06b1faf5", key: "05b47ae3be1368912ebe28f87480fc84" },
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
    { name: "Animax", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/cg_animax_sd_new.mpd", keyId: "92032b0e41a543fb9830751273b8debd", key: "03f8b65e2af785b10d6634735dbe6c11" },
    { name: "Dreamworks", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/cg_dreamworks_hd1.mpd", keyId: "4ab9645a2a0a47edbd65e8479c2b9669", key: "8cb209f1828431ce9b50b593d1f44079" },
    { name: "Dreamworks Tagalog", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/cg_dreamworktag.mpd", keyId: "564b3b1c781043c19242c66e348699c5", key: "d3ad27d7fe1f14fb1a2cd5688549fbab" },
    { name: "Moonbug Kids", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/cg_moonbug_kids_sd.mpd", keyId: "0bf00921bec94a65a124fba1ef52b1cd", key: "0f1488487cbe05e2badc3db53ae0f29f" }, 
    { name: "Nickelodeon", url: "https://qp-pldt-live-grp-11-prod.akamaized.net/out/u/dr_nickelodeon.mpd", keyId: "9ce58f37576b416381b6514a809bfd8b", key: "f0fbb758cdeeaddfa3eae538856b4d72" },
    { name: "Nick Jr", url: "https://qp-pldt-live-grp-12-prod.akamaized.net/out/u/dr_nickjr.mpd", keyId: "bab5c11178b646749fbae87962bf5113", key: "0ac679aad3b9d619ac39ad634ec76bc8" },
    { name: "Cartoon Network", url: "https://qp-pldt-live-grp-12-prod.akamaized.net/out/u/dr_cartoonnetworkhd.mpd", keyId: "a2d1f552ff9541558b3296b5a932136b", key: "cdd48fa884dc0c3a3f85aeebca13d444" },
    { name: "Knowledge Channel", url: "https://qp-pldt-live-grp-13-prod.akamaized.net/out/u/dr_knowledgechannel.mpd", keyId: "0f856fa0412b11edb8780242ac120002", key: "783374273ef97ad3bc992c1d63e091e7" },
    { name: "Buko", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/cg_buko_sd.mpd", keyId: "d273c085f2ab4a248e7bfc375229007d", key: "7932354c3a84f7fc1b80efa6bcea0615" },
    { name: "Sari-Sari", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/cg_sari_sari_sd.mpd", keyId: "0a7ab3612f434335aa6e895016d8cd2d", key: "b21654621230ae21714a5cab52daeb9d" },
    { name: "DepEd Channel", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/depedch_sd.mpd", keyId: "0f853706412b11edb8780242ac120002", key: "2157d6529d80a760f60a8b5350dbc4df" }, 
    { name: "TVN Movies Pinoy", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/cg_tvnmovie.mpd", keyId: "2e53f8d8a5e94bca8f9a1e16ce67df33", key: "3471b2464b5c7b033a03bb8307d9fa35" },
    { name: "PBO", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/pbo_sd.mpd", keyId: "dcbdaaa6662d4188bdf97f9f0ca5e830", key: "31e752b441bd2972f2b98a4b1bc1c7a1" },
    { name: "VIVA Cinema", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/viva_sd.mpd", keyId: "07aa813bf2c147748046edd930f7736e", key: "3bd6688b8b44e96201e753224adfc8fb" },
    { name: "CNN International", url: "https://qp-pldt-live-grp-12-prod.akamaized.net/out/u/dr_cnnhd.mpd", keyId: "900c43f0e02742dd854148b7a75abbec", key: "da315cca7f2902b4de23199718ed7e90" },
    { name: "CNA", url: "https://qp-pldt-live-grp-13-prod.akamaized.net/out/u/dr_channelnewsasia.mpd", keyId: "b259df9987364dd3b778aa5d42cb9acd", key: "753e3dba96ab467e468269e7e33fb813" },
    { name: "BBC World News", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/bbcworld_news_sd.mpd", keyId: "f59650be475e4c34a844d4e2062f71f3", key: "119639e849ddee96c4cec2f2b6b09b40" },
    { name: "Disovery Channel", url: "https://qp-pldt-live-grp-13-prod.akamaized.net/out/u/dr_discovery.mpd", keyId: "d9ac48f5131641a789328257e778ad3a", key: "b6e67c37239901980c6e37e0607ceee6" },
    { name: "History Channel", url: "https://qp-pldt-live-grp-11-prod.akamaized.net/out/u/dr_historyhd.mpd", keyId: "a7724b7ca2604c33bb2e963a0319968a", key: "6f97e3e2eb2bade626e0281ec01d3675" }, 
    { name: "HGTV", url: "https://qp-pldt-live-grp-08-prod.akamaized.net/out/u/hgtv_hd1.mpd", keyId: "f0e3ab943318471abc8b47027f384f5a", key: "13802a79b19cc3485d2257165a7ef62a" },
    { name: "Food Network", url: "https://qp-pldt-live-grp-09-prod.akamaized.net/out/u/cg_foodnetwork_hd1.mpd", keyId: "b7299ea0af8945479cd2f287ee7d530e", key: "b8ae7679cf18e7261303313b18ba7a14" },
    { name: "Asian Food Network", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/asianfoodnetwork_sd.mpd", keyId: "1619db30b9ed42019abb760a0a3b5e7f", key: "5921e47fb290ae263291b851c0b4b6e4" },
    { name: "TMC", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/cg_tagalogmovie.mpd", keyId: "96701d297d1241e492d41c397631d857", key: "ca2931211c1a261f082a3a2c4fd9f91b" },     
    { name: "HBO", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/cg_hbohd.mpd", keyId: "d47ebabf7a21430b83a8c4b82d9ef6b1", key: "54c213b2b5f885f1e0290ee4131d425b" },
    { name: "HBO Hits", url: "https://qp-pldt-live-grp-09-prod.akamaized.net/out/u/cg_hbohits.mpd", keyId: "b04ae8017b5b4601a5a0c9060f6d5b7d", key: "a8795f3bdb8a4778b7e888ee484cc7a1" },
    { name: "HBO Family", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/cg_hbofam.mpd", keyId: "872910c843294319800d85f9a0940607", key: "f79fd895b79c590708cf5e8b5c6263be" },
    { name: "HBO Signature", url: "https://qp-pldt-live-grp-01-prod.akamaized.net/out/u/cg_hbosign.mpd", keyId: "a06ca6c275744151895762e0346380f5", key: "559da1b63eec77b5a942018f14d3f56f" },
    { name: "Cinemax", url: "https://qp-pldt-live-grp-01-prod.akamaized.net/out/u/cg_cinemax.mpd", keyId: "b207c44332844523a3a3b0469e5652d7", key: "fe71aea346db08f8c6fbf0592209f955" }, 
    { name: "Tap Movies", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/cg_tapmovies_hd1.mpd", keyId: "71cbdf02b595468bb77398222e1ade09", key: "c3f2aa420b8908ab8761571c01899460" },  
    { name: "Thrill", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/cg_thrill_sd.mpd", keyId: "928114ffb2394d14b5585258f70ed183", key: "a82edc340bc73447bac16cdfed0a4c62" },  
    { name: "Hits Movies", url: "https://qp-pldt-live-grp-12-prod.akamaized.net/out/u/dr_hitsmovies.mpd", keyId: "f56b57b32d7e4b2cb21748c0b56761a7", key: "3df06a89aa01b32655a77d93e09e266f" },  
    { name: "Tap ActionFlix", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/cg_tapactionflix_hd1.mpd", keyId: "bee1066160c0424696d9bf99ca0645e3", key: "f5b72bf3b89b9848de5616f37de040b7" },  
    { name: "Tap Sports", url: "https://qp-pldt-live-grp-11-prod.akamaized.net/out/u/dr_tapsports.mpd", keyId: "eabd2d95c89e42f2b0b0b40ce4179ea0", key: "0e7e35a07e2c12822316c0dc4873903f" },
    { name: "Warner TV", url: "https://qp-pldt-live-grp-11-prod.akamaized.net/out/u/dr_warnertvhd.mpd", keyId: "4503cf86bca3494ab95a77ed913619a0", key: "afc9c8f627fb3fb255dee8e3b0fe1d71" },
    { name: "AXN", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/cg_axn_sd.mpd", keyId: "fd5d928f5d974ca4983f6e9295dfe410", key: "3aaa001ddc142fedbb9d5557be43792f" },
    { name: "Hits", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/hits_hd1.mpd", keyId: "dac605bc197e442c93f4f08595a95100", key: "975e27ffc1b7949721ee3ccb4b7fd3e5" },
    { name: "Hits Now", url: "https://qp-pldt-live-grp-09-prod.akamaized.net/out/u/cg_hitsnow.mpd", keyId: "14439a1b7afc4527bb0ebc51cf11cbc1", key: "92b0287c7042f271b266cc11ab7541f1" },
    { name: "Lifetime", url: "https://qp-pldt-live-grp-11-prod.akamaized.net/out/u/dr_lifetime.mpd", keyId: "cf861d26e7834166807c324d57df5119", key: "64a81e30f6e5b7547e3516bbf8c647d0" },
    { name: "TapTV", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/cg_taptv_sd.mpd", keyId: "f6804251e90b4966889b7df94fdc621e", key: "55c3c014f2bd12d6bd62349658f24566" },
    { name: "Rock Action", url: "https://qp-pldt-live-grp-13-prod.akamaized.net/out/u/dr_rockextreme.mpd", keyId: "0f852fb8412b11edb8780242ac120002", key: "4cbc004d8c444f9f996db42059ce8178" },
    { name: "Rock Entertainment", url: "https://qp-pldt-live-grp-13-prod.akamaized.net/out/u/dr_rockentertainment.mpd", keyId: "e4ee0cf8ca9746f99af402ca6eed8dc7", key: "be2a096403346bc1d0bb0f812822bb62" },
    { name: "Animal Planet", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/cg_animal_planet_sd.mpd", keyId: "436b69f987924fcbbc06d40a69c2799a", key: "c63d5b0d7e52335b61aeba4f6537d54d" },
    { name: "Travel Channel", url: "https://qp-pldt-live-grp-08-prod.akamaized.net/out/u/travel_channel_sd.mpd", keyId: "f3047fc13d454dacb6db4207ee79d3d3", key: "bdbd38748f51fc26932e96c9a2020839" },
    { name: "BBC Earth", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/cg_bbcearth_hd1.mpd", keyId: "34ce95b60c424e169619816c5181aded", key: "0e2a2117d705613542618f58bf26fc8e" },
    { name: "BBC Lifestyle", url: "https://qp-pldt-live-grp-09-prod.akamaized.net/out/u/cg_bbclifestyle.mpd", keyId: "34880f56627c11ee8c990242ac120002", key: "c23677c829bb244b79a3dc09ffd88ca0" },
    { name: "Bloomberg", url: "https://qp-pldt-live-grp-09-prod.akamaized.net/out/u/bloomberg_sd.mpd", keyId: "ef7d9dcfb99b406cb79fb9f675cba426", key: "b24094f6ca136af25600e44df5987af4" },
    { name: "ABC Australia", url: "https://qp-pldt-live-grp-10-prod.akamaized.net/out/u/dr_abc_aus.mpd", keyId: "389497f9f8584a57b234e27e430e04b7", key: "3b85594c7f88604adf004e45c03511c0" },
    { name: "Al Jazeera", url: "https://qp-pldt-live-grp-12-prod.akamaized.net/out/u/dr_aljazeera.mpd", keyId: "7f3d900a04d84492b31fe9f79ac614e3", key: "d33ff14f50beac42969385583294b8f2" },
    { name: "TVN Premium", url: "https://qp-pldt-live-grp-09-prod.akamaized.net/out/u/cg_tvnpre.mpd", keyId: "e1bde543e8a140b38d3f84ace746553e", key: "b712c4ec307300043333a6899a402c10" },
    { name: "Premier Sports 1", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/cg_ps_hd1.mpd", keyId: "b8b595299fdf41c1a3481fddeb0b55e4", key: "cd2b4ad0eb286239a4a022e6ca5fd007" },
    { name: "Premier Sports 2", url: "https://qp-pldt-live-grp-13-prod.akamaized.net/out/u/dr_premiertennishd.mpd", keyId: "59454adb530b4e0784eae62735f9d850", key: "61100d0b8c4dd13e4eb8b4851ba192cc" },
    { name: "Spotv", url: "https://qp-pldt-live-grp-11-prod.akamaized.net/out/u/dr_spotvhd.mpd", keyId: "ec7ee27d83764e4b845c48cca31c8eef", key: "9c0e4191203fccb0fde34ee29999129e" },
    { name: "Spotv 2", url: "https://qp-pldt-live-grp-13-prod.akamaized.net/out/u/dr_spotv2hd.mpd", keyId: "7eea72d6075245a99ee3255603d58853", key: "6848ef60575579bf4d415db1032153ed" },
    { name: "PPV HD", url: "https://qp-pldt-live-grp-05-prod.akamaized.net/out/u/cg_ppv_main_hd.mpd", keyId: "549ab7cd35a64bb6bb479ecead04d69d", key: "829799ed534d11fcadeb4b192467e050" },
    { name: "Pilipinas Live 1", url: "https://qp-pldt-live-grp-08-prod.akamaized.net/out/u/pl_sdi1.mpd", keyId: "a913faeecaac4813a55240bea0c68858", key: "05b7d7eaba8d6410dbe234336d9b235a" },
    { name: "Pilipinas Live 2", url: "https://qp-pldt-live-grp-02-prod.akamaized.net/out/u/pl_sdi2.mpd", keyId: "2f3056cac18d4e31a59de39767042b03", key: "83728946b898141ae411572f9f5fce0d" },
    { name: "Pilipinas Live 3", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/pl_sdi3.mpd", keyId: "0c16d5962a22494db502b3453f891208", key: "acaed175b981b34ae9b5cb0130506854" },
    { name: "Pilipinas Live 4", url: "https://qp-pldt-live-grp-06-prod.akamaized.net/out/u/pl_sdi4.mpd", keyId: "c3050cba95c945418efa3aedbc69cff7", key: "988e7fade0828273472e24545d0cfa4c" },
    { name: "Pilipinas Live 5", url: "https://qp-pldt-live-grp-08-prod.akamaized.net/out/u/pl_sdi5.mpd", keyId: "eecc6d7ac3df439fb2b73fb38007cb82", key: "826c341a6fef4518cefd27ec85e8b274" },
    { name: "Pilipinas Live 6", url: "https://qp-pldt-live-grp-08-prod.akamaized.net/out/u/pl_sdi6.mpd", keyId: "02d5f086706e407e9343c040ac7fb5b8", key: "9d7e088bf7fffc9297ab3a02f0ce9a72" },
    { name: "Pilipinas Live 7", url: "https://qp-pldt-live-grp-04-prod.akamaized.net/out/u/pl_sdi7.mpd", keyId: "40bed7f7948e4e5792982cf5b7ee4d78", key: "1fbfd2e3be51aae857f2f24306e5fc41" },
    { name: "Pilipinas Live 8", url: "https://qp-pldt-live-grp-03-prod.akamaized.net/out/u/pl_sdi8.mpd", keyId: "5a8dbf3b9c2c43079a40fb5d0068f9ef", key: "1778ac6e22527ee2efd6886d8d509c2d" },
    { name: "Pilipinas Live 9", url: "https://qp-pldt-live-grp-01-prod.akamaized.net/out/u/pl_sdi9.mpd", keyId: "1c7b9a2af9ad4076b155f06269b6adc2", key: "ed6a8b11738cd27c0bee2d9e3fee178a" },
    { name: "Pilipinas Live 10", url: "https://qp-pldt-live-grp-07-prod.akamaized.net/out/u/pl_sdi10.mpd", keyId: "63055a8904644407a64a57874703f71e", key: "0fd611777d37a7ff8afce19d9cee2e91" },
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
