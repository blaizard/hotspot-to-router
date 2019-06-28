<template>
    <div class="proxy">
        <div class="proxy-tabs">
            <div v-for="tab, index in tabList" :class="getProxyTabClass(index)" @click="selectPage(index)">{{ tab || "No title" }}</div>
        </div>
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
                timeoutScreenshot: null,
                timeoutStatus: null,
                tabList: [],
                tabIndex: 0
            };
		},
        mounted() {
            this.startMonitoring();
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
            startMonitoring() {
                this.fetchStatus();
                this.fetchScreenshot();
            },
            getProxyTabClass(index) {
                return {
                    "proxy-tab": true,
                    "proxy-tab-active": (this.tabIndex == index)
                }
            },
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
                    return response;
                }
                catch (e) {
                    this.$emit("error", e);
                }
            },
            async fetchStatus() {
                clearTimeout(this.timeoutStatus);
                const response = await this.fetch("status");
                try {
                    const status = await response.json();
                    // Only update if it does not have the focus
                    if (document.activeElement !== this.$refs.url) {
                        this.$refs.url.value = status.url;
                    }
                    this.tabList = status.pages;
                    this.tabIndex = status.index;
                    this.timeoutStatus = setTimeout(this.fetchStatus, 1000);
                }
                catch (e) {
                    this.$emit("error", e);
                }
            },
            fetchScreenshot() {
                clearTimeout(this.timeoutScreenshot);
                let image = new Image();
                const rect = this.$refs.container.getBoundingClientRect();
                image.src = "/api/v1/proxy/screenshot?uid=" + (Date.now()) + "&width=" + rect.width + "&height=" + rect.height;
                image.onload = () => {
                    this.image = image;
                    this.timeoutScreenshot = setTimeout(this.fetchScreenshot, this.refreshRateMs);
                }
            },
            getCoordinatesFromEvent(e) {
                const rect = this.$refs.screen.getBoundingClientRect();
                const coord = (e.touches && e.touches.length) ? {x: e.touches[0].pageX, y: e.touches[0].pageY} : {x: e.pageX, y: e.pageY};
                const scroll = {x: window.pageXOffset || document.documentElement.scrollLeft, y: window.pageYOffset || document.documentElement.scrollTop};

                return {
                    x: Math.round((coord.x - rect.x - scroll.x) * this.screenshotWidth / rect.width),
                    y: Math.round((coord.y - rect.y - scroll.y) * this.screenshotHeight / rect.height)
                };
            },
            handleClick(e) {
                const coord = this.getCoordinatesFromEvent(e);
                this.fetch("click", coord);
            },
            handleKeydown(e) {
                this.fetch("press", {
                    key: String(e.key)
                });
            },
            selectPage(index) {
                this.fetch("select", {
                    index: index
                });
            },
            cleanUrl(url) {
                let parsedUrl = Url.parse(url);
                parsedUrl.protocol = parsedUrl.protocol || "http";
                parsedUrl.slashes = parsedUrl.slashes || "//";
                delete parsedUrl.path;
                delete parsedUrl.href;

                let pathnameList = (parsedUrl.pathname || "").split("/").filter((entry) => Boolean(entry));
                if (!parsedUrl.hostname) {
                    parsedUrl.hostname = pathnameList.shift();
                }
                parsedUrl.pathname = pathnameList.join("/");

                return Url.format(parsedUrl);
            },
            async handleUrlChange() {
                const url = this.cleanUrl(this.$refs.url.value);
                this.$refs.url.value = url;
                await this.fetch("goto", {
                    url: url
                });
                this.startMonitoring();
            }
        }
	}
</script>

<style lang="scss">
    .proxy {
        margin: 0;
        padding: 0;
        border: none;

        .proxy-tabs {
            display: flex;
            flex-flow: row nowrap;

            .proxy-tab {
                border: 1px solid #777;
                border-bottom: none;
                padding: 5px 10px;
                line-height: 18px;
                font-size: 18px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
                color: #999;
                cursor: pointer;

                &.proxy-tab-active {
                    color: #000;
                }
            }
        }

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
            height: calc(100% - 64px);
            overflow: hidden;

            .proxy-screen {
                margin: 0;
                padding: 0;
                border: none;
            }
        }
    }
</style>
