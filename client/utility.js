"use strict";

export default {
	async fetch(api, args = {}, type = "text") {
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
};
