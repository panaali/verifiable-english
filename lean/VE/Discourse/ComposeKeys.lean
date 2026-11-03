/-! # The key order of `composedJson`'s object (docs/spec/discourse.md 14.5)

An object built from a list of fields orders its keys by `compare`; `conditions_retained` (`VE.Discourse.Compose`)
reads the object's tree through these facts, which `simp` uses definitionally. -/
namespace VE.Discourse

theorem cmp_i_d : compare "inner" "document_id" = .gt := rfl
theorem cmp_ir_d : compare "inner_report_id" "document_id" = .gt := rfl
theorem cmp_ir_i : compare "inner_report_id" "inner" = .gt := rfl
theorem cmp_rf_i : compare "references" "inner" = .gt := rfl
theorem cmp_rf_ir : compare "references" "inner_report_id" = .gt := rfl
theorem cmp_rp_i : compare "report_id" "inner" = .gt := rfl
theorem cmp_rp_ir : compare "report_id" "inner_report_id" = .gt := rfl
theorem cmp_rp_rf : compare "report_id" "references" = .gt := rfl

end VE.Discourse
