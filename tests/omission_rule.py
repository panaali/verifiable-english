"""The record paths of the uc-audit omission rule, ported for the use-case condition tests (one copy in this repo).

The rule's owner is the audit tooling outside this repository: manage-agents `tools-local/uc-audit.py`, `omit_exposure`,
version omission-2 (installed 2026-11-13 22:59Z, reviews/dri-decisions-20261113-uc-audit-omission-bind.md item 1; file
sha256 1c7cc4f79bce94e8...). Tests cannot read that file (hermetic), so this module ports its exposure step line for line
over the working tree instead of `git show <commit>:`. Every record path is kept, including the fail-closed ones a partial
copy tends to drop:

- accounting.d1.txt: a `loss` tag, and ANY other or empty tag (`exposition`, `dropped`, untagged) = `loss`; a line whose
  quotes do not parse = `loss`; a `restates` / `rule <id>` / `reading RSn` tag whose words (every whole token but the
  articles, no threshold; an empty word list never resolves) are not all in one segment of the carrier (one formal body
  statement or one predicate legend, comments, header and quoted literals stripped) = `mistag`;
- a unit with no accounting line = `no-record` (no accounting file: unit `*`);
- PLAN section 12 and every gaps / coverage text: each sentence naming the unit (bare or backticked) = `plan12` / `gaps`;
  README and every docs REPORT.md of the case: such a sentence with a drop or merge word = `report`; a gaps / coverage
  JSON object naming the unit = `gaps`;
- an UNFORMALISED span whose blocked_rule (a list or a comma list too) names the unit = `unformalised`;
- a revoked documentation clearance = `revoked`.

`tools/` and `ve/` never import this module: it is test evidence about a use case's files, not a VE answer.
"""

import json
import re
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OMISSION_VERSION = "omission-2"
OMISSION_SHA256_PREFIX = "1c7cc4f79bce94e8"
OMIT_REVOKED = {"anthropic-rsp": ("f16-ask-commentary",), "openai-preparedness": ("f9-threshold",)}
OMIT_DROP_RE = re.compile(r"\b(drop|drops|dropped|merge|merged|merges|leaves out|left out|omit|omits|omitted|not translated|"
                          r"no rule|unformalised|restates?|removed|lost|lose|loses|loss|omission|unformalized|not formali[sz]ed|"
                          r"not encoded|excluded|skipped|deferred|dropping|deleted|folded|collapsed|subsumed|simplified|"
                          r"combined|replaced|out of scope|not model?led)\b", re.I)
OMIT_STOP = {"a", "an", "the"}
OMIT_GAP_RE = re.compile(r"gap|coverage", re.I)
SENTENCE_SPLIT = re.compile(r"(?<=[.;:])\s+(?=[A-Z(`])|\n\s*\n|\n(?=\s*(?:\d+\.|[-*])\s)|\s\|\s")
PATHS = ("loss", "mistag", "no-record", "plan12", "report", "gaps", "unformalised", "revoked")


def omit_norm(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("—", "-"), ("–", "-"),
                 ("‑", "-"), ("‐", "-"), ("…", "..."), ("‚", ",")):
        s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s.lower()).strip()
    return re.sub(r"(?<=[a-z])- (?=[a-z])", "", s)


def content_words(s):
    return [w for w in re.findall(r"[a-z0-9]+", omit_norm(s)) if w not in OMIT_STOP]


def rule_blocks(text):
    """{block id: (block text incl. header, body text)} of a rules.d1.ve / facts.d1.ve ('## <id> | ...' headers)."""
    lines = text.splitlines()
    heads = [(i, m.group(1)) for i, line in enumerate(lines) for m in [re.match(r"^## (\S+) \|", line)] if m]
    out = {}
    for j, (i, uid) in enumerate(heads):
        e = heads[j + 1][0] if j + 1 < len(heads) else len(lines)
        out[uid] = ("\n".join(lines[i:e]).rstrip(), "\n".join(lines[i + 1:e]))
    return out


def used_predicates(rule_text, env):
    used = []
    for key, p in ((env.get("vocabulary") or {}).get("predicates") or {}).items():
        hit = re.search(r'classified as "' + re.escape(key) + '"', rule_text)
        for tp in (p.get("verbalisation"), (p.get("regulated") or {}).get("act")):
            if hit or not tp:
                continue
            tp = re.sub(r"^\{0\}\s*", "", tp)
            pat = re.sub(r"\\\{\d\\\}", ".+?", re.escape(tp))
            if re.search(r"(?<![A-Za-z])" + pat + r"(?![A-Za-z])", rule_text):
                hit = True
        if hit:
            used.append(key)
    return used


def legend_raw(key, vlines):
    start = next((i for i, line in enumerate(vlines) if re.match(r'\s*"' + re.escape(key) + r'"\s*:', line)), None)
    if start is None:
        return []
    out, depth, j = [vlines[start]], vlines[start].count("(") - vlines[start].count(")"), start + 1
    while j < len(vlines) and (depth > 0 or vlines[j].lstrip().startswith('"')
                               and not re.match(r'\s*"[a-z0-9_]+"\s*:', vlines[j])):
        out.append(vlines[j])
        depth += vlines[j].count("(") - vlines[j].count(")")
        j += 1
        if len(out) > 40:
            break
    return out


def strip_comments(lines, body=False):
    out = []
    for line in lines:
        if line.lstrip().startswith(("#", "--", "//")):
            continue
        line = re.sub(r"\s*(#|--|//).*$", "", re.sub(r'"[^"]*"', " ", line)) if body else re.sub(r"\s#.*$", "", line)
        out.append(line)
    return out


def json_records(x, ptr, names):
    """[(pointer, unit)]: every JSON object of a gaps / coverage file that names a unit, at that object's pointer."""
    out = []

    def hit(s, p):
        out.extend((p, u) for u in sorted(set(re.findall(r"[A-Za-z0-9_.:+-]+", s)) & names))
    if isinstance(x, dict):
        for k, v in x.items():
            if k in names:
                out.append((f"{ptr}/{k}", k))
            if isinstance(v, str):
                hit(v, ptr or "/")
            elif isinstance(v, list):
                for i, e in enumerate(v):
                    if isinstance(e, str):
                        hit(e, ptr or "/")
                    else:
                        out += json_records(e, f"{ptr}/{k}/{i}", names)
            else:
                out += json_records(v, f"{ptr}/{k}", names)
    elif isinstance(x, list):
        for i, e in enumerate(x):
            if isinstance(e, str):
                hit(e, ptr or "/")
            else:
                out += json_records(e, f"{ptr}/{i}", names)
    return out


def _read(path):
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else None


def _tree(root, base):
    """Repo-relative paths of the files under base, sorted as `git ls-tree -r` lists them (caches left out)."""
    d = root / base
    if not d.is_dir():
        return []
    return sorted(p.relative_to(root).as_posix() for p in d.rglob("*")
                  if p.is_file() and not any(part == "__pycache__" or part.startswith(".")
                                             for part in p.relative_to(root).parts))


def exposures(case, units, root=REPO):
    """omit_exposure's step 1-4 over the tree at `root`: {unit: [(unit, record unit, path, detail)]}, or None when a rules,
    PLAN, spans or gaps file is unreadable (the rule then excludes every answer: fail closed)."""
    units = set(units)
    cdir = root / "usecases" / case
    rules = _read(cdir / "rules.d1.ve")
    plan = _read(cdir / "PLAN.md")
    try:
        spans = json.loads(_read(cdir / "spans.json") or "null")["units"]
        assert isinstance(spans, list)
    except (ValueError, TypeError, KeyError, AssertionError):
        spans = None
    if rules is None or plan is None or spans is None:
        return None
    blocks = rule_blocks(rules)
    fblocks = rule_blocks(_read(cdir / "facts.d1.ve") or "")
    top = sorted(p.name for p in cdir.iterdir() if p.is_file())
    envs = [n for n in top if re.fullmatch(r"environment\.d1\.json", n)]
    try:
        env = json.loads(_read(cdir / envs[0])) if envs else {}
    except ValueError:
        env = {}
    vf = sorted(n for n in top if n.endswith("vocabulary.py"))
    vlines = _read(cdir / vf[0]).splitlines() if vf else []
    cache = {}

    def carrier(uid):
        if uid not in cache:
            b = blocks.get(uid) or fblocks.get(uid)
            if not b:
                cache[uid] = []
            else:
                body = strip_comments(b[1].splitlines(), body=True)
                legs = ["\n".join(strip_comments(legend_raw(k, vlines))) for k in used_predicates(b[1], env)]
                cache[uid] = [set(re.findall(r"[a-z0-9_]+", omit_norm(x))) for x in body + legs if x.strip()]
        return cache[uid]

    def carried(cw, uid):
        return any(cw <= seg for seg in carrier(uid))
    heads = {uid: " | ".join(b[0].splitlines()[0].split(" | ", 3)[1:3])
             for uid, b in list(fblocks.items()) + list(blocks.items())}
    exp = {}

    def put(u, path, det):
        uu = u if u in units else "FACTS" if "FACTS" in units and u in fblocks else u
        if uu in units:
            e = (uu, u, path, det)
            if e not in exp.setdefault(uu, []):
                exp[uu].append(e)
    acc = _read(cdir / "accounting.d1.txt")
    seen = set()
    for line in (acc or "").splitlines():
        if " | omits:" not in line:
            continue
        uid, rest = line.split(" | omits:", 1)
        uid = uid.strip()
        seen.add("FACTS" if uid in fblocks and uid not in units else uid)
        ents = re.findall(r'"([^"]*)"\s*([^;"]*)', rest)
        if rest.count('"') != 2 * len(ents):
            put(uid, "loss", "accounting line not parseable: " + rest.strip()[:80])
        for words, tag in ents:
            tag = tag.strip()
            kind = tag.split()[0] if tag else ""
            if kind == "loss":
                put(uid, "loss", words)
            elif kind not in ("restates", "rule", "reading"):
                put(uid, "loss", f'{words} ({tag or "untagged"})')
            else:
                cw = set(content_words(words))
                arg = tag.split()[1] if len(tag.split()) > 1 else ""
                if not cw:
                    ok = False
                elif kind == "rule":
                    ok = bool(arg) and carried(cw, arg)
                elif kind == "restates":
                    ok = carried(cw, uid)
                else:
                    rs = re.match(r"(RS|N)\d+", arg)
                    ok = (bool(rs) and re.search(r"(?<![A-Za-z0-9])" + rs.group(0) + r"(?![0-9])", heads.get(uid, ""))
                          is not None and carried(cw, uid))
                if not ok:
                    put(uid, "mistag", f"{words} ({tag})")
    if acc is None:
        exp["*"] = [("*", "*", "no-record", "no accounting file: a per-answer read is required")]
    else:
        for u in units:
            if u not in seen:
                put(u, "no-record", "no accounting line")
    m = re.search(r"^#{2,3}\s*12\b.*?(?=^#{2,3}\s*13\b|\Z)", plan, re.M | re.S)
    docs = [("plan12", m.group(0) if m else plan)]
    dpaths = [p for p in _tree(root, "docs/usecases") if case in p.split("/")[2:-1]]
    docs += [("report", _read(root / p) or "")
             for p in [f"usecases/{case}/README.md"] + [p for p in dpaths if p.endswith("REPORT.md")]]
    gpaths = sorted({p for p in _tree(root, f"usecases/{case}") + dpaths if OMIT_GAP_RE.search(p.rsplit("/", 1)[-1])})
    names = units | set(fblocks)
    for p in gpaths:
        txt = _read(root / p)
        if txt is None:
            return None
        if p.endswith(".json"):
            try:
                js = json.loads(txt)
            except ValueError:
                return None
            for ptr, u in json_records(js, "", names):
                put(u, "gaps", f"{p}#{ptr}")
        else:
            docs.append(("gaps", txt))
    for path, txt in docs:
        for sent in SENTENCE_SPLIT.split(txt):
            if path in ("plan12", "gaps") or OMIT_DROP_RE.search(sent):
                for u in {t.rstrip(".:") for t in re.findall(r"[A-Za-z0-9_.:+-]+", sent)} & names:
                    put(u, path, " ".join(sent.split())[:160])
    for s in spans:
        if str(s.get("status", "")).upper() == "UNFORMALISED" and s.get("blocked_rule"):
            br = s["blocked_rule"]
            for x in (br if isinstance(br, list) else [br]):
                for u in re.split(r"[,\s]+", str(x)):
                    if u:
                        put(u, "unformalised", s.get("id", ""))
    for ru in OMIT_REVOKED.get(case, ()):
        if ru in units:
            put(ru, "revoked", "documentation-based clearance revoked (lp1701 item 1)")
    return exp


def record_paths(case, units, root=REPO):
    """{unit: [path, ...]} (one entry per exposure, in the rule's order) for the units that carry any record."""
    exp = exposures(case, units, root)
    if exp is None:
        raise AssertionError(f"{case}: a rules, PLAN, spans or gaps file is unreadable (the rule fails closed)")
    return {u: [e[2] for e in es] for u, es in exp.items() if es}
