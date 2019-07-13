<template>
    <Module class="temperature" :icon="icon" :title="title">
	</Module>
</template>

<script>
	"use strict"

    import Module from "./module.vue";
    import Utility from "./utility.js";

	export default {
		data: function() {
			return {
                temperature: null,
                utility: new Utility((e) => { this.$emit("error", e); })
            };
		},
        components: {
            Module
        },
        mounted() {
            this.fetchTemperature();
        },
		computed: {
            icon() {
                return "icon-thermometer-100";
            },
			temperatureDegree() {
				return parseInt(this.temperature) || 0;
			},
			title() {
				return (this.temperatureDegree + "℃") || "-";
			}
		},
        methods: {
            async fetchTemperature() {
                try {
                    this.temperature = await this.utility.fetch("/api/v1/temperature/get");
                }
				catch(e) {
					// ignore
				}
                finally {
					setTimeout(this.fetchTemperature, 2000);
                }
            }
        }
    }
</script>

<style lang="scss">
    .temperature {
    }
</style>
