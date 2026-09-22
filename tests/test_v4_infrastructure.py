"""Offline adversarial checks for endpoint integrity, gold labels, and scoring."""
import importlib.util
import json
from itertools import product
from pathlib import Path
import sys
from unittest.mock import patch

import pytest
import ve
from ve_experiments.claude_cli import (ClaudeCLI, Controls, EndpointError, MODELS, command,
                                     empty_working_directory, isolated_env, parse_stream)

DIRECTORY = Path(__file__).resolve().parents[1]/"experiments/V4-fidelity"
sys.path.insert(0,str(DIRECTORY))
from generator import evaluate, sat, solutions, RULES, instantiate
from fidelity import environment, score, compare_translation, prompt
sys.path.remove(str(DIRECTORY))


def stream(model=MODELS["opus"], tools=None, stop="end_turn", tokens=100):
    message={"id":"m1","model":model,"content":[{"type":"thinking","thinking":""}]}
    return "\n".join(map(json.dumps,[
        {"type":"system","subtype":"init","model":model,"tools":tools or [],"mcp_servers":[],
         "agents":["claude","Explore","general-purpose","Plan"],"skills":[],"plugins":[]},
        {"type":"assistant","message":message},
        {"type":"assistant","message":{**message,"content":[{"type":"text","text":"OK"}]}},
        {"type":"result","subtype":"success","stop_reason":stop,"num_turns":1,"is_error":False,"result":"OK",
         "usage":{"input_tokens":tokens,"cache_creation_input_tokens":20,"cache_read_input_tokens":30,
                  "output_tokens":4,"output_tokens_details":{"thinking_tokens":0}},"modelUsage":{model:{}}}]))


def test_stream_chunks_and_cached_input_accounting():
    result=parse_stream(stream(),MODELS["opus"])
    assert result["input_tokens"]==150
    assert result["thinking_tokens_reported"]==0


@pytest.mark.parametrize("raw",[stream(model=MODELS["sonnet"]), stream(tools=["Bash"]),
                                 stream(stop="max_tokens"), stream()+"\n{}bad"])
def test_fail_closed_stream(raw):
    with pytest.raises((EndpointError,ValueError)):
        parse_stream(raw,MODELS["opus"])


def test_middle_message_model_fallback_rejected():
    rows=[json.loads(x) for x in stream().splitlines()]
    rows[1]["message"]["model"]=MODELS["sonnet"]
    with pytest.raises(EndpointError,match="model mismatch"):
        parse_stream("\n".join(map(json.dumps,rows)),MODELS["opus"])


def test_environment_and_command_isolate_ambient_config(tmp_path):
    c=Controls()
    env=isolated_env({"PATH":"/bin","ANTHROPIC_API_KEY":"secret","ANTHROPIC_BASE_URL":"bad",
                      "CLAUDE_CONFIG_DIR":"bad","HOME":"bad","MAX_THINKING_TOKENS":"9999"},
                     tmp_path/"config",tmp_path/"home","oauth",c)
    assert "ANTHROPIC_API_KEY" not in env and "ANTHROPIC_BASE_URL" not in env
    assert env["MAX_THINKING_TOKENS"]=="1024" and env["CLAUDE_CODE_MAX_RETRIES"]=="0"
    args=command("claude",c,"system",tmp_path/"mcp")
    for flag in ("--safe-mode","--strict-mcp-config","--no-session-persistence","--system-prompt"):
        assert flag in args
    assert args[args.index("--tools")+1]==""
    assert "--fallback-model" not in args


def test_stable_empty_directory_never_deletes_existing(tmp_path):
    directory=tmp_path/"empty"
    with empty_working_directory(directory) as p:
        assert list(p.iterdir())==[]
        with pytest.raises(FileExistsError):
            with empty_working_directory(directory): pass
    assert not directory.exists()


def test_ledger_resume_reject_drift_and_no_hidden_retry(tmp_path):
    binary=tmp_path/"claude";binary.write_text("fixture binary")
    controls=Controls(working_directory=str(tmp_path/"empty"))
    client=ClaudeCLI(tmp_path/"ledger.jsonl",controls,max_calls=3)
    process=type("Process",(),{"returncode":0,"stdout":stream(),"stderr":""})()
    with patch("ve_experiments.claude_cli.shutil.which",return_value=str(binary)), \
         patch("ve_experiments.claude_cli.subprocess.check_output",return_value=controls.cli_version), \
         patch("ve_experiments.claude_cli.oauth_token",return_value="private-token"), \
         patch("ve_experiments.claude_cli.check_context_date"), \
         patch("ve_experiments.claude_cli.subprocess.run",return_value=process) as run:
        row=client.sample("i","s","p",0)
        assert client.sample("i","s","p",0)==row
        assert run.call_count==1
        process.stdout=stream(tokens=101)
        with pytest.raises(EndpointError,match="overhead drift"):
            client.sample("i","s","p",1)
        with pytest.raises(EndpointError,match="previously started or failed"):
            client.sample("i","s","p",1)
        assert run.call_count==2
    rows=[json.loads(x) for x in client.ledger.read_text().splitlines()]
    assert [r["status"] for r in rows]==["started","ok","started","error"]
    assert rows[-1]["input_tokens"]==151
    assert "private-token" not in client.ledger.read_text()


def test_dpll_matches_exhaustive_rule_pool():
    for template in RULES["goal_rules"]+RULES["normal_rules"]:
        names=[f"a{i}" for i in range(template.count("[F]"))]
        formula=instantiate(template,names)
        for bits in product((False,True),repeat=len(names)):
            assignment=dict(zip(names,bits))
            premises=[n if v else ("¬",n) for n,v in assignment.items()]
            assert (sat(premises+[formula]) is not None)==evaluate(formula,assignment)


def small_item():
    env=environment({"p0":{"arguments":["person"],"description":"is amber"},
                     "p1":{"arguments":["person"],"description":"is bright"}})
    a=["unary","p0",["const","ada"]]; b=["unary","p1",["const","ada"]]
    item={"id":"test","environment":env,"label":"True","premises":[
        {"id":"p0","english":"Ada is amber.","gold_ast":a},
        {"id":"p1","english":"If Ada is amber, Ada is bright.","gold_ast":["implies",a,b]}],
        "query":{"english":"Ada is bright.","gold_ast":b}}
    sources=["@ada is p0.","if (@ada is p0), then (@ada is p1)."]
    response={"translations":[{"premise_id":p["id"],"english":p["english"],"ve":s} for p,s in zip(item["premises"],sources)],
        "query_ve":"@ada is p1.","answer":"True","graph":{"claims":[{"id":f"p{i}","ve":s} for i,s in enumerate(sources)]+[{"id":"goal","ve":"@ada is p1."}],
        "deductions":[{"id":"d0","premises":["p0","p1"],"conclusion":"goal"}],"root":"goal"}}
    return item,response


def test_faithful_certificate_and_gold_not_in_prompt():
    item,response=small_item(); result=score(item,response)
    assert result["faithful_mechanical"] and result["grounded_certificate"],result
    text=prompt(item)
    assert '"gold_ast"' not in text and '"label"' not in text


def test_certified_mistranslation_does_not_pass_fidelity():
    item,response=small_item()
    response["translations"][0]["ve"]="@ada is p1."
    response["graph"]["claims"][0]["ve"]="@ada is p1."
    result=score(item,response)
    assert result["certified_answer"]
    assert not result["faithful_mechanical"] and not result["grounded_certificate"]


def test_wrong_query_and_extra_assumption_cannot_pass():
    item,response=small_item()
    response["graph"]["claims"].append({"id":"cheat","ve":"@ada is p1."})
    response["graph"]["deductions"][0]["premises"]=["cheat"]
    result=score(item,response)
    assert result["certified_answer"] and not result["grounded_certificate"]
    response["graph"]["root"]="p0"
    assert not score(item,response)["certified_answer"]


def test_quantifier_negation_xor_regressions():
    item,_=small_item(); env=ve.Environment.from_dict(item["environment"])
    a=["unary","p0",["var",0]]
    r=compare_translation(env,"there exists person x0, (x0 is p0).",["forall","person",a])
    assert not r["faithful_mechanical"]
    a=["unary","p0",["const","ada"]];b=["unary","p1",["const","ada"]]
    xor=["and",["or",a,b],["not",["and",a,b]]]
    assert not compare_translation(env,"(@ada is p0) or (@ada is p1).",xor)["faithful_mechanical"]
    assert not compare_translation(env,"not (@ada is p0).",a)["faithful_mechanical"]


def test_frozen_60_labels_and_e0_fit():
    rows=[json.loads(x) for x in (DIRECTORY/"items.jsonl").read_text().splitlines()]
    assert len(rows)==60 and len({r["id"] for r in rows})==60
    for r in rows:
        assert all(not f["flags"] for f in r["e0_fit"])
        sk=r["skeleton"]
        yes=sat(sk["premises"]+[sk["query"]])
        no=sat(sk["premises"]+[("¬",sk["query"])])
        expected="Uncertain" if yes is not None and no is not None else "True" if yes is not None else "False"
        assert r["label"]==expected


def test_uncertain_requires_two_real_countermodels():
    item,response=small_item()
    item["premises"]=item["premises"][:1]
    item["label"]="Uncertain"
    response["translations"]=response["translations"][:1]
    response["answer"]="Uncertain"
    response["graph"]["claims"]=[response["graph"]["claims"][0],response["graph"]["claims"][-1]]
    response["graph"]["deductions"]=[]
    model={"complete":True,"domains":{"person":["a"]},"constants":{"ada":"a","ben":"a"},
           "relations":{"p0":[["a"]],"p1":[["a"]]}}
    response["countermodels"]={"query_true":model,"query_false":{**model,"relations":{"p0":[["a"]],"p1":[]}}}
    assert score(item,response)["grounded_certificate"]
    response["countermodels"]["query_false"]=model
    assert not score(item,response)["certified_answer"]


def test_predicate_argument_order_and_quantifier_scope():
    env=ve.Environment.from_dict(environment({"rel":{"arguments":["person","person"],"description":"trusts"}}))
    gold=["forall","person",["exists","person",["binary","rel",["var",1],["var",0]]]]
    submitted="there exists person x0, (for every person x1, (x1 rel x0))."
    assert not compare_translation(env,submitted,gold)["faithful_mechanical"]
    gold=["binary","rel",["const","ada"],["const","ben"]]
    assert not compare_translation(env,"@ben rel @ada.",gold)["faithful_mechanical"]


def test_equivalent_xor_reordering_is_accepted():
    item,_=small_item();env=ve.Environment.from_dict(item["environment"])
    a=["unary","p0",["const","ada"]];b=["unary","p1",["const","ada"]]
    gold=["and",["or",a,b],["not",["and",a,b]]]
    equivalent="(not ((@ada is p0) and (@ada is p1))) and ((@ada is p0) or (@ada is p1))."
    result=compare_translation(env,equivalent,gold)
    assert not result["exact_structure"] and result["faithful_mechanical"]


def test_allowed_rate_event_cannot_mask_fatal_model_or_control_drift():
    spec=importlib.util.spec_from_file_location('v4_run_b',DIRECTORY/'run_b.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    raw=json.dumps({'type':'rate_limit_event','rate_limit_info':{'status':'allowed'}})
    assert module.endpoint_failure("Served model mismatch: ['claude-opus-4-8']",raw)==(True,False)
    assert module.endpoint_failure('Input overhead drift for identical content',raw)==(True,False)
    assert module.endpoint_failure('CLI exit 1',raw)==(False,False)
    limited=raw+'\n'+json.dumps({'type':'result','is_error':True,'result':'rate_limit_error'})
    assert module.endpoint_failure('CLI exit 1',limited)==(False,True)
    # Fatal integrity errors retain priority even when a real rate failure co-occurs.
    assert module.endpoint_failure('Served model mismatch',limited)==(True,True)


def test_stopped_study_never_calls_backend():
    spec=importlib.util.spec_from_file_location('v4_run_b_stopped',DIRECTORY/'run_b.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with patch.object(Path,'exists',return_value=True), patch.object(ClaudeCLI,'sample',side_effect=AssertionError('must not spend')):
        with pytest.raises(EndpointError,match='permanently stopped'):
            module.main()
