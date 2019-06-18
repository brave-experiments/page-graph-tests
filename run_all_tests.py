#!/usr/bin/env python3

import argparse
import sys
import subprocess

if __name__ == "__main__":
	all_tests = [
			"static_page.html",
			"cross_dom_script.html",
			"script_modify.html",
			"eval.html",
		]

	parser = argparse.ArgumentParser()
	parser.add_argument("--brave-bin-path", "-p", type=str,
			help="Path to Brave binary", required=True)
	args = parser.parse_args()

	brave_bin_path = args.brave_bin_path

	# Spin up a temporary HTTP server.
	http_server = subprocess.Popen(["python3", "-m", "http.server"],
			stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	for test in all_tests:
		print("\n[*] Running test \"{0}\"...\n".format(test))
		p = subprocess.Popen(["node", "puppeteer_run_test.js",
				brave_bin_path, test])
		p.wait()

	http_server.terminate()

