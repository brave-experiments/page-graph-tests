const p = require("puppeteer");
const child_process = require("child_process");
const fs = require("fs");

if (process.argv.length != 4) {
	console.log("[-]: Wrong number of arguments");
	process.exit(-1);
}

const brave_bin_path = process.argv[2]
const target = process.argv[3];
const base_target = target.split(".").slice(0, -1).join(".");

p.launch({
		//headless: false,
		executablePath: brave_bin_path,
		//dumpio: true,
		args: ["--no-sandbox",
			"--enable-logging=/dev/null"]}).then(async browser => {

	// Visit test page.
	const page = await browser.newPage();
	await page.goto("http://localhost:8000/" + target);

	// Dump the PG.
	const client = await page.target().createCDPSession();
	const rep = await client.send("Page.generatePageGraph");
	await fs.promises.writeFile("/tmp/pagegraph.log", rep.data);

	await browser.close();

	// Run unittest.
	child_process.execSync("./" + base_target + ".py");
});

