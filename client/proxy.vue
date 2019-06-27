<template>
    <div class="proxy">
        <div class="proxy-toolbar">
            <input class="proxy-toolbar-url" ref="url" type="text" placeholder="Type url here..." @change="handleUrlChange" />
            <input class="proxy-toolbar-send" type="button" value="OK" @click="handleUrlChange" />
        </div>
        <div class="proxy-wrapper" ref="container">
	        <img class="proxy-screen" ref="screen" tabindex="0" :src="image.src" @click="handleClick($event)" @keydown="handleKeydown($event)" />
        </div>
    </div>
</template>

<script>
	"use strict"

    import Url from "url";

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
                const rect = this.$refs.container.getBoundingClientRect();
                image.src = "/api/v1/proxy/screenshot?uid=" + (Date.now()) + "&width=" + rect.width + "&height=" + rect.height;
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
            handleKeydown(e) {
                console.log(e.key, e);
                this.fetch("press", {
                    key: String(e.key)
                });
            },
            cleanUrl(url) {
                let parsedUrl = Url.parse(url);
                parsedUrl.protocol = parsedUrl.protocol || "http";
                parsedUrl.slashes = parsedUrl.slashes || "//";
                delete parsedUrl.path;
                delete parsedUrl.href;

                let pathnameList = parsedUrl.pathname.split("/").filter((entry) => Boolean(entry));
                if (!parsedUrl.hostname) {
                    parsedUrl.hostname = pathnameList.shift();
                }
                parsedUrl.pathname = pathnameList.join("/");

                return Url.format(parsedUrl);
            },
            handleUrlChange() {
                const url = this.cleanUrl(this.$refs.url.value);
                this.$refs.url.value = url;
                this.fetch("goto", {
                    url: url
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

            .proxy-toolbar-url,
            .proxy-toolbar-send {
                border: 1px solid #777;
                padding: 5px 10px;
                line-height: 18px;
                font-size: 18px;
            }
        }

        .proxy-wrapper {

            margin: 0;
            padding: 0;
            border: none;
            width: 100%;
            height: calc(100% - 48px);
            overflow: hidden;

            .proxy-screen {
                margin: 0;
                padding: 0;
                border: none;
            }
        }
    }
</style>
