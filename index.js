"use strict";

// Dependencies
const Path = require("path");
const ChildProcess = require("child_process");

const Log = require("./lib/log.require.js")("server");
const Exception = require("./lib/exception.require.js")("server");
const Web = require("./lib/web.require.js");
const FileSystem = require("./lib/filesystem.require.js");
const BrowserProxy = require("./browser-proxy.js");

// Set-up the web server
let web = new Web(8001, {
	rootDir: Path.resolve(__dirname, "www")
});

// Add the various REST APIs
web.addRoute("get", "/api/v1/wifi/list", async (request, response) => {
	const output = ChildProcess.spawnSync("python", ["./bin/wifi.py", "list"]);
	response.send(output.stdout.toString());
}, undefined, { exceptionGuard: true });

let browser = new BrowserProxy();
browser.start();

web.addRoute("get", "/api/v1/proxy/screenshot", async (request, response) => {

	response.setHeader("Content-Type", "image/png");
	response.status(200);

	const buffer = await browser.screenshot();

	response.write(buffer,"binary");
    response.end(null, "binary");
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/proxy/click", async (request, response) => {

	const x = parseInt(request.query.x);
	const y = parseInt(request.query.y);

	await browser.click(x, y);
	response.sendStatus(200);
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/proxy/goto", async (request, response) => {

	const url = request.query.url;

	await browser.goto(url);
	response.sendStatus(200);
}, undefined, { exceptionGuard: true });

web.start();
