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
            <div class="proxy-overlay">
                <span v-if="loading">(loading...)</span>
                {{ frameRate }} FPS
            </div>
	        <img class="proxy-screen" ref="screen" tabindex="0" :src="image.src" @click="handleClick($event)" @keydown="handleKeydown($event)" />
        </div>
        <div class="proxy-scrollbar-vertical">
            <div class="proxy-cursor-up" @click="scrollVertical(-screenshotHeight / 5)"></div>
            <div class="proxy-cursor-down" @click="scrollVertical(screenshotHeight / 5)"></div>
        </div>
        <div class="proxy-scrollbar-horizontal">
            <div class="proxy-cursor-left" @click="scrollHorizontal(-screenshotWidth / 5)"></div>
            <div class="proxy-cursor-right" @click="scrollHorizontal(screenshotWidth / 5)"></div>
        </div>
    </div>
</template>

<script>
	"use strict"

    import Url from "url";
    import Utility from "./utility.js";

	export default {
		data: function() {
			return {
                statusRateMs: 1000,
                screenshotRateMs: 1000,
                image: new Image(),
                timeoutScreenshot: null,
                timeoutStatus: null,
                tabList: [],
                tabIndex: 0,
                loading: false,
                utility: new Utility((e) => { this.$emit("error", e) }),
                pageHeight: 0,
                pageWidth: 0,
                pageOffsetHeight: 0,
                pageOffsetWidth: 0
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
            },
            frameRate() {
                return parseInt(1000 / this.screenshotRateMs);
            }
		},
        methods: {
            startMonitoring() {
                this.pageOffsetHeight = 0;
                this.pageOffsetTop = 0;
                this.fetchStatus();
                this.fetchScreenshot();
            },
            getProxyTabClass(index) {
                return {
                    "proxy-tab": true,
                    "proxy-tab-active": (this.tabIndex == index)
                }
            },
            async fetchStatus() {
                clearTimeout(this.timeoutStatus);
                try {
                    const status = await this.utility.fetch("/api/v1/proxy/status", {}, "json");

                    if (status.status == "up") {
                        // Only update if it does not have the focus
                        if (document.activeElement !== this.$refs.url) {
                            this.$refs.url.value = status.url;
                        }
                        this.tabList = status.pages;
                        this.tabIndex = status.index;
                        this.pageHeight = status.height;
                        this.pageWidth = status.width;
                        this.loading = false;
                    }
                    else {
                        this.loading = true;
                    }

                    this.timeoutStatus = setTimeout(this.fetchStatus, this.statusRateMs);
                }
                catch (e) {
                    this.$emit("error", e);
                }
            },
            fetchScreenshot() {
                clearTimeout(this.timeoutScreenshot);
                let image = new Image();
                const rect = this.$refs.container.getBoundingClientRect();
                const timeStartMs = performance.now();
                image.src = "/api/v1/proxy/screenshot?uid=" + (Date.now()) + "&width=" + rect.width + "&height=" + rect.height + "&top=" + this.pageOffsetHeight + "&left=" + this.pageOffsetWidth;
                image.onload = () => {
                    const timeMs = performance.now() - timeStartMs;

                    // Adjust the screenshotRateMs according to the time it takes to generate and get this screenshot
                    this.screenshotRateMs = timeMs * 2;

                    this.image = image;
                    this.timeoutScreenshot = setTimeout(this.fetchScreenshot, this.screenshotRateMs);
                }
            },
            getCoordinatesFromEvent(e) {
                const rect = this.$refs.screen.getBoundingClientRect();
                const coord = (e.touches && e.touches.length) ? {x: e.touches[0].pageX, y: e.touches[0].pageY} : {x: e.pageX, y: e.pageY};
                const scroll = {x: window.pageXOffset || document.documentElement.scrollLeft, y: window.pageYOffset || document.documentElement.scrollTop};

                return {
                    x: Math.round((coord.x - rect.x - scroll.x) * this.screenshotWidth / rect.width + this.pageOffsetWidth),
                    y: Math.round((coord.y - rect.y - scroll.y) * this.screenshotHeight / rect.height + this.pageOffsetHeight)
                };
            },
            handleClick(e) {
                const coord = this.getCoordinatesFromEvent(e);
                console.log("click @ (" + coord.x + ", " + coord.y + ")");
                this.utility.fetch("/api/v1/proxy/click", coord);
            },
            handleKeydown(e) {
                this.utility.fetch("/api/v1/proxy/press", {
                    key: String(e.key)
                });
            },
            scrollVertical(inc) {
                this.pageOffsetHeight = Math.max(0, Math.min(this.pageHeight - this.screenshotHeight, this.pageOffsetHeight + inc));
            },
            scrollHorizontal(inc) {
                this.pageOffsetWidth = Math.max(0, Math.min(this.pageWidth - this.screenshotWidth, this.pageOffsetWidth + inc));
            },
            async selectPage(index) {
                await this.utility.fetch("/api/v1/proxy/select", {
                    index: index
                });
                this.pageOffsetHeight = 0;
                this.pageOffsetTop = 0;
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
                await this.utility.fetch("/api/v1/proxy/goto", {
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
        position: relative;

        .proxy-tabs {
            display: flex;
            flex-flow: row nowrap;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;

            .proxy-tab {
                border: 1px solid #777;
                border-bottom: none;
                padding: 0 10px;
                line-height: 28px;
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
            position: absolute;
            top: 30px;
            left: 0;
            width: 100%;

            .proxy-toolbar-url {
                flex: 2;
            }

            .proxy-toolbar-url,
            .proxy-toolbar-send {
                border: 1px solid #777;
                padding: 0 10px;
                line-height: 28px;
                font-size: 18px;
            }
        }

        .proxy-wrapper {

            margin: 0;
            padding: 0;
            border: none;
            width: calc(100% - 20px);
            height: calc(100% - 80px);
            overflow: hidden;
            position: absolute;
            top: 60px;
            left: 0;
            width: 100%;

            .proxy-overlay {
                position: absolute;
                top: 0;
                left: 0;
                background-color: rgba(255, 255, 255, 0.5);
                pointer-events: none;
                padding: 0 5px;
            }

            .proxy-screen {
                margin: 0;
                padding: 0;
                border: none;
            }
        }

        .proxy-scrollbar-vertical {
            width: 20px;
            height: calc(100% - 80px);
            position: absolute;
            top: 60px;
            right: 0;

            .proxy-cursor-up,
            .proxy-cursor-down {
                width: 20px;
                height: 20px;
                background-color: #000;
                position: absolute;
            }

            .proxy-cursor-up {
                top: 0;
            }
            .proxy-cursor-down {
                top: 20px;
            }
        }

        .proxy-scrollbar-horizontal {
            width: calc(100% - 20px);
            height: 20px;
            position: absolute;
            bottom: 0;

            .proxy-cursor-left,
            .proxy-cursor-right {
                width: 20px;
                height: 20px;
                background-color: #000;
                position: absolute;
            }

            .proxy-cursor-left {
                left: 0;
            }
            .proxy-cursor-right {
                right: 0;
            }
        }
    }
</style>
