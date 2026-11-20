"""rsp-repair-r1-catastrophic-1119: D2's severity class "catastrophic" carries RSP footnote 1 verbatim to its end.

Footnote 1 defines "catastrophic risk". The use case recorded its first clause as a D2D3 loss; now the legend of
D2's footnote-1 constant (`existential_threats`, classed catastrophic: the risk wire's `severity.classes` is a list of
names with no legend of its own) quotes the whole footnote, and the D2D3 accounting line no longer records it.

The sentences are read from the pinned source text (usecases/anthropic-rsp/source/extract_text.py's output) through
build_document's own unit partition (fn1-catastrophic, fn1-plain-meaning, fn1-sb53) and compared byte for byte after
the project's quote normalisation (usecases/safetyfw_accounting.py `norm`). Without the stored text the test checks
the legend's footnote run against the SHA-256 of that normalised text (the repository keeps hashes, not the text).
"""
import hashlib
import re

import test_rsp_fidelity_fix as fix
import test_safetyfw_usecases as base
from tests.pinned_source import pinned_source

RSP = base.RSP
FN1_UNITS = ("fn1-catastrophic", "fn1-plain-meaning", "fn1-sb53")
# norm(footnote 1) without its marker "1 ": 445 bytes, from the pinned text (source SHA-256 c7de7fe2...).
FN1_SHA256 = "defb605c778e98890ff8e403eb06fb551b6c92547d2dd94a9fadd235be3942f3"
FN1_RUN = re.compile(r'"Catastrophic risk" as used .*? separate compliance frameworks\.')


def _norm(text):
    return fix._accounting().norm(text).strip()


def _legend():
    """The legend D2 sends: the description of the footnote-1 constant in the risk environment."""
    return base.rsp_stage0.risk_environment()["vocabulary"]["constants"]["existential_threats"]["description"]


def _source_sentences(path):
    """Footnote 1's sentences, each normalised, from the pinned text: the three fn1 units' spans, marker cut."""
    source = path.read_bytes()
    spans = dict(zip((unit[1] for unit in base.rsp_build.UNITS), base.rsp_build.spans(source)))
    sentences = [_norm(source[slice(*spans[unit])].decode("utf-8")) for unit in FN1_UNITS]
    assert sentences[0].startswith('1 "Catastrophic risk"')
    return [sentences[0][2:]] + sentences[1:]


def test_catastrophic_legend_quotes_footnote_1_to_its_end():
    """Each sentence of footnote 1 is in the legend byte for byte (normalised), and so is the whole footnote."""
    legend = _legend()
    path = pinned_source("anthropic-rsp", skip=False)
    if path is not None:
        sentences = _source_sentences(path)
        assert len(sentences) == 3 and sentences[-1].endswith("separate compliance frameworks.")
        for sentence in sentences:
            assert sentence in legend, sentence
        whole = " ".join(sentences)
        assert whole in legend
        assert hashlib.sha256(whole.encode()).hexdigest() == FN1_SHA256
    run = FN1_RUN.search(legend)
    assert run is not None and hashlib.sha256(run.group(0).encode()).hexdigest() == FN1_SHA256


def test_footnote_1_constant_stays_in_the_catastrophic_class():
    """The legend is on a constant D2 classes catastrophic (S5's instance), not on an unclassified one."""
    env = base.rsp_stage0.risk_environment()
    assert ["existential_threats", "catastrophic"] in env["risk"]["harm_classes"]
    assert env["risk"]["severity"]["classes"] == ["catastrophic"]


def test_d2d3_no_longer_records_footnote_1_as_a_loss():
    """The D2D3 line keeps its other entries and records no footnote-1 words; the saved report agrees."""
    acc = fix._accounting()
    [line] = [e for _, b, e, _ in acc.read_sidecar(RSP / "accounting.d1.txt") if b == "D2D3"]
    assert not [e for e in line if "refers generally" in e["words"] or "Catastrophic risk" in e["words"]]
    # srccov-anthropic-rsp-1119 moved the sub-heading "Scope." into the s31-heading unit, so D2D3 no longer records it.
    assert [(e["words"], e["reason"]) for e in line] == [
        ("A Risk Report will cover the risks of Anthropic's models and actions", "loss")]
