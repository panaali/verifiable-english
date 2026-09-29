"""Browser acceptance smoke with a disposable loopback server and no model calls."""
import os
import re
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
                context = browser.new_context(viewport={'width': 1280, 'height': 800}, accept_downloads=True)
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(url)
                page.locator('#token').fill(token)
                page.get_by_role('button', name='Unlock workspace').click()
                expect(page.locator('#ide')).to_be_visible(timeout=30000)
                expect(page.locator('#prose')).to_be_empty()
                expect(page.locator('#documentStatus')).to_contain_text('The draft is empty.')
                page.locator('#prose').fill('Api is safe.')
                page.locator('#analyse').click()
                expect(page.locator('#documentStatus')).to_contain_text('The reading is ready.')
                page.locator('#approveReading').click()
                expect(page.locator('#documentStatus')).to_contain_text('The reading is approved.')
                page.reload()
                expect(page.locator('#prose')).to_have_value('Api is safe.')
                expect(page.locator('#documentStatus')).to_contain_text('The reading is approved.')
                page.locator('#newDocument').click()
                expect(page.locator('#prose')).to_be_empty()
                page.locator('#prose').fill('A strange new assertion.')
                page.locator('#analyse').click()
                expect(page.locator('#recovery')).to_contain_text('Word help')
                expect(page.locator('#recovery')).to_contain_text('The app shows the example.')
                page.locator('#cancelReview').click()
                expect(page.locator('#documentStatus')).to_contain_text('The draft is available.')
                page.locator('#analyse').click()
                page.locator('#askRepair').click()
                expect(page.locator('#documentStatus')).to_contain_text('The budget is exhausted.')
                page.once('dialog', lambda dialog: dialog.accept('No faithful reading yet.'))
                page.locator('#unresolvedReading').click()
                expect(page.locator('#documentStatus')).to_contain_text('The reading is unresolved.')
                page.locator('#undoReview').click()
                expect(page.locator('#documentStatus')).to_contain_text('The draft is available.')
                page.locator('#exampleSelect').select_option('scope')
                expect(page.locator('#documentStatus')).to_contain_text('The draft is empty.')
                page.locator('#prose').fill('Every engineer checks a server.')
                page.locator('#analyse').click()
                expect(page.locator('.checked-card')).to_have_count(1)
                expect(page.locator('.checked-card')).to_contain_text('Engineer 1 checks Server 1.')
                page.locator('.checked-card .card-reading button').first.click()
                expect(page.locator('#documentStatus')).to_contain_text('The reading is ready.')
                page.locator('#approveReading').click()
                expect(page.locator('#documentStatus')).to_contain_text('The reading is approved.')
                second = page.context.new_page()
                second.goto(url)
                expect(second.locator('#ide')).to_be_visible()
                second.locator('#prose').fill('A second tab changed this sentence.')
                second.locator('#analyse').click()
                expect(second.locator('#documentUnits')).to_contain_text('A second tab changed this sentence.')
                page.locator('#prose').fill('An outdated edit.')
                page.locator('#analyse').click()
                expect(page.locator('#notice')).to_contain_text('another tab')
                expect(page.locator('#prose')).to_have_value('A second tab changed this sentence.')
                second.close()
                page.locator('#newDocument').click()
                page.locator('#documentMode').select_option('translation')
                page.locator('#prose').fill('Every engineer checks a server.')
                page.locator('#analyse').click()
                expect(page.locator('.checked-card')).to_have_count(1)
                expect(page.locator('#recovery')).to_contain_text('Source alternatives stay together')
                assert page.locator('.checked-card button').count() == 0
                page.reload()
                expect(page.locator('#documentMode')).to_have_value('translation')
                expect(page.locator('.checked-card')).to_have_count(1)
                page.locator('#newDocument').click()
                page.locator('#prose').fill('<img src=x onerror=alert(1)>')
                page.locator('#analyse').click()
                assert page.locator('#recovery img').count() == 0
                page.locator('#rulesNav').click()
                expect(page.locator('#rules')).to_be_visible()
                expect(page.locator('#rulesResult')).to_contain_text('no conflict')
                page.locator('#rulesText').fill(page.locator('#rulesText').input_value().replace(' (exception to rule 1)', ''))
                page.locator('#checkRules').click()
                expect(page.locator('#rulesResult')).to_contain_text('The conflict is present.')
                page.locator('#learnNav').click()
                page.locator('[data-example="news"]').click()
                expect(page.locator('#lessonViews .explicit-badge').first).to_be_visible()
                assert not re.search(r'[@()\[\]*<=]', page.locator('#lessonViews .natural-view').inner_text())
                page.locator('#asimovNav').click()
                expect(page.locator('#asimov')).to_be_visible()
                expect(page.locator('#asimovRules li')).to_have_count(13)
                expect(page.locator('#asimovDocument')).to_have_text('Conflict-free')
                swimmer = page.locator('.asimov-card', has_text='Pulling a swimmer out of the water')
                expect(swimmer.locator('.asimov-verdict')).to_contain_text('Required')
                swimmer.locator('summary', has_text='Change the facts').click()
                swimmer.locator('input[type=checkbox]').uncheck()
                swimmer.get_by_role('button', name='Ask VE again').click()
                swimmer = page.locator('.asimov-card', has_text='Pulling a swimmer out of the water')
                expect(swimmer).to_contain_text('VE decided this again just now', timeout=30000)
                expect(swimmer.locator('.asimov-verdict')).to_contain_text('Permitted')
                assert not re.search(r'[@()\[\]*<=_{}]', page.locator('#asimov').inner_text())
                if os.environ.get('VE_SMOKE_SCREENSHOT'):
                    page.screenshot(path=os.environ['VE_SMOKE_SCREENSHOT'], full_page=True)
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
            print('Browser smoke passed: blank draft, approval, reload, checked card, recovery, two-tab conflict, translation alternatives, escaped prose, Rules, Asimov edit and re-run, export, mobile layout, logout.')
        finally:
            server.terminate()
            server.wait(timeout=10)


if __name__ == '__main__':
    main()
