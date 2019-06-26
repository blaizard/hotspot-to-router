"use strict";

// Dependencies
const Path = require("path");
const ChildProcess = require("child_process");

const Log = require("./lib/log.require.js")("server");
const Exception = require("./lib/exception.require.js")("server");
const Web = require("./lib/web.require.js");
const FileSystem = require("./lib/filesystem.require.js");

// Set-up the web server
let web = new Web(8001, {
	rootDir: Path.resolve(__dirname, "www")
});

// Add the various REST APIs
web.addRoute("get", "/api/v1/wifi/list", async (request, response) => {
	const output = ChildProcess.spawnSync("python", ["./bin/wifi.py", "list"]);
	response.send(output.stdout.toString());
});

web.start();
