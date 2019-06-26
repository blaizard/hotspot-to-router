<template>
    <div class="proxy">
        <div class="proxy-toolbar">
            <input class="proxy-toolbar-url" ref="url" type="text" @change="handleUrlChange" />
            <input class="proxy-toolbar-send" type="button" value="OK" @click="handleUrlChange" />
        </div>
	    <img class="proxy-screen" ref="screen" :src="image.src" @click="handleClick($event)" />
    </div>
</template>

<script>
	"use strict"

	export default {
		data: function() {
			return {
                refreshRateMs: 100,
                image: new Image(),
                timeout: null
            };
		},
        mounted() {
            this.fetchScreenshot();
        },
		computed: {
            screenshotWidth() {
                return this.image.width;
            },
            screenshotHeight() {
                return this.image.height;
            }
		},
        methods: {
            async fetch(action, args) {
                let argList = [];
                for (const key in args) {
                    argList.push(key + "=" + encodeURIComponent(args[key]));
                }

                try {
                    const response = await fetch("/api/v1/proxy/" + action + ((argList.length > 0) ? ("?" + argList.join("&")) : ""));
                    if (!response.ok) {
                        throw Error((await response.text()) || response.statusText);
                    }
                    await response.text();
                }
                catch (e) {
                    this.$emit("error", e);
                }
            },
            fetchScreenshot() {
                clearTimeout(this.timeout);
                let image = new Image();
                image.src = "/api/v1/proxy/screenshot?uid=" + (Date.now());
                image.onload = () => {
                    this.image = image;
                    this.timeout = setTimeout(this.fetchScreenshot, this.refreshRateMs);
                }
            },
            getCoordinatesFromEvent(e) {
                const rect = this.$refs.screen.getBoundingClientRect();
                const coord = (e.touches && e.touches.length) ? {x: e.touches[0].pageX, y: e.touches[0].pageY} : {x: e.pageX, y: e.pageY};

                return {
                    x: Math.round((coord.x - rect.x) * this.screenshotWidth / rect.width),
                    y: Math.round((coord.y - rect.y) * this.screenshotHeight / rect.height)
                };
            },
            handleClick(e) {
                const coord = this.getCoordinatesFromEvent(e);
                this.fetch("click", coord);
            },
            handleUrlChange() {
                this.fetch("goto", {
                    url: this.$refs.url.value
                });
            }
        }
	}
</script>

<style lang="scss">
    .proxy {
        margin: 0;
        padding: 0;
        border: none;

        .proxy-toolbar {
            display: flex;
            flex-flow: row nowrap;

            .proxy-toolbar-url {
                flex: 2;
            }
        }

        .proxy-screen {
            margin: 0;
            padding: 0;
            border: none;
            width: 100%;
        }
    }
</style>
