"use strict";

// Dependencies
const Path = require("path");
const ChildProcess = require("child_process");

const Log = require("./lib/log.require.js")("server");
const Exception = require("./lib/exception.require.js")("server");
const Web = require("./lib/web.require.js");
const FileSystem = require("./lib/filesystem.require.js");
const RemoteBrowser = require("./remote-browser.js");

// Set-up the web server
let web = new Web(8080, {
	rootDir: Path.resolve(__dirname, "www")
});

let browser = null;

async function restartBrowser()
{
	if (browser) {
		await browser.stop();
	}
	browser = new RemoteBrowser();
	await browser.start();
	await browser.goto("http://neverssl.com/");
}

restartBrowser();

/*
"statusList": [{"uptime": 40.15963292121887, "log": "/home/blaise/projects/hotspot-to-router/.irapp/log/hotspot/8453", "pid": 8453, "cpu": 4.5, "memory": 456949760.0, "type": "daemon", "id": "hotspot", "restart": 0}], "dispatchResults": {}}
*/

// Add the various REST APIs
web.addRoute("get", "/api/v1/apps/status", async (request, response) => {
	const output = ChildProcess.spawnSync("python", ["./app.py", "info", "--apps", "--json"]);
	response.send(output.stdout.toString());
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/wifi/list", async (request, response) => {
	const output = ChildProcess.spawnSync("python", ["./bin/wifi.py", "list"]);
	response.send(output.stdout.toString());
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/wifi/connect", async (request, response) => {
	const ssid = request.query.ssid;
	const password = request.query.password || null;

	ChildProcess.spawnSync("python", ["./bin/wifi.py", "connect", ssid].concat((password) ? [password] : []));
	response.sendStatus(200);
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/temperature/get", async (request, response) => {
	const output = ChildProcess.spawnSync("python", ["./bin/temperature.py", "get"]);
	response.send(output.stdout.toString());
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/proxy/reset", async (request, response) => {
	await restartBrowser();
	response.sendStatus(200);
}, undefined, { exceptionGuard: true });

web.addRoute("get", "/api/v1/proxy/screenshot", async (request, response) => {

	const width = parseInt(request.query.width) || 800;
	const height = parseInt(request.query.height) || 600;
	const left = parseInt(request.query.left) || 0;
	const top = parseInt(request.query.top) || 0;

	await browser.setViewport(width, height);

	const buffer = await browser.screenshot({
		type: "jpeg",
		left: left,
		top: top
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
