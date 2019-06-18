const p = require("puppeteer");
const child_process = require("child_process");

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
		args: ["--no-sandbox"]}).then(async browser => {
	const page = await browser.newPage();
	await page.goto("http://localhost:8000/" + target);
	child_process.execSync("kill -30 -" + browser.process().pid);
	child_process.execSync("sleep 5");  // Give enough time for the PG dump.
	await browser.close();

	child_process.execSync("./" + base_target + ".py");
});

