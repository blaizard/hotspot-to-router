<template>
	<div class="client-wrapper">
		<div class="client-menu">
			<Power class="client-menu-power" @error="handleError"></Power>
			<Temperature class="client-menu-temperature" @error="handleError"></Temperature>
			<Irapps class="client-menu-irapps" @error="handleError"></Irapps>
			<Wifi class="client-menu-wifi" @error="handleError"></Wifi>
		</div>
		<div class="client-body">
			<Proxy class="client-body-proxy" @error="handleError"></Proxy>
		</div>
		<Error class="client-error" :error="error"></Error>
	</div>
</template>

<script>
	"use strict"

	import Wifi from "./wifi.vue";
	import Temperature from "./temperature.vue";
	import Irapps from "./irapps.vue";
	import Power from "./power.vue";
	import Proxy from "./proxy.vue";
	import Error from "./error.vue";

	export default {
		components: {
			Wifi, Temperature, Irapps, Power, Proxy, Error
		},
		data: function() {
			return {
				error: null
			}
		},
		computed: {
		},
		methods: {
			handleError(e) {
				this.error = e;
			}
		}
	}
</script>

<style lang="scss">
	@import "[client]/style/style.scss";
	@import "[client]/style/config.scss";
	@import "[client]/style/icons.scss";

	html, body {
		width: 100%;
		height: 100%;
	}

	.client-wrapper {
		width: 100%;
		height: 100%;
		margin: 0;
		padding: 0;
		position: relative;

		.client-menu {
			width: 100%;
			height: #{$client-menu-height}px;
			color: $client-menu-color;
			background-color: $client-menu-background-color;

			.client-menu-power,
			.client-menu-temperature,
			.client-menu-irapp {
				float: left;
			}

			.client-menu-wifi {
				float: right;
			}
		}

		.client-body {
			width: 100%;
			height: calc(100% - 64px);

			.client-body-proxy {
				width: 100%;
				height: 100%;
			}
		}

		.client-error {
			position: absolute;
			bottom: 0;
			width: 100%;
		}
	}
</style>