'use strict';

const Log = require('./log.require.js')("server");
const Exception = require('./exception.require.js')("server");
const Web = require('./web.require.js');
const Router = require('./router.require.js');
const Http = require('http');
const Https = require('https');
const HttpProxy = require('http-proxy');
const Fs = require('fs');

module.exports = class Proxy {
	constructor(port, config) {
		this.config = Object.assign({
			/**
			 * \brief Public key of the SSL certificate.
			 */
			key: null,
			/**
			 * \brief SSL certificate.
			 */
			cert: null,
			/**
			 * \brief SSL certificate authority.
			 */
			ca: null,
			/**
			 * \brief Port of local server to serve static files.
			 */
			localPort: 29876,
			/**
			 * \brief Root directory of the static data to provide.
			 */
			rootDir: false,
			/**
			 * \brief Use data compression and minfy certain file types.
			 */
			useCompression: true,
			/**
			 * \brief List of routes to be registered.
			 */
			routes: {}
		}, config);
		this.port = port;

		// Create the proxy server
		this.proxy = HttpProxy.createProxyServer({
			changeOrigin: true
		});

		// Create the router instance
		this.router = new Router({
			fallback: (path, req, res) => {
				Log.info("Fallback " + path);
				this.proxy.web(req, res, { target: "http://localhost:" + this.config.localPort });
			}
		});

		// Register the routes
		for (let path in this.config.routes) {
			this.router.add(path + "{path:.*}", (vars, req, res) => {
				Log.info("Proxy " + req.url + " toward " + this.config.routes[path]);
				// Update URL
				req.url = vars.path || "/";
				this.proxy.web(req, res, { target: this.config.routes[path] });
			});
		}

		this.web = new Web(this.config.localPort, {
			rootDir: this.config.rootDir,
			useCompression: this.config.useCompression
		});
	}

	handleRequest(req, res) {
		const path = req.url;
		Log.info("Processing " + path);
		this.router.dispatch(path, req, res);
	}

	/**
	 * Start the server
	 */
	start() {
		return new Promise((resolve, reject) => {

			// Start the web server
			this.web.start();

			// If any of the certificate file is set, assume SSL is to be used
			const useSSL = this.config.key || this.config.cert || this.config.ca;
			let configStrList = [];

			// Create the server
			if (useSSL) {
				let options = {};
				if (this.config.key) options.key = Fs.readFileSync(this.config.key);
				if (this.config.cert) options.cert = Fs.readFileSync(this.config.cert);
				if (this.config.ca) options.ca = Fs.readFileSync(this.config.ca);
				this.server = Https.createServer(options, (req, res) => {
					this.handleRequest(req, res);
				});
				configStrList.push("SSL");
			}
			else {
				this.server = Http.createServer((req, res) => {
					this.handleRequest(req, res);
				});
			}

			this.server.listen(this.port, undefined, undefined, () => {
				resetErrorHandler.call(this, reject);
				Log.info("Proxy server started on port " + this.port
						+ ((configStrList.length) ? (" (" + configStrList.join(" and ") + ")") : ""));
				resolve();
			});
			this.server.on('error', (e) => {
				resetErrorHandler.call(this, reject);
				reject(new Exception(e));
			});
		});
	}

	/**
	 * Stop the server
	 */
	stop() {
	}

	/**
	 * \brief Add a custom route the web server.
	 *
	 * \param type The type of HTTP request (get, post, put, delete or patch).
	 * \param uri The uri to which the request should match.
	 * \param callback A callback that will be called if the uri and type matches
	 *                 the request.
	 */
	addRoute(type, uri, callback) {
		return this.web.addRoute(type, uri, callback);
	}
}

function resetErrorHandler(reject)
{
	this.server.on('error', (e) => {
		reject(e);
	});
}
