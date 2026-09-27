"""Browser acceptance smoke with a disposable loopback server and no model calls."""
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from playwright.sync_api import sync_playwright, expect


def main():
    with tempfile.TemporaryDirectory(prefix='ve-web-smoke-') as temp:
        token = secrets.token_urlsafe(32)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        url = f'http://127.0.0.1:{port}'
        server = subprocess.Popen([sys.executable, '-m', 've_webapp', '--http', '--host', '127.0.0.1',
                                   '--port', str(port), '--state-dir', temp],
                                  env={**os.environ, 'VE_WEB_TOKEN': token},
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    urllib.request.urlopen(url, timeout=1).close()
                    break
                except OSError:
                    time.sleep(.1)
            else:
                raise RuntimeError('Smoke server did not start')
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
                page = browser.new_page(viewport={'width': 1280, 'height': 800}, accept_downloads=True)
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(url)
                page.locator('#token').fill(token)
                page.get_by_role('button', name='Unlock workspace').click()
                expect(page.locator('#ide')).to_be_visible(timeout=30000)
                expect(page.locator('#prose')).to_be_empty()
                expect(page.locator('#documentStatus')).to_contain_text('blank draft')
                page.locator('#prose').fill('Api is safe.')
                page.locator('#analyse').click()
                expect(page.locator('#documentStatus')).to_contain_text('ready')
                page.locator('#approveReading').click()
                expect(page.locator('#documentStatus')).to_contain_text('approved')
                page.reload()
                expect(page.locator('#prose')).to_have_value('Api is safe.')
                expect(page.locator('#documentStatus')).to_contain_text('approved')
                page.locator('#newDocument').click()
                expect(page.locator('#prose')).to_be_empty()
                page.locator('#prose').fill('A strange new assertion.')
                page.locator('#analyse').click()
                expect(page.locator('#recovery')).to_contain_text('needs your help')
                page.locator('#askRepair').click()
                expect(page.locator('#documentStatus')).to_contain_text('exhausted')
                page.once('dialog', lambda dialog: dialog.accept('No faithful reading yet.'))
                page.locator('#unresolvedReading').click()
                expect(page.locator('#documentStatus')).to_contain_text('unresolved')
                page.locator('#exampleSelect').select_option('scope')
                expect(page.locator('#documentStatus')).to_contain_text('blank draft')
                page.locator('#prose').fill('Every engineer checks a server.')
                page.locator('#analyse').click()
                expect(page.locator('.checked-card')).to_have_count(1)
                expect(page.locator('.checked-card')).to_contain_text('Engineer 1 checks Server 1.')
                page.locator('.checked-card .card-reading button').first.click()
                expect(page.locator('#documentStatus')).to_contain_text('ready')
                page.locator('#approveReading').click()
                expect(page.locator('#documentStatus')).to_contain_text('approved')
                page.locator('#newDocument').click()
                page.locator('#prose').fill('<img src=x onerror=alert(1)>')
                page.locator('#analyse').click()
                assert page.locator('#recovery img').count() == 0
                page.locator('#rulesNav').click()
                expect(page.locator('#rules')).to_be_visible()
                expect(page.locator('#rulesResult')).to_contain_text('no conflict')
                page.locator('#rulesText').fill(page.locator('#rulesText').input_value().replace(' (exception to rule 1)', ''))
                page.locator('#checkRules').click()
                expect(page.locator('#rulesResult')).to_contain_text('Conflict found')
                page.locator('#ideNav').click()
                with page.expect_download() as download:
                    page.locator('#export').click()
                assert download.value.suggested_filename == 've-document.json'
                for width in (1280, 390):
                    page.set_viewport_size({'width': width, 'height': 844})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
                page.locator('#logout').click()
                expect(page.locator('#login')).to_be_visible()
                assert not errors, errors
                browser.close()
            print('Browser smoke passed: blank draft, approval, reload, checked card, recovery, escaped prose, Rules, export, mobile layout, logout.')
        finally:
            server.terminate()
            server.wait(timeout=10)


if __name__ == '__main__':
    main()
