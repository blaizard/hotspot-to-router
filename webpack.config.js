const Path = require("path");
const Webpack = require("./lib/webpack.js");
const TemplateFactory = require("./lib/template/factory.js");

let config = {
	entries: {
		index: Path.resolve(__dirname, "client/app.js")
	},
	output: Path.resolve(__dirname, "www/"),
	publicPath: "",
	hooks: {
		manifest: async (manifest, config) => {
			// Generate the templates of the entry points
			const factory = new TemplateFactory();
			await factory.allEntriesFromManifest(config.output, manifest, {
				body: "<div id=\"app\"></div>"
			});
			return manifest;
		}
	}
};

module.exports = Webpack.generate(config);
