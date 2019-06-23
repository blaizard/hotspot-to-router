"use strict"

const Path = require("path");

const Log = require("../log.require.js")("template", "factory");
const Exception = require("../exception.require.js")("template", "factory");
const Template = require("../template.require.js");
const FileSystem = require("../filesystem.require.js");

module.exports = class Factory {

	/**
	 * Construct the template factory
	 */
	constructor() {
		this.template = Template.fromFileSync(Path.resolve(__dirname, "factory.index.html"));
	}

	/**
	 * Generate a template from a manifest
	 */
	fromManifest(manifest, entryId, content) {

		// Sanity check
		Exception.assert(manifest.entries.hasOwnProperty(entryId), "There is no entry ID \"" + entryId + "\"");

		// Create the dependency list
		const cssList = (manifest.common.css || []).concat(manifest.entries[entryId].css || []);
		const jsList = (manifest.common.js || []).concat(manifest.entries[entryId].js || []);

		// Generate the template
		return this.template.process(Object.assign({
			base: manifest.path.split("/").filter((entry) => (entry && entry != "/")).map((entry) => "..").join("/"),
			css: cssList.map((path) => ("<link href=\"" + manifest.path + path + "\" rel=\"stylesheet\"/>")).join(""),
			js: jsList.map((path) => ("<script src=\"" + manifest.path + path + "\"></script>")).join(""),
			head: "",
			body: ""
		}, content));
	}

	/**
	 * Generate the template for all entries in the manifest
	 */
	async allEntriesFromManifest(outputPath, manifest, content) {
		for (const entryId in manifest.entries) {
			const data = this.fromManifest(manifest, entryId, content);
			await FileSystem.writeFile(Path.join(outputPath, entryId + ".html"), data);
			Log.info("Generated \"" + Path.join(outputPath, entryId) + ".html\"");
		}
	}
};
