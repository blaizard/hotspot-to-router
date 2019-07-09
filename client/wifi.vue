<template>
    <Module class="wifi" title="Wifi">
        <template v-slot:body="{ close }">
            <div v-if="stateLoading" class="module-body-list">Scanning...</div>
            <div v-else-if="stateError" class="module-body-list">Error: {{ error }}</div>
            <template v-else-if="stateData">
                <div v-for="network in networkList" class="module-body-list" @click="handleNetworkConnect(network, close)">
                    {{ network.ssid }}
                </div>
            </template>
            <div v-else class="module-body-list">No Network</div>
        </template>
	</Module>
</template>

<script>
	"use strict"

    import Module from "./module.vue";

	export default {
		data: function() {
			return {
                networkList: [],
                loading: false,
                error: null
            };
		},
        components: {
            Module
        },
        mounted() {
            this.fetchNetworkList();
        },
		computed: {
            stateLoading() {
                return this.loading;
            },
            stateError() {
                return this.error;
            },
            stateData() {
                return !this.loading && !this.stateError && (this.networkList.length > 0);
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
            fetch(api, args = {}) {
                return new Promise((resolve, reject) => {
                    const query = Object.keys(args).map((key) => key + "=" + encodeURIComponent(args[key])).join("&");
                    const url = api + ((query) ? ("?" + query) : "");
                    fetch(url).then((data) => {
                        return data.json();
                    }).then((data) => {
                        resolve(data);
                    }).catch((e) => {
                        reject(e);
                    });
                });
            },
            async fetchNetworkList() {
                this.loading = true;
                this.error = null;
                try {
                    this.networkList = await this.fetch("/api/v1/wifi/list");
                }
                catch (e) {
                    this.error = e;
                }
                finally {
                    this.loading = false;
                }
            },
            async handleNetworkConnect(network, close) {
                close();
                await this.fetch("/api/v1/wifi/connect", {
                    ssid: network.ssid
                });
            }
        }
    }
</script>

<style lang="scss">
    .wifi {
    }
</style>
