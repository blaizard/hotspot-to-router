<template>
	<div class="wifi">
        <div class="wifi-status">Wifi</div>
        <div class="wifi-menu">
            <div v-if="stateLoading" class="wifi-menu-element">Scanning...</div>
            <div v-else-if="stateError" class="wifi-menu-element">Error: {{ error }}</div>
            <template v-else-if="stateData">
                <div v-for="network in networkList" class="wifi-menu-element">
                    {{ network.ssid }}
                </div>
            </template>
            <div v-else class="wifi-menu-element">No Network</div>
        </div>
	</div>
</template>

<script>
	"use strict"

	export default {
		data: function() {
			return {
                networkList: [],
                loading: false,
                error: null
            };
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
            fetchNetworkList() {
                this.loading = true;
                this.error = null;
				fetch("/api/v1/wifi/list").then((data) => {
					return data.json();
				}).then((data) => {
					this.networkList = data;
				}).catch((e) => {
                    this.error = e;
                }).finally(() => {
                    this.loading = false;
                });
            }
        }
    }
</script>

<style lang="scss">
	@import "[client]/style/config.scss";

    .wifi {
        position: relative;

        .wifi-status {
            width: #{$client-menu-height}px;
            height: #{$client-menu-height}px;
            line-height: #{$client-menu-height}px;
            padding: 0 10px;
        }
        .wifi-menu {
            position: absolute;

            top: #{$client-menu-height}px;
            right: 0;

            .wifi-menu-element {
                padding: 4px 10px;
                white-space: nowrap;
            }
        }
    }
</style>
