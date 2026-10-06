import VE.Service.Protocol
import ResponseShape

/-! The source of `ve/backends/lean_service_schema/envelope.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Envelope
open Lean ResponseShape

def ok : Shape :=
  n [
    obj,
    .required ["id", "status", "mode", "results", "counts"],
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("mode", n [str, .equals "/mode"]),
      ("results", n [arr, .length "/cases", .rows (ref "#/$defs/bound")]),
      ("counts", n [
        obj,
        .required ["cases", "bytes", "errors"],
        closed [
          ("cases", n [.type ["integer"], .count "/cases"]),
          ("bytes", n [.type ["integer"], .equals "/bytes"]),
          ("errors", ref "common.json#/$defs/nat")]])],
    .countWhere
      "/results"
      (n [obj, props [("result", n [obj, .required ["status"], props [("status", constS "error")]])]])
      "/counts/errors"]

def bound : Shape :=
  c
    "Service.Protocol.bound: the result's position, the digest of its case and the runner's result for that case; beside a rejection (an error row with a text error), its code and the generator an InvalidModel(generator) message names (Service.Protocol.coding), beside any other result neither."
    [
      obj,
      .required ["index", "digest", "result"],
      closed [
        ("index", .index),
        ("digest", .digest),
        ("result", .row),
        ("code", ref "common.json#/$defs/code"),
        ("generator", str)],
      .ite
        (props [
          ("result", n [obj, .required ["status", "error"], props [("status", constS "error"), ("error", str)]])])
        (.required ["code"])
        (.not (.anyOf [.required ["code"], .required ["generator"]]))]

def error : Shape :=
  c
    "Service.Protocol.requestError: a request error is bound like a response, to the nonce, the mode and the digests of the cases as sent (null when the cases text does not split into cases). The unbound lineError answers no request."
    [
      obj,
      .required ["id", "status", "mode", "digests", "error", "code"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "error"),
        ("mode", n [str, .equals "/mode"]),
        ("digests", .equals "/digests"),
        ("error", ref "common.json#/$defs/text"),
        ("code", ref "common.json#/$defs/code")]]

def handshake : Shape :=
  c "Service.Protocol.handshake: this protocol, every mode and at least the client's limits." [
    obj,
    .required ["service", "protocol", "modes", "codes", "limits", "handles"],
    closed [
      ("service", constS "ve-lean@1"),
      ("protocol", .const (toJson (2 : Int))),
      ("lean", str),
      ("modes", n [
        ref "common.json#/$defs/strings",
        .allOf (VE.Service.modes.map fun m => .contains (constS m.name))]),
      ("codes", c
        "Service.Protocol.rejectionCodes: exactly the code domain of the rows (common.json code), so a service with another code list is refused at its start."
        [.const (toJson VE.Service.rejectionCodes)]),
      ("limits", n [
        obj,
        .required ["max_line_bytes", "max_cases", "json_depth"],
        closed [
          ("max_line_bytes", n [.type ["integer"], .minimum VE.Service.maxLineBytes]),
          ("max_cases", n [.type ["integer"], .minimum VE.Service.maxCases]),
          ("json_depth", n [.type ["integer"], .minimum 256])]]),
      ("handles", c
        "Service.Protocol.Handles: the case member naming a handle and the table's bounds, exactly: the client keeps the same table (Handles.insert)."
        [obj,
          .required ["member", "max", "max_bytes"],
          closed [
            ("member", constS VE.Service.handleKey),
            ("max", .const (toJson VE.Service.maxHandles)),
            ("max_bytes", .const (toJson VE.Service.maxHandleBytes))]])]]

def response : Shape :=
  .anyOf [ref "#/$defs/ok", ref "#/$defs/error"]

def file : File where
  name := "envelope.json"
  comment := some "Service.Protocol lines. `handshake` is the first line; the context of `response` is the request: {id (the nonce), mode, cases (decoded), digests (SHA-256 of each case text as sent, null when the cases text does not split into cases), bytes (trimmed cases text)}. A bound request error is kept; any other mismatch is operational. Binding: the response echoes the nonce and mode, and result i is {index: i, digest: the digest of case i, result}, so omitted, reordered, duplicated and substituted results are rejected without semantic checks; a request error echoes the nonce, the mode and every case digest (docs/spec/lean-service.md, threat model). Every rejection, a request error or a result whose status is error, carries `code` (Service.Protocol.rejectionCode)."
  top := [("handshake", handshake), ("response", response)]
  defs := [
    ("ok", .schema ok),
    ("bound", .schema bound),
    ("error", .schema error)]

end ResponseShape.Schemas.Envelope
