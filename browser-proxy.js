"use strict";

const Puppeteer = require("puppeteer");

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
            ready: {proactive: true}
        });
    }

    async start() {
        Exception.assert(this.browser === null && this.page === null);

        this.browser = await Puppeteer.launch();
        this.page = await this.browser.newPage();

        this.event.trigger("ready");

        await this.goto('https://www.mikewesthad.com/twine-resources/demos/animate.css/example.html');
    }

    async stop() {
        this.event.clear("ready");
        await browser.close();
    }

	async waitReady() {
		return this.event.waitUntil("ready");
    }

    async screenshot() {
        Exception.assert(this.event.is("ready"), "Module is not ready");

        return await this.page.screenshot({});
    }

    async goto(url) {
        Exception.assert(this.event.is("ready"), "Module is not ready");

        await this.page.goto(url);
    }

    async click(x, y) {
        Exception.assert(this.event.is("ready"), "Module is not ready");

        await this.page.mouse.click(x, y);
    }
}
