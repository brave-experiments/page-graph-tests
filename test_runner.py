# vim: set tw=99 ts=4 sw=4 et:

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import asyncio
import fnmatch
import importlib.util
import logging
import os
import re
import sys
import tempfile
import traceback
import urllib.parse
import time

import aiofiles
from aiohttp import web
from chromewhip import Chrome
import chromewhip.protocol as devtools
import colorama
from colorama import Fore
from networkx import graphml

process_termination_timeout = 10

wait_check_interval = 0.2
wait_timeout = 30
wait_js = 'document.body.dataset.hasOwnProperty("testWait")'

devtools_listening_re = re.compile('^DevTools listening on (?P<devtools_ws_uri>.+)$')

web_server_host = 'localhost'
web_server_port = 8080
web_server_uri_prefix = 'http://{}:{}/'.format(web_server_host, web_server_port)

root_dir_path = os.path.dirname(os.path.realpath(__file__))
graphml_dir_path = os.path.join(root_dir_path, 'graphml')
logs_dir_path = os.path.join(root_dir_path, 'logs')
tests_dir_path = os.path.join(root_dir_path, 'tests')
test_html_dir_path = os.path.join(tests_dir_path, 'html')
test_scripts_dir_path = os.path.join(tests_dir_path, 'scripts')

colorama.init()

# Configure chromewhip logging.
logging.getLogger('chromewhip.chrome.Chrome').setLevel(logging.ERROR)

async def run_tests(brave_exe_path, test_name_filters=['*'], headless=True):
    # Start web server hosting the test HTML content.

    app = web.Application()
    app.add_routes([web.static('/', test_html_dir_path)])

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, web_server_host, web_server_port)
    await site.start()

    # Execute tests.
    total_tests = 0
    passed_tests = 0
    for (root_dir_path, sub_dir_paths, test_script_file_paths) in os.walk(test_scripts_dir_path):
        sub_dir_paths.sort()
        test_script_file_paths.sort()
        for test_script_file_path in test_script_file_paths:
            test_name, file_ext = os.path.splitext(test_script_file_path)
            if file_ext != '.py':
                continue

            test_name_matched = False
            for test_name_filter in test_name_filters:
                if fnmatch.fnmatch(test_name, test_name_filter):
                    test_name_matched = True
                    break
            if not test_name_matched:
                continue

            total_tests += 1
            passed_tests += await run_test(test_name, brave_exe_path, headless=headless)

    # Stop web server.
    await runner.cleanup()

    print('===> Result: {}/{} test(s) passed'.format(passed_tests, total_tests))
    if passed_tests != total_tests:
        sys.exit(1)

async def run_test(test_name, brave_exe_path, headless=True):
    print(Fore.CYAN + 'Running test: ' + Fore.RESET + test_name)

    test_page_file_name = test_name + '.html'
    test_page_file_path = os.path.join(test_html_dir_path, test_page_file_name)
    test_page_uri = web_server_uri_prefix + urllib.parse.quote(test_page_file_name)

    # Use a fresh temporary directory for the browser profile.
    with tempfile.TemporaryDirectory('brave-tmp-profile') as profile_dir_path:
        # Launch the browser.

        brave_args = [
            # Arguments Puppeteer uses when launching Chrome:
            '--disable-background-networking',
            # '--enable-features=NetworkService,NetworkServiceInProcess',
            # ^ breaks Brave Shields
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-client-side-phishing-detection',
            '--disable-default-apps',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--disable-features=site-per-process,TranslateUI,BlinkGenPropertyTrees',
            '--disable-hang-monitor',
            '--disable-ipc-flooding-protection',
            '--disable-popup-blocking',
            '--disable-prompt-on-repost',
            '--disable-renderer-backgrounding',
            '--disable-sync',
            '--force-color-profile=srgb',
            '--metrics-recording-only',
            '--no-first-run',
            '--enable-automation',
            '--password-store=basic',
            '--use-mock-keychain',
            '--hide-scrollbars',
            '--mute-audio',
            'about:blank',
            '--remote-debugging-port=0',
            '--user-data-dir=' + profile_dir_path,
            # Custom Brave options:
            '--v=0',
            '--disable-brave-update',
            '--enable-logging=stderr',
        ]

        if headless:
            brave_args.append('--headless')

        proc = await asyncio.create_subprocess_exec(
            brave_exe_path,
            *brave_args,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        test_succeeded = False
        page_graph_data = None

        try:
            browser_output = ''

            # Collect lines from the browser's output.
            async def take_output_line():
                nonlocal browser_output
                line = (await proc.stdout.readline()).decode('utf-8')
                browser_output += line
                return line

            # Wait for DevTools to be ready and figure out what host/port it's
            # listening on.

            devtools_ws_uri = None

            while not proc.stdout.at_eof():
                line = await take_output_line()
                match = devtools_listening_re.match(line)
                if match is not None:
                    devtools_ws_uri = urllib.parse.urlparse(match.group('devtools_ws_uri'))
                    break

            if devtools_ws_uri is None:
                raise RuntimeError('Brave quit prematurely')

            devtools_host = devtools_ws_uri.hostname
            devtools_port = devtools_ws_uri.port

            # For the remainder of the test run, collect the browser's output in the background.
            async def collect_browser_output():
                try:
                    while not proc.stdout.at_eof():
                        await take_output_line()
                except asyncio.CancelledError:
                    pass
            collect_browser_output_task = asyncio.create_task(collect_browser_output())

            # Connect to the browser DevTools and open the test page in a new
            # tab.

            browser = Chrome(host=devtools_host, port=devtools_port)
            await browser.connect()

            tab = await browser.create_tab()
            await tab.enable_page_events()

            await tab.send_command(
                devtools.page.Page.navigate(url=test_page_uri),
                await_on_event_type=devtools.page.FrameStoppedLoadingEvent,
            )

            # Sleep while "data-test-wait" is set on the document's body.
            total_time = 0
            while total_time < wait_timeout:
                has_wait_attribute = (await tab.evaluate(wait_js))['ack']['result']['result'].value
                if not has_wait_attribute:
                    break
                await asyncio.sleep(wait_check_interval)
                total_time += wait_check_interval

            # sleep in case we have requests, so they are added properly to the
            # graph
            time.sleep(1)

            # Grab and parse the page graph data.
            result = await tab.send_command(
                (
                    devtools.page.Page.build_send_payload('generatePageGraph', {}),
                    devtools.page.Page.convert_payload(
                        {'data': {'class': str, 'optional': False}}
                    ),
                )
            )

            page_graph_data = result['ack']['result']['data']
            page_graph = graphml.parse_graphml(page_graph_data)

            # Read in the test page HTML.
            async with aiofiles.open(test_page_file_path, 'r', encoding='utf-8') as test_page_file:
                test_page_html = await test_page_file.read()

            # Import the test script as a module.
            test_spec = importlib.util.spec_from_file_location(
                test_name, os.path.join(test_scripts_dir_path, test_name + '.py')
            )
            test_module = importlib.util.module_from_spec(test_spec)

            try:
                # Evaluate the test case, passing in the test page HTML, its
                # corresponding page graph, and a reference to the open browser tab.
                test_spec.loader.exec_module(test_module)
                test_module.test(page_graph, test_page_html, tab)
            except BaseException as e:
                if isinstance(e, AssertionError):
                    print('...' + Fore.RED + 'FAIL' + Fore.RESET)
                else:
                    print('...' + Fore.YELLOW + 'ERROR' + Fore.RESET)
                print(Fore.MAGENTA + 'Test Traceback:' + Fore.RESET)
                traceback.print_exc()
            else:
                test_succeeded = True
                print('...' + Fore.GREEN + 'OK' + Fore.RESET)

            # Close all tabs and terminate the browser instance.
            for tab in browser.tabs:
                await browser.close_tab(tab)
        finally:
            try:
                proc.stdout._transport.close()
                await collect_browser_output_task
            except BaseException:
                # Output collection failed.
                pass

            if not test_succeeded:
                log_file_path = os.path.join(logs_dir_path, test_name + '.log')
                os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
                async with aiofiles.open(log_file_path, 'w', encoding='utf-8') as log_file:
                    await log_file.write(browser_output)

                print(Fore.MAGENTA + 'Browser Log:' + Fore.RESET)
                print('Dumped to ' + log_file_path)

                if page_graph_data is not None:
                    graphml_file_path = os.path.join(graphml_dir_path, test_name + '.graphml')
                    os.makedirs(os.path.dirname(graphml_file_path), exist_ok=True)
                    async with aiofiles.open(
                        graphml_file_path, 'w', encoding='utf-8'
                    ) as graphml_file:
                        await graphml_file.write(page_graph_data)

                    print(Fore.MAGENTA + 'Page Graph Data:' + Fore.RESET)
                    print('Dumped to ' + graphml_file_path)

            try:
                proc.terminate()
            except ProcessLookupError:
                # Process not running.
                pass

            try:
                await asyncio.wait_for(proc.wait(), timeout=process_termination_timeout)
            except asyncio.TimeoutError:
                proc.kill()

        return test_succeeded

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Page Graph test suite for the Brave browser.')
    parser.add_argument(
        'brave', metavar='BRAVE', help='path to a Page Graph-enabled Brave browser executable'
    )
    parser.add_argument(
        '--filter',
        metavar='FILTER',
        nargs='+',
        dest='filters',
        default='*',
        help='run only tests with names matching one of these glob-style filters',
    )
    parser.add_argument(
        '--no-headless',
        dest='headless',
        action='store_false',
        default=True,
        help='disable headless mode browser execution',
    )

    args = parser.parse_args()
    asyncio.run(run_tests(args.brave, test_name_filters=args.filters, headless=args.headless))
