<template>
	<div class="irapps">
		<Module v-for="app, index in apps" :key="index" class="irapp" icon="icon-cli" :title="getTitle(app)" :onclick="handleClick">
            <template v-slot:body>
                <div>Up time: {{ Math.round(app.uptime) }}s</div>
                <div>Restared: {{ Math.round(app.restart) }}</div>
                <div>CPU: {{ Math.ceil(app.cpu) }}%</div>
                <div>Memory: {{ Math.ceil(app.memory / (1024 * 1024)) }}MB</div>
            </template>
		</Module>
	</div>
</template>

<script>
	"use strict"

    import Module from "./module.vue";
    import Utility from "./utility.js";

	export default {
		data: function() {
			return {
                utility: new Utility((e) => { this.$emit("error", e); }),
                apps: []
            };
		},
        components: {
            Module
        },
        mounted() {
            this.fetchStatus();
        },
        methods: {
            getTitle(app) {
                return app.id + " (" + Math.ceil(app.cpu) + "%)";
            },
            async fetchStatus() {
                try {
                    const status = await this.utility.fetch("/api/v1/apps/status", {}, "json");
                    this.apps = status.statusList;
                }
                finally {
                    setTimeout(this.fetchStatus, 2000);
                }
            },
            async handleClick() {
            }
        }
    }
</script>

<style lang="scss">
    .irapps {
        .irapp {
            float: left;
            .module-body {
                padding: 10px;
            }
        }
    }
</style>
