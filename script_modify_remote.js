var identifier = "This is a testing script";
var title = document.getElementById("title");
var content = document.getElementById("content");
title.textContent = "Big Title";
content.textContent = "Lorem Ipsum";

setTimeout(function() {
	document.getElementById("singleton_script").src =
			"./script_modify_remote2.js";
}, 3000);
