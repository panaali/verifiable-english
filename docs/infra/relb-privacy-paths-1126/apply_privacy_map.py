#!/usr/bin/env python3
"""relb-privacy-paths (privacy steps 3+4): replace owner/login names (kind b) and private paths (kind e) in the
tracked tree with neutral forms, by one mechanical map. Value-free: every private value is read at run time from
the host or the environment; none is written here.

Usage: python3 -I apply_privacy_map.py --repo <checkout> [--write] [--held held.json] [--skip path ...]
Environment (required): PRIVACY_OPS_REPO  the operations repo's directory (its basename is the name mapped to
                        <ops-repo>; its ACCOUNTS.md gives the account order),
                        PRIVACY_REPO_OWNER  the public repository's owner (kept only inside the public repo URL),
                        PRIVACY_ACCOUNTS_DIR  the directory holding the per-account claude-* directories.
Values read from the host: the login name and home directory, the claude-* directory names in $PRIVACY_ACCOUNTS_DIR, the
ssh config's User lines.

Map (in this order on every line):
  paths   (/home/<login> | /Users/<login> | ~ | $HOME | ${HOME}) /code/<ops repo>   -> <ops-repo>
          (same prefixes) /code/<another repository>                              -> <home>/code/<its name>
          (same prefixes) /code/<dir> (a VE checkout)                             -> <repo>   (rest of path kept)
          (same prefixes) /ve-inputs                                              -> <inputs>
          /home/<any user> | /Users/<any user> starting a path                    -> <home>
          ~/.ve-<x> | $HOME/.ve-<x>                                               -> <home>/.ve-<x>
  names   worker account handles and labels (ACCOUNTS.md order, main first, then other account directories sorted;
          spellings equal after removing . _ - are one account)
                                                                                  -> worker-account-1..n
          a handle's name part alone (split at . _ -; >= 4 characters) -> its handle's role (first handle wins)
          the login name -> operator; ssh User names -> ssh-user; the repo owner -> repo-owner
          (whole words: not preceded or followed by a letter or digit; any case; the public repo URL is kept)
Without --write it only counts. Prints counts per rule (no values).
"""
import getpass, json, os, re, subprocess, sys
from collections import Counter


def private_values():
    ops = os.environ["PRIVACY_OPS_REPO"].rstrip("/")
    owner = os.environ["PRIVACY_REPO_OWNER"]
    login = getpass.getuser()
    home = os.path.expanduser("~")
    # accounts: a list of alias groups, one per account, in ACCOUNTS.md row order (main first). A row's label
    # (column 1, unless "main") is an alias of its directory's handle; account directories not in ACCOUNTS.md come
    # after, sorted. Handles equal after removing . _ - are one account (review B1).
    order = []

    def norm(h):
        return re.sub(r"[._-]", "", h.lower())

    def add(*hs):
        hs = [h for h in hs if h and h != "main"]
        for g in order:
            if any(norm(h) in {norm(x) for x in g} for h in hs):
                g.extend(h for h in hs if h not in g)
                return
        order.append(list(dict.fromkeys(hs)))
    for line in open(os.path.join(ops, "ACCOUNTS.md")):
        f = line.split()
        if len(f) >= 2 and f[1].startswith("/") and "/claude-" in f[1]:
            add(f[1].rstrip("/").rsplit("/claude-", 1)[1], f[0])
    acc = os.environ["PRIVACY_ACCOUNTS_DIR"]  # the accounts directory (named here by the environment only)
    for d in sorted(os.listdir(acc)) if os.path.isdir(acc) else []:
        if d.startswith("claude-"):
            add(d[len("claude-"):])
    ssh_users = []
    try:
        for line in open(os.path.join(home, ".ssh/config")):
            f = line.split()
            if len(f) >= 2 and f[0].lower() == "user" and f[1] not in ssh_users and len(f[1]) >= 4:
                ssh_users.append(f[1])
    except OSError:
        pass
    # directories under ~/code that are not VE checkouts: present here with another root commit or no git, plus
    # the ones the tree names that live on other machines (separate repositories, not private names)
    other = set(OTHER_REPOS)
    code = os.path.join(home, "code")
    ve_root = subprocess.run(["git", "-C", os.environ.get("PRIVACY_VE_REPO", "."), "rev-list", "--max-parents=0",
                              "HEAD"], capture_output=True, text=True).stdout.split()
    for d in sorted(os.listdir(code)) if os.path.isdir(code) else []:
        if d == os.path.basename(ops) or not os.path.isdir(os.path.join(code, d)):
            continue
        r = subprocess.run(["git", "-C", os.path.join(code, d), "rev-list", "--max-parents=0", "HEAD"],
                           capture_output=True, text=True).stdout.split()
        if not set(r) & set(ve_root):
            other.add(d)
    return dict(ops=os.path.basename(ops), owner=owner, login=login, home=home, handles=order, ssh_users=ssh_users,
                other_repos=sorted(other))


OTHER_REPOS = ("ve-bench", "ve-northstar", "ve-webapp", "ve-github-export")


def build_rules(v):
    L = re.escape(v["login"])
    pre = rf"(?:/home/{L}|/Users/{L}|~|\$HOME|\$\{{HOME\}})"
    rules = [
        ("e:ops-repo", re.compile(rf"{pre}/code/{re.escape(v['ops'])}(?![\w.-])"), "<ops-repo>"),
        # another repository (not a VE checkout) keeps its directory name under <home>/code (review B2)
        ("e:other-repo", re.compile(rf"{pre}/code/(?=(?:{'|'.join(map(re.escape, v['other_repos']))})(?![\w.-]))"),
         "<home>/code/"),
        ("e:repo", re.compile(rf"{pre}/code/[\w.-]+"), "<repo>"),
        ("e:inputs", re.compile(rf"{pre}/ve-inputs(?![\w.-])"), "<inputs>"),
        # a home directory starts a path: a /home/ segment inside another path (a test sandbox) is not one (B3)
        ("e:home", re.compile(r"(?<![\w.$}/])(?:/home|/Users)/[A-Za-z0-9_][\w.-]*"), "<home>"),
        ("e:home-dot-ve", re.compile(r"(?:~|\$HOME)/(?=\.ve-[\w.-])"), "<home>/"),
    ]
    names = [(h, f"worker-account-{i}") for i, g in enumerate(v["handles"], 1) for h in g]
    names += [(v["login"], "operator")] + [(u, "ssh-user") for u in v["ssh_users"]] + [(v["owner"], "repo-owner")]
    # a handle's name parts (split at . _ -, >= 4 characters, not all digits) stand for that handle when alone
    for i, g in enumerate(v["handles"], 1):
        for h in g:
            parts = [p for p in re.split(r"[._-]", h) if len(p) >= 4 and not p.isdigit()]
            if len(parts) > 1:
                names += [(p, f"worker-account-{i}") for p in parts]
    seen, uniq = set(), []
    for val, role in sorted(names, key=lambda x: -len(x[0])):
        if val.lower() not in seen and len(val) >= 4:
            seen.add(val.lower()); uniq.append((val, role))
    for val, role in uniq:
        rules.append((f"b:{role}", re.compile(rf"(?<![A-Za-z0-9]){re.escape(val)}(?![A-Za-z0-9])", re.I), role))
    public = re.compile(rf"(?:github\.com[/:])?{re.escape(v['owner'])}/verifiable-english", re.I)
    return rules, public


def transform(text, rules, public, counts):
    kept = []

    def keep(m):
        kept.append(m.group(0)); return f"\x00PUB{len(kept) - 1}\x00"
    text = public.sub(keep, text)
    for name, rx, new in rules:
        text, n = rx.subn(new, text)
        if n:
            counts[name] += n
    return re.sub(r"\x00PUB(\d+)\x00", lambda m: kept[int(m.group(1))], text)


def main(argv):
    repo, write, held, skip = None, False, None, set()
    it = iter(argv)
    for a in it:
        if a == "--repo": repo = next(it)
        elif a == "--write": write = True
        elif a == "--held": held = next(it)
        elif a == "--skip": skip.add(next(it))
    v = private_values()
    rules, public = build_rules(v)
    if held:
        skip |= set(json.load(open(held)))
    out = subprocess.run(["git", "-C", repo, "ls-files", "-z"], capture_output=True, check=True).stdout
    counts, files_changed, renames = Counter(), 0, []
    for rel in out.decode().split("\0"):
        if not rel or rel in skip:
            continue
        p = os.path.join(repo, rel)
        new_rel = transform(rel, rules, public, Counter())
        if new_rel != rel:
            renames.append((rel, new_rel))
        if os.path.islink(p) or not os.path.isfile(p):
            continue
        data = open(p, "rb").read()
        if b"\0" in data[:8000]:
            continue
        text = data.decode("utf-8", "surrogateescape")
        c = Counter()
        new = transform(text, rules, public, c)
        if new != text:
            files_changed += 1
            counts.update(c)
            if write:
                with open(p, "wb") as f:
                    f.write(new.encode("utf-8", "surrogateescape"))
    for old, new in renames:
        if write:
            subprocess.run(["git", "-C", repo, "mv", old, new], check=True)
    print(f"files changed {files_changed}; renamed {len(renames)}; replacements by rule:")
    for k in sorted(counts):
        print(f"  {k}\t{counts[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
