"""rights-cfr-5 evidence: parse_line at the base commit against the worktree, on header variants.

Usage: uv run python docs/rights/rights-cfr-5/header_delta.py > docs/rights/rights-cfr-5/header-delta.json
Writes every input whose answer differs (base 49f1682dc, ve/surface/rights.py) and the count of equal ones."""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

BASE = "49f1682dcb7e4aa304a86a3c8c6e240d1ff7752f"
PARTIES = ("operator", "user")
BODY = "Every state must protect each person."
VARIANTS = ["", " ()", " (exception to rule 1)", " (exception to rules 1)",
            " (exception to rule 1; user may turn off)", " (user may turn off; exception to rule 1)",
            " (user may turn off;)", "  (user may turn off)", " (user  may turn off)", " (User may turn off)",
            " (user may turn it off)", " (operator, user may turn off)", " (user may turn off) ",
            "(user may turn off)", " [user may turn off]", " (user may turn off)", "\t(user may turn off)",
            " (user may turn off)", " (user may turn off)\r", " （user may turn off）",
            " (user and operator may turn off)", " (guest may turn off)", " (user and user may turn off)",
            " (user may turn off)", " (operator and user may turn off)"]


def answer(module, env, source):
    try:
        return {"accepted": module.parse_line(env, source, name="protect")["norm"].get("alterable", [])}
    except Exception as error:  # the answer is the error's class and text
        return {"refused": f"{type(error).__name__}: {error}"}


def main():
    import ve.surface.rights as head
    from tests.test_rights import switch_env
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "rights_base.py"
        path.write_bytes(subprocess.run(["git", "show", f"{BASE}:ve/surface/rights.py"],
                                        check=True, capture_output=True).stdout)
        spec = importlib.util.spec_from_file_location("ve.surface.rights_base", path)
        base = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(base)
        env = switch_env(PARTIES)
        rows, same = [], 0
        for variant in VARIANTS:
            for tail in (". " + BODY, ". "):
                source = "Claim of right life" + variant + tail
                before, after = answer(base, env, source), answer(head, env, source)
                if before == after:
                    same += 1
                else:
                    rows.append({"source": source, "base": before, "head": after})
    json.dump({"base": BASE, "parties": list(PARTIES), "equal": same, "differ": rows}, sys.stdout,
              indent=1, ensure_ascii=True)
    print()


if __name__ == "__main__":
    main()
