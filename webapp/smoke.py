"""Optional browser integration smoke; no live model calls or external assets."""
import json
import os
from pathlib import Path
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
        token=secrets.token_urlsafe(32)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
        url=f'http://127.0.0.1:{port}'
        server=subprocess.Popen([sys.executable,'-m','ve_webapp','--http','--host','127.0.0.1',
            '--port',str(port),'--state-dir',temp], env={**os.environ,'VE_WEB_TOKEN':token},
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    urllib.request.urlopen(url,timeout=1).close();break
                except OSError: time.sleep(.1)
            else: raise RuntimeError('Smoke server did not start')
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
                page=browser.new_page(viewport={'width':1280,'height':800})
                errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(url)
                page.locator('#token').fill(token);page.get_by_role('button',name='Unlock workspace').click()
                expect(page.locator('#workspace')).to_be_visible()
                expect(page.locator('#lessonViews .view')).to_have_count(4)
                page.get_by_role('button',name='Check this example').click()
                expect(page.locator('#lessonResult')).to_contain_text('Certified consequence')
                page.locator('[data-example="news"]').click()
                expect(page.locator('#lessonViews .view')).to_have_count(4)
                page.get_by_role('button',name='Check this example').click()
                expect(page.locator('#lessonResult')).to_contain_text('A countermodel exists')
                page.locator('[data-example="policy"]').click()
                expect(page.locator('#lessonViews .view')).to_have_count(4)
                page.locator('#openExample').click()
                page.locator('#premises').fill('@api is reviewed.')
                page.locator('#claim').press('Control+Enter')
                expect(page.locator('#checkResult')).to_contain_text('A countermodel exists')
                page.locator('#claim').fill('@api is .')
                expect(page.locator('#validation')).to_contain_text('line 1')
                page.locator('#claim').fill('@api is safe.')
                expect(page.locator('#validation')).to_contain_text('Parsed and type-checked')
                # Stub only browser-facing model response, never enable server-side models.
                page.route('**/api/propose',lambda route:route.fulfill(json={
                    'ok':True,'candidates':[{'text':'@api is safe.','paraphrase':'Api is safe.','reading':'<img src=x onerror=alert(1)>'}],
                    'comparisons':[]}))
                page.locator('#propose').evaluate('(b)=>b.disabled=false')
                page.locator('#prose').fill('The API is safe.')
                page.locator('#propose').click()
                expect(page.locator('#candidates')).to_contain_text('<img src=x onerror=alert(1)>')
                assert page.locator('#candidates img').count()==0
                page.get_by_role('button',name='Accept this reading').click()
                expect(page.locator('#provenance')).to_contain_text('Model proposal accepted')
                page.locator('#theme').click()
                page.locator('#tourButton').click()
                expect(page.locator('#tour')).to_be_visible()
                for _ in range(4):page.locator('#tourNext').click()
                expect(page.locator('#tour')).not_to_be_visible()
                with page.expect_download() as download:page.locator('#export').click()
                assert download.value.suggested_filename=='ve-draft.json'
                for width in (1280,390):
                    page.set_viewport_size({'width':width,'height':844})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {width}px'
                page.locator('#logout').click();expect(page.locator('#login')).to_be_visible()
                assert not errors,errors
                browser.close()
            print('Browser smoke passed: login, views, proofs, countermodels, diagnostics, mocked candidates, XSS rendering, tour, theme, export, mobile layout, logout.')
        finally:
            server.terminate();server.wait(timeout=10)


if __name__=='__main__':main()
