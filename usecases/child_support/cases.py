"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). SAME-FAMILY.

Encoder: dri-statute-corpus-child-support-1123 (Opus 5.5), after the translation was committed (a7f7140090, 20:21Z).
Each case: "parent" (x, the non-resident parent), "children", "persons" (everyone else the facts name: persons with care,
spouses, civil partners, people lived with), "benefits" (each benefit, pension or allowance named for the week),
"facts" (unary facts true of an item), "pairs" ("<a>@<b>" -> binary facts true of the pair; every other one false, encode
C1), "ints" (stated amounts and nights), "questions" (qid -> item and form: rate = Q1, amount = Q2, share = Q3),
"judgement" (anything the encoder decided beyond copying a stated fact: listed as "encoder judgement").
Standing readings (every case): "no maintenance order / agreement" -> morder, agree false; "no regulations under 10A",
"no prescribed description under 10C(2)(b)", "not a variation" -> those facts false (the writer's fixed facts); "receives
<benefit> for the week" -> paid in respect of the week (encode C5); child benefit named as received is also a benefit
item, prescribed for neither 4(1)(b) nor 4(1)(c) where the case says so.
PROBES: out-of-scope cases (every answer UNSUPPORTED).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "a4b2b70632ddfe58eaa05c556006638bc30c3589a998c7f3d9c527cd3a386858"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

QC = ["qcalc", "childof"]          # a qualifying child of the calculation (stated), the parent's child
OTHER = []                          # a child who is not a qualifying child, no arrangement


def case(cid, parent, inc, qc, qs, others=(), persons=(), benefits=(), facts=None, pairs=None, ints=None,
         nights=None, judgement=()):
    """qc: {child: person with care}; qs: [(item, form)] numbered cid-1, cid-2, ...; nights: {child: n}."""
    children = list(qc) + list(others)
    people = []
    for w in list(qc.values()) + list(persons):
        if w not in people:
            people.append(w)
    f = {ch: list(QC) for ch in qc}
    for item, more in (facts or {}).items():
        f.setdefault(item, [])
        f[item] = sorted(set(f[item]) | set(more))
    pr = {f"{ch}@{w}": ["pwc"] for ch, w in qc.items()}
    for kk, more in (pairs or {}).items():
        pr[kk] = sorted(set(pr.get(kk, [])) | set(more))
    i = {f"inc_{parent}": inc}
    i.update({f"nights_{ch}": str(n) for ch, n in (nights or {}).items()})
    i.update(ints or {})
    return {"id": cid, "parent": parent, "children": children, "persons": people, "benefits": list(benefits),
            "facts": f, "pairs": pr, "ints": i,
            "questions": [{"qid": f"{cid}-{n}", "item": it, "form": fm} for n, (it, fm) in enumerate(qs, 1)],
            "judgement": list(judgement)}


def rate(x): return (x, "rate")
def amt(w): return (w, "amount")
def share(ch): return (ch, "share")


CHB = {"chb": []}  # child benefit as a benefit item: prescribed for neither 4(1)(b) nor 4(1)(c)

CASES = [
    case("M001", "sam", "640.00", {"mia": "jordan"}, [rate("sam"), amt("jordan"), share("mia")], nights={"mia": 51}),
    case("M002", "ravi", "800.00", {"ruby": "priya", "noah": "femi"}, [rate("ravi"), amt("priya"), amt("femi")]),
    case("M003", "tom", "801.00", {"lucy": "beatrice"}, [rate("tom"), amt("beatrice")]),
    case("M004", "oscar", "799.00", {"ada": "helen", "ben": "helen", "cora": "helen"}, [rate("oscar"), amt("helen")],
         others=["dylan"], facts={"dylan": ["childof"]}),
    case("M005", "gareth", "1500.00", {"ivy": "moira", "jack": "moira", "kit": "moira", "luke": "nadia"},
         [rate("gareth"), amt("moira"), amt("nadia")]),
    case("M006", "ian", "3000.00", {"owen": "petra"}, [rate("ian"), amt("petra"), share("owen")], nights={"owen": 104}),
    case("M007", "callum", "3001.00", {"rosa": "tara", "seth": "tara"},
         [rate("callum"), amt("tara"), share("rosa"), share("seth")], nights={"rosa": 156, "seth": 174}),
    case("M008", "dmitri", "2999.00", {"uma": "vera"}, [rate("dmitri"), amt("vera")]),
    case("M009", "edmund", "5000.00", {"will": "zara", "xena": "zara", "yusuf": "zara"}, [rate("edmund"), amt("zara")],
         others=["iris"], persons=["hana"], benefits=["chb"], facts=CHB,
         pairs={"hana@iris": ["cbpaid"], "hana@chb": ["paid"], "edmund@hana": ["married", "samehh"]}),
    case("M010", "leo", "1000.00", {"amber": "chloe", "bruno": "chloe"}, [rate("leo"), amt("chloe")],
         others=["dara", "eli"], benefits=["chb"], facts=CHB,
         pairs={"leo@dara": ["cbpaid"], "leo@eli": ["cbpaid"], "leo@chb": ["paid"]}),
    case("M011", "fern", "900.00", {"gil": "hugo"}, [rate("fern"), amt("hugo")], others=["jonah"], persons=["alex"],
         benefits=["chb"], facts=CHB,
         pairs={"alex@jonah": ["cbpaid"], "alex@chb": ["paid"], "fern@alex": ["livetog"]}),
    case("M012", "hassan", "500.00", {"ella": "carla", "finn": "carla", "gus": "carla"},
         [rate("hassan"), amt("carla"), share("ella"), share("finn"), share("gus")],
         others=["jade", "kai", "lena"], persons=["ines"], benefits=["chb"], facts=CHB,
         pairs={"hassan@jade": ["cbpaid"], "hassan@kai": ["cbpaid"], "ines@lena": ["cbpaid"], "hassan@chb": ["paid"],
                "ines@chb": ["paid"], "hassan@ines": ["married", "samehh"]},
         nights={"ella": 175, "finn": 52, "gus": 0}),
    case("M013", "quentin", "700.00", {"rhea": "stella"}, [rate("quentin"), amt("stella"), share("rhea")],
         others=["tess", "ugo"], persons=["robin"], benefits=["chb"], facts=CHB,
         pairs={"robin@tess": ["cbpaid"], "robin@chb": ["paid"]}, nights={"rhea": 156},
         judgement=["Quentin and Robin 'share a house': not stated to be members of the same household; samehh left "
                    "false (no effect: they are neither married nor civil partners, nor living together)"]),
    case("M014", "owen", "700.00", {"vince": "yasmin", "wren": "yasmin"}, [rate("owen"), amt("yasmin")],
         others=["zak"], persons=["grace"], benefits=["chb", "ben"], facts={**CHB, "ben": ["b41c"]},
         pairs={"grace@zak": ["cbpaid"], "grace@chb": ["paid"], "grace@ben": ["paid"], "owen@grace": ["married"]}),
    case("M015", "karim", "1250.00", {"nabil": "sara", "omar": "sara"}, [rate("karim"), amt("sara")],
         others=["ruqaya", "samir", "tariq"], persons=["amina", "layla"], benefits=["chb"], facts=CHB,
         pairs={"amina@ruqaya": ["cbpaid"], "layla@samir": ["cbpaid"], "layla@tariq": ["cbpaid"], "amina@chb": ["paid"],
                "layla@chb": ["paid"], "karim@amina": ["polyg", "oppsex", "samehh", "married"],
                "karim@layla": ["polyg", "oppsex", "samehh", "married"]},
         judgement=["a husband by virtue of a polygamous marriage read as also married to each wife (10C(5)(a)); the "
                    "partner test holds by 10C(4)(b) on the stated facts alone"]),
    case("M016", "una", "200.00", {"vic": "wes"}, [rate("una"), amt("wes"), share("vic")], nights={"vic": 175},
         ints={"redrate_una": "19.80"}),
    case("M017", "xavier", "199.00", {"yara": "anya", "zeb": "anya"},
         [rate("xavier"), amt("anya"), share("yara"), share("zeb")], nights={"yara": 52, "zeb": 0},
         ints={"redrate_xavier": "21.00"}),
    case("M018", "bianca", "101.00", {"cyrus": "emeka", "delia": "flora"},
         [rate("bianca"), amt("emeka"), amt("flora"), share("cyrus"), share("delia")],
         nights={"cyrus": 156, "delia": 156}, ints={"redrate_bianca": "11.20"}),
    case("M019", "glen", "100.00", {"holly": "imran"}, [rate("glen"), amt("imran")], ints={"redrate_glen": "7.10"}),
    case("M020", "jules", "150.00", {"kira": "lars"}, [rate("jules"), amt("lars")], benefits=["pen"],
         facts={"pen": ["b41b"]}, pairs={"jules@pen": ["paid"]}, ints={"redrate_jules": "15.00"}),
    case("M021", "milo", "350.00", {"nell": "otto"}, [rate("milo"), amt("otto")], persons=["ellen"], benefits=["ben"],
         facts={"ben": ["b41c"]}, pairs={"ellen@ben": ["paid"], "milo@ellen": ["married", "samehh"]}),
    case("M022", "piers", "420.00", {"quinn": "rosalind"}, [rate("piers"), amt("rosalind"), share("quinn")],
         persons=["tess"], benefits=["alw"], facts={"alw": ["b41b"]},
         pairs={"tess@alw": ["paid"], "piers@tess": ["married", "samehh"]}, nights={"quinn": 155}),
    case("M023", "saul", "300.00", {"tilda": "ursula"}, [rate("saul"), amt("ursula")], benefits=["alw"],
         facts={"alw": ["b41b"]}, pairs={"saul@alw": ["due"]},
         judgement=["'an amount of it is due to be paid to Saul in respect of that week, payment held back' -> due to be "
                    "paid in respect of the week (10C(3)); not paid"]),
    case("M024", "victor", "350.00", {"wanda": "yves"}, [rate("victor"), amt("yves"), share("wanda")],
         benefits=["ben"], facts={"ben": ["b41b"]}, nights={"wanda": 103},
         judgement=["a benefit paid during the week in respect only of an earlier week -> neither paid nor due to be paid "
                    "in respect of the week (10C(3))"]),
    case("M025", "dev", "60.00", {"asha": "bina"}, [rate("dev"), amt("bina")], persons=["kim"], benefits=["ben"],
         facts={"ben": ["b41c"], "kim": ["alsonrp", "calcinforce"]},
         pairs={"kim@ben": ["paid"], "dev@kim": ["married", "samehh"]}, ints={"flatamt_dev": "3.50"}),
    case("M026", "nico", "400.00", {"dina": "emil"}, [rate("nico"), amt("emil")], persons=["kerry"], benefits=["ben"],
         facts={"ben": ["b41c"], "kerry": ["alsonrp"]}, pairs={"kerry@ben": ["paid"], "nico@kerry": ["livetog"]},
         ints={"flatamt_nico": "3.50"}),
    case("M027", "jamie", "90.00", {"gwen": "iona", "hal": "iona"}, [rate("jamie"), amt("iona"), share("gwen")],
         persons=["lou"], benefits=["ben"], facts={"ben": ["b41c"], "lou": ["alsonrp", "calcinforce"]},
         pairs={"jamie@ben": ["paid"], "jamie@lou": ["civil", "samehh"]}, nights={"gwen": 60, "hal": 0},
         ints={"flatamt_jamie": "4.00"}),
    case("M028", "kofi", "250.00", {"ava": "beth", "cal": "dana"},
         [rate("kofi"), amt("beth"), amt("dana"), share("ava")], benefits=["ben"], facts={"ben": ["b41b"]},
         pairs={"kofi@ben": ["paid"]}, nights={"ava": 52, "cal": 0}),
    case("M029", "lydia", "80.00", {"mark": "nate"}, [rate("lydia"), amt("nate"), share("mark")], nights={"mark": 200}),
    case("M030", "ollie", "6.99", {"pia": "rory"}, [rate("ollie"), amt("rory")]),
    case("M031", "selma", "2000.00", {"theo": "uri"}, [rate("selma"), amt("uri")], benefits=["ben"],
         facts={"selma": ["presc5a"], "ben": ["b41b"]}, pairs={"selma@ben": ["paid"]}),
    case("M032", "wilf", "7.00", {"xia": "yoel"}, [rate("wilf"), amt("yoel")]),
    case("M033", "barney", "600.00", {"zoe": "ruth", "max": "ian"},
         [rate("barney"), amt("ruth"), amt("ian"), share("zoe"), share("max")], others=["theo"],
         facts={"theo": ["childof", "morder", "habuk"]}, nights={"zoe": 175, "max": 0},
         judgement=["Theo 'habitually resident in England' -> habitually resident in the United Kingdom"]),
    case("M034", "caspar", "200.00", {"dot": "erin"}, [rate("caspar"), amt("erin")],
         others=["hc1", "hc2", "hc3", "fergus", "greer", "hamish", "isla", "jock"], benefits=["chb"],
         facts={**CHB, **{ch: ["childof", "morder", "habuk"] for ch in ("fergus", "greer")},
                **{ch: ["childof", "agree", "agree_presc", "habuk"] for ch in ("hamish", "isla", "jock")}},
         pairs={"caspar@hc1": ["cbpaid"], "caspar@hc2": ["cbpaid"], "caspar@hc3": ["cbpaid"], "caspar@chb": ["paid"]},
         ints={"redrate_caspar": "19.80"},
         judgement=["the three unnamed household children entered as items hc1-hc3; 'liable to pay aliment under a "
                    "maintenance order' -> morder; Scotland and Wales -> habitually resident in the United Kingdom"]),
    case("M035", "felix", "500.00", {"gemma": "hattie"}, [rate("felix"), amt("hattie")], others=["elodie", "toby"],
         facts={"elodie": ["childof", "morder"], "toby": ["childof", "agree", "habuk"]},
         judgement=["Elodie 'habitually resident in France' -> not in the United Kingdom; Toby 'habitually resident in "
                    "England' -> in the United Kingdom"]),
]

UNSUPPORTED = {}
PROBES = {
    "M036": "Northern Ireland law: out of scope", "M037": "old-scheme assessment (2001): out of scope",
    "M038": "variation on special expenses: out of scope", "M039": "gross weekly income from pay slips: out of scope",
    "M040": "whether a benefit is prescribed, not stated: out of scope",
    "M041": "figures changed by regulations under para. 10A: out of scope",
    "M042": "gross weekly income from a tax return: out of scope",
    "M043": "whether a foreign pension is prescribed, not stated: out of scope",
    "M044": "old-scheme assessment (2010): out of scope", "M045": "variation on unearned income: out of scope",
}
PROBE_QIDS = {"M036": ["M036-1", "M036-2"], "M037": ["M037-1"], "M038": ["M038-1"], "M039": ["M039-1", "M039-2"],
              "M040": ["M040-1", "M040-2"], "M041": ["M041-1"], "M042": ["M042-1"], "M043": ["M043-1"],
              "M044": ["M044-1", "M044-2"], "M045": ["M045-1"]}
