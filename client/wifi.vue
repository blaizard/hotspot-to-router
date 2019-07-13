<template>
    <Module class="wifi" :icon="icon" :title="title">
        <template v-slot:body="{ close }">
            <div v-if="stateInput">
                <div>Password: <input type="password" ref="password"/></div>
                <div><button @click="handleNetworkConnect(needInput, close, $refs.password.value)">Connect</button></div>
            </div>
            <!-- <div v-else-if="stateLoading" class="module-body-list">Scanning...</div> //-->
            <div v-else-if="stateError" class="module-body-list">Error: {{ error }}</div>
            <template v-else-if="stateData">
                <div v-for="network in networkList" class="module-body-list" @click="handleNetworkConnect(network, close)">
                    <span :class="getNetworkIcon(network)"></span> {{ network.ssid }}
                </div>
            </template>
            <div v-else class="module-body-list">No Network</div>
        </template>
	</Module>
</template>

<script>
	"use strict"

    import Module from "./module.vue";
    import Utility from "./utility.js";

	export default {
		data: function() {
			return {
                networkList: [],
                loading: false,
                title: "wifi",
                icon: "icon-wifi-0",
                error: null,
                needInput: false
            };
		},
        components: {
            Module
        },
        mounted() {
            this.fetchNetworkList();
        },
		computed: {
            stateInput() {
                return this.needInput;
            },
            stateLoading() {
                return this.loading;
            },
            stateError() {
                return this.error;
            },
            stateData() {
                return !this.stateError && (this.networkList.length > 0);
            },
            current() {
                if (this.stateData) {
                    for (const i in this.networkList) {
                        if (this.networkList[i].inUse) {
                            return this.networkList;
                        }
                    }
                }
                return null;
            }
		},
        methods: {
            getNetworkIcon(network) {
                let signalClass = "icon-wifi-0";
                if (network.signal > 85) {
                    signalClass = "icon-wifi-100";
                }
                else if (network.signal > 60) {
                    signalClass = "icon-wifi-75";
                }
                else if (network.signal > 35) {
                    signalClass = "icon-wifi-50";
                }
                else if (network.signal > 10) {
                    signalClass = "icon-wifi-25";
                }
                return signalClass;
            },
            async fetchNetworkList() {
                this.loading = true;
                try {
                    const networkList = await Utility.fetch("/api/v1/wifi/list", {}, "json");
                    const timestamp = Date.now();

                    // Merge with current networkList
                    networkList.forEach((network) => {
                        network.timestamp = timestamp;
                        let value = this.networkList.find((item) => item.ssid == network.ssid);
                        if (value) {
                            Object.assign(value, network);
                        }
                        else {
                            this.networkList.push(network);
                        }
                    });

                    // Keep only networks that have been discovered less than 1min ago
                    this.networkList = this.networkList.filter((network) => ((timestamp - network.timestamp) < 60 * 1000));

                    this.networkList.forEach((network) => {
                        if (network.inUse) {
                            this.title = network.ssid;
                            this.icon = this.getNetworkIcon(network);
                        }
                    });

                    console.log(this.networkList);

                    this.error = null;
                }
                catch (e) {
                    this.error = e;
                }
                finally {
                    this.loading = false;
                    setTimeout(this.fetchNetworkList, 10 * 1000);
                }
            },
            async handleNetworkConnect(network, close, password = null) {
                if (network.security.length > 0 && password === null) {
                    this.needInput = network;
                }
                else {
                    this.needInput = false;
                    close();
                    try {
                        let query = {
                            ssid: network.ssid
                        };
                        if (password) {
                            query.password = password;
                        }
                        await Utility.fetch("/api/v1/wifi/connect", query);
                        await Utility.fetch("/api/v1/proxy/goto", {
                            url: "http://www.example.com"
                        });
                    }
                    finally {
                        await this.fetchNetworkList();
                    }
                }
            }
        }
    }
</script>

<style lang="scss">
    .wifi {
    }
</style>
