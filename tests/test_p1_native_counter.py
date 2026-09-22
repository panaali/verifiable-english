"""Offline native-counter tests: pinned templates, no downloads or providers."""
import hashlib
import importlib.util
import json
from copy import deepcopy

import pytest
from tokenizers import Tokenizer, models, pre_tokenizers

from experiments import p1
from experiments.p1_preflight import CommandCounter

spec = importlib.util.spec_from_file_location('native_counter', p1.HERE / 'native_counter.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


def config(name):
    return json.loads((native.HERE / f'tokenizers/{name}_config.json').read_text())


def wire(model='replication'):
    return {'model': p1.MODELS[model], 'messages': [
        {'role': 'system', 'content': 'Reply with one word.'},
        {'role': 'user', 'content': 'Hello'}]}


def test_qwen_exact_joint_chat_template():
    assert native.chat_text(wire(), config('qwen')) == (
        '<|im_start|>system\nReply with one word.<|im_end|>\n'
        '<|im_start|>user\nHello<|im_end|>\n<|im_start|>assistant\n')


def test_llama_exact_joint_chat_template():
    assert native.chat_text(wire('weak'), config('llama')) == (
        '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n'
        'Reply with one word.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n'
        'Hello<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n')


def test_llama_date_adjustment_preserves_content_and_tool_template():
    value = wire('weak')
    dates = 'Cutting Knowledge Date: December 2023\nToday Date: 26 Jul 2024\n\n'
    value['messages'][1]['content'] = dates + 'Hello'
    assert native.chat_text(value, config('llama')).count(dates) == 1
    value['tools'] = [{'type': 'function', 'function': {'name': 'replay'}}]
    text = native.chat_text(value, config('llama'))
    assert text.count(dates) == 2
    assert 'Environment: ipython' in text and '"name": "replay"' in text
    changed = {**config('llama'), 'chat_template': '{{ messages }}'}
    with pytest.raises(ValueError, match='unrecognized Llama date template'):
        native.chat_text(wire('weak'), changed)


@pytest.mark.parametrize('judge,expected', [('replication', 19), ('weak', 21)])
def test_retained_deepinfra_smoke_native_count(judge, expected, monkeypatch):
    counter = native.NativeCounter()
    blob = counter.sources[p1.MODELS[judge]]['files']['tokenizer.json']['git_blob_sha1']
    if not (counter.cache / (blob + '.json')).exists():
        pytest.skip('pinned tokenizer not cached; test never downloads')
    monkeypatch.setattr(native.httpx, 'get', lambda *a, **kw: pytest.fail('network forbidden'))
    assert counter(wire(judge)) == expected


@pytest.mark.parametrize('name', ['qwen', 'llama'])
def test_tool_schema_and_replay_are_joint_and_arguments_are_objects(name):
    value = wire()
    value['tools'] = [{'type': 'function', 'function': {'name': 'replay',
        'description': 'unique-schema-marker', 'parameters': {'type': 'object'}}}]
    value['messages'] += [
        {'role': 'assistant', 'content': None, 'tool_calls': [{'id': 'r1', 'type': 'function',
         'function': {'name': 'replay', 'arguments': '{"item_id":"é<&"}'}}]},
        {'role': 'tool', 'tool_call_id': 'r1', 'content': 'unique-finding-marker'}]
    before = deepcopy(value)
    text = native.chat_text(value, config(name))
    assert 'unique-schema-marker' in text and 'unique-finding-marker' in text
    assert '"item_id": "é<&"' in text
    assert value == before
    assert text.endswith('<|im_start|>assistant\n' if name == 'qwen'
                         else '<|start_header_id|>assistant<|end_header_id|>\n\n')


def test_counter_encodes_joint_text_once_without_extra_special_tokens(tmp_path, monkeypatch):
    counter = native.NativeCounter(tmp_path)
    tokenizer = Tokenizer(models.WordLevel({'[UNK]': 0, 'Hello': 1}, unk_token='[UNK]'))
    tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
    class Recorder:
        calls = []
        def encode(self, text, **kwargs):
            self.calls.append((text, kwargs))
            return tokenizer.encode(text, **kwargs)
    recorder = Recorder()
    counter.loaded[p1.MODELS['replication']] = recorder, config('qwen')
    monkeypatch.setattr(native.httpx, 'get', lambda *a, **kw: pytest.fail('network forbidden'))
    assert counter(wire()) == len(tokenizer.encode(native.chat_text(wire(), config('qwen'))).ids)
    assert recorder.calls == [(native.chat_text(wire(), config('qwen')), {'add_special_tokens': False})]
    with pytest.raises(ValueError, match='panel blocked'):
        counter({**wire(), 'model': 'unverified/model'})


def test_pinned_config_bytes_and_upstream_identity():
    sources = native.NativeCounter().sources
    llama = sources[p1.MODELS['weak']]
    assert llama['files']['tokenizer.json']['git_blob_sha1'] == '5cc5f00a5b203e90a27a3bd60d1ec393b07971e8'
    assert llama['files']['tokenizer_config.json']['git_blob_sha1'] == 'db88166e2bc4c799fd5d1ae643b75e84d03ee70e'
    for source in sources.values():
        native.verify_blob((native.HERE / 'tokenizers' / source['config_file']).read_bytes(),
                           source['files']['tokenizer_config.json']['git_blob_sha1'])


def test_corrupt_cache_blocks_without_download(tmp_path, monkeypatch):
    blob = hashlib.sha1(b'blob 2\0{}').hexdigest()
    (tmp_path / (blob + '.json')).write_text('corrupt')
    monkeypatch.setattr(native.httpx, 'get', lambda *a, **kw: pytest.fail('network forbidden'))
    with pytest.raises(ValueError, match='hash mismatch'):
        native.tokenizer_bytes({'git_blob_sha1': blob}, tmp_path)


def test_bundled_command_counter_uses_local_counter_and_detects_asset_changes(monkeypatch):
    counter = CommandCounter(p1.HERE / 'native_counter.py')
    assert counter.native is not None
    counter.native = lambda value: 123
    assert counter(wire()) == 123
    original = p1.sha
    monkeypatch.setattr(p1, 'sha', lambda path: 'changed' if path.name == 'sources.json' else original(path))
    with pytest.raises(p1.PreflightError, match='configuration changed'):
        counter(wire())


def test_cli_defaults_to_bundled_counter(monkeypatch):
    from experiments import p1_preflight
    import sys
    calls = []
    monkeypatch.setattr(sys, 'argv', ['run_p1.py', 'preflight-openrouter', '--cap-usd', '.5'])
    monkeypatch.setattr(p1_preflight, 'preflight_openrouter', lambda cap, path: calls.append((cap, path)) or 0)
    assert p1.main() == 0
    assert calls == [(.5, p1.HERE / 'native_counter.py')]


@pytest.mark.parametrize('message', [
    {'role': 'unsupported', 'content': 'Hello'},
    {'role': 'user', 'content': [{'type': 'image_url', 'image_url': 'x'}]},
    {'role': 'assistant', 'content': '', 'tool_calls': [{'function': {'name': 'replay', 'arguments': 'bad json'}}]},
])
def test_unsupported_wire_fails_closed(message):
    with pytest.raises(ValueError):
        native.chat_text({'messages': [message]}, config('qwen'))
