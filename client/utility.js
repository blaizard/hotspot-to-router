"use strict";

export default class Utility {

	constructor(errorHandler = null) {
		this.errorHandler = errorHandler;
	}

	async fetch(api, args = {}, type = "text") {
		try {
			const query = Object.keys(args).map((key) => key + "=" + encodeURIComponent(args[key])).join("&");
			const url = api + ((query) ? ("?" + query) : "");
			const response = await fetch(url);
			if (!response.ok) {
				throw Error((await response.text()) || response.statusText);
			}
			let data = null;
			switch (type) {
			case "json":
				data = await response.json();
				break;
			default:
				data = await response.text();
			}
			return data;
		}
		catch (e) {
			if (this.errorHandler) {
				this.errorHandler(e);
			}
			else {
				throw e;
			}
		}
	}
};
