"use strict";

const Puppeteer = require("puppeteer");
const Process = require("process");
const Which = require("which");

const Log = require("./lib/log.require.js")("browser-proxy");
const Exception = require("./lib/exception.require.js")("browser-proxy");
const Event = require("./lib/event.require.js");

/**
 * Add events functionality
 */
module.exports = class BrowserProxy {
	constructor(options) {
        this.browser = null;
        this.page = null;

        this.event = new Event({
            ready: {proactive: true},
            // Page goto error
            error: {proactive: true}
        });
    }

    async start() {
        Exception.assert(this.browser === null && this.page === null);

        // Clear all events
        this.event.clear();

        let config = {};
        switch (Process.arch)
        {
        // On some architectures, the executable for chromium is not available
        case "arm":
        case "arm64":
            const path = Which.sync("chromium", {nothrow: true})
                    || Which.sync("chromium-browser", {nothrow: true})
                    || Which.sync("google-chrome", {nothrow: true});
            if (path) {
                config.executablePath = path;
            }
            break;
        }

        this.browser = await Puppeteer.launch(config);
        this.page = await this.browser.newPage();
        this.width = 0;
        this.height = 0;

        this.event.trigger("ready");

        await this.goto('http://www.google.com');
    }

    async stop() {
        this.event.clear("ready");
        await browser.close();
    }

	async waitReady() {
		return this.event.waitUntil("ready");
    }

	async setViewport(width, height) {
        Exception.assert(this.event.is("ready"), "Module is not ready");
        Exception.assert(!this.event.is("error"), "Page has error");

        if (this.width != width || this.height != height) {
            await this.page.setViewport({ width: width, height: height });
            this.width = width;
            this.height = height;
        }
    }

    async selectPage(index) {
        Exception.assert(this.event.is("ready"), "Module is not ready");

        const pages = await this.browser.pages();

        Exception.assert(index >= 0 && index < pages.length, "Page requested is out of bound");

        this.page = pages[index];
    }

    async screenshot(config) {
        Exception.assert(this.event.is("ready"), "Module is not ready");
        Exception.assert(!this.event.is("error"), "Page has error");

        config = Object.assign({
            type: "png"
        }, config);

        return await this.page.screenshot({
            type: config.type,
            quality: 20,
            encoding: "binary"
        });
    }

    async goto(url) {
        Exception.assert(this.event.is("ready"), "Module is not ready");

        this.event.clear("error");
        try {
            await this.page.goto(url, {
                timeout: 30000,
                waitUntil: "domcontentloaded"
            });
        }
        catch (e) {
            this.event.trigger("error");
            throw e;
        }
    }

    async click(x, y) {
        Exception.assert(this.event.is("ready"), "Module is not ready");
        Exception.assert(!this.event.is("error"), "Page has error");

        await this.page.mouse.click(x, y);
    }

    async press(key) {
        Exception.assert(this.event.is("ready"), "Module is not ready");
        Exception.assert(!this.event.is("error"), "Page has error");

        await this.page.keyboard.press(key);
    }

    /**
     * Get the current status of the browser
     */
    async getStatus() {

        // Get all open pages title
        const pageList = await this.browser.pages();

        const index = pageList.findIndex((page) => (this.page === page))

        let pageTitleList = [];
        for (const i in pageList) {
            pageTitleList.push(await pageList[i].title());
        }

        const dimensions = await this.page.evaluate(() => {
            return {
                width: document.width || document.body.offsetWidth,
                height: document.height || document.body.offsetHeight
            }
        });

        return {
            viewportWidth: this.width,
            viewportHeight: this.height,
            width: dimensions.width,
            height: dimensions.height,
            pages: pageTitleList,
            index: index,
            url: this.page.url()
        }
    }
}
