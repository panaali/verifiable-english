use serde_json::json;
use ve_core::quantity_case;

fn environment() -> serde_json::Value {
    json!({"language":"ve.core@0.2",
      "profiles":["order@0","relational-fol@0","time@0"],
      "spec_revision":"ve-v0.2-expand2-2026-09-25",
      "vocabulary":{"sorts":{},"predicates":{},"constants":{}},
      "unit_schema":"ve-units@1",
      "units":{"bp":{"scale":"100","display":{"kind":"percent"}},
               "usd_cent":{"scale":"100","display":{"kind":"money","currency":"USD"}},
               "day":{"scale":"1","display":{"kind":"iso_date"}},
               "elapsed_day":{"scale":"1","display":{"kind":"decimal","label":"days"}}}})
}
fn case(formula: serde_json::Value) -> serde_json::Value {
    json!({"id":"w6","kind":"quantity","environment":environment(),
           "quantity":{"format":"ve-quantity@1","formula":formula}})
}
#[test]
fn exact_grid_and_nominal_tags() {
    let out = quantity_case(&case(json!([
        "lt",
        ["decimal", "bp", "3.75"],
        ["decimal", "bp", "4.00"]
    ])))
    .unwrap();
    assert_eq!(
        out["Q"],
        json!(["lt", ["num", "bp", "375"], ["num", "bp", "400"]])
    );
    assert_eq!(out["core"], json!(["lt", ["num", "375"], ["num", "400"]]));
    let err = quantity_case(&case(json!([
        "eq",
        ["decimal", "bp", "3.75"],
        ["decimal", "usd_cent", "3.75"]
    ])))
    .unwrap_err();
    assert!(err.message.contains("UnitMismatch(bp,usd_cent)"));
    let err = quantity_case(&case(json!([
        "eq",
        ["decimal", "bp", "3.755"],
        ["num", "bp", "375"]
    ])))
    .unwrap_err();
    assert!(err.message.contains("UnitPrecision(bp, scale=100)"));
}
#[test]
fn date_and_claimed_q_correspondence() {
    let out = quantity_case(&case(json!([
        "shift_days",
        ["date", "2026-09-17"],
        ["date", "2026-09-16"],
        "1"
    ])))
    .unwrap();
    assert_eq!(
        out["Q"],
        json!([
            "shift_days",
            ["num", "day", "20713"],
            ["num", "day", "20712"],
            "1"
        ])
    );
    let mut forged = case(json!([
        "eq",
        ["decimal", "bp", "3.75"],
        ["num", "bp", "375"]
    ]));
    forged["quantity"]["Q"] = json!(["eq", ["num", "bp", "376"], ["num", "bp", "375"]]);
    assert!(
        quantity_case(&forged)
            .unwrap_err()
            .message
            .contains("Q differs")
    );
}

#[test]
fn user_sort_counting_expansion_is_checked_and_evaluated() {
    let mut input = case(json!(["exists", "item", ["unary", "p", ["var", 0]]]));
    input["environment"]["vocabulary"]["sorts"] = json!({"item":{"description":"an item"}});
    input["environment"]["vocabulary"]["predicates"] =
        json!({"p":{"arguments":["item"],"description":"P"}});
    input["model"] = json!({"complete":true,"domains":{"item":["e1"]},
        "constants":{},"relations":{"p":[["e1"]]}});
    let result = quantity_case(&input).unwrap();
    assert_eq!(result["value"], true);
    assert_eq!(
        result["Q"],
        json!(["exists", "item", ["unary", "p", ["var", 0]]])
    );
}
