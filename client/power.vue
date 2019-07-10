<template>
    <Module class="power" icon="icon-power" :onclick="handleClick">
	</Module>
</template>

<script>
	"use strict"

    import Module from "./module.vue";
    import Utility from "./utility.js";

	export default {
		data: function() {
			return {
            };
		},
        components: {
            Module
        },
        methods: {
            async handleClick() {
                await Utility.fetch("/api/v1/proxy/reset");
				location.reload();
            }
        }
    }
</script>

<style lang="scss">
    .power {
    }
</style>
