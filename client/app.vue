<template>
	<div class="client-wrapper">
		<div class="client-menu">
			<Wifi class="client-menu-wifi"></Wifi>
		</div>
		<div class="client-body">
		</div>
	</div>
</template>

<script>
	"use strict"

	import Wifi from "./wifi.vue";

	export default {
		components: {
			Wifi
		},
		data: function() {
			return {};
		},
		computed: {
		}
	}
</script>

<style lang="scss">
	@import "[client]/style/style.scss";
	@import "[client]/style/config.scss";

	.client-wrapper {
		width: 100%;
		height: 100%;
		margin: 0;
		padding: 0;

		.client-menu {
			width: 100%;
			height: #{$client-menu-height}px;
			background-color: #eee;

			.client-menu-wifi {
				float: right;
			}
		}

		.client-body {
			width: 100%;
			height: calc(100% - 64px);
		}
	}
</style>