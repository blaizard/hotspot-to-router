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

web.addRoute("get", "/api/v1/wifi/connect", async (request, response) => {
	const ssid = request.query.ssid;

	ChildProcess.spawnSync("python", ["./bin/wifi.py", "connect", ssid]);
	response.sendStatus(200);
}, undefined, { exceptionGuard: true });

let browser = new BrowserProxy();
browser.start();

web.addRoute("get", "/api/v1/proxy/screenshot", async (request, response) => {

	const width = parseInt(request.query.width) || 800;
	const height = parseInt(request.query.height) || 600;

	await browser.setViewport(width, height);

	const buffer = await browser.screenshot({
		type: "jpeg"
	});

	response.setHeader("Content-Type", "image/jpeg");
	response.status(200);
	response.write(buffer,"binary");
    response.end(null, "binary");
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/proxy/click", async (request, response) => {

	const x = parseInt(request.query.x);
	const y = parseInt(request.query.y);

	await browser.click(x, y);
	response.sendStatus(200);
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/proxy/press", async (request, response) => {

	const key = request.query.key;

	await browser.press(key);
	response.sendStatus(200);
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/proxy/goto", async (request, response) => {

	const url = request.query.url;

	await browser.goto(url);
	response.sendStatus(200);
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/proxy/select", async (request, response) => {

	const index = parseInt(request.query.index);

	await browser.selectPage(index);
	response.sendStatus(200);
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/proxy/status", async (request, response) => {

	const status = await browser.getStatus();
	response.json(status);
}, undefined, { exceptionGuard: true });

web.start();
