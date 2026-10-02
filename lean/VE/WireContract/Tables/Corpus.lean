/- The engine corpus contracts inner@0, demo@0 and defer@0, revision 1, of docs/spec/wire-contract.md 8.1,
   written by hand in the grammar of a generated table module (spec 7.1). This module is to be replaced by
   the output of tools/wire_contract.py for conformance/wire-contract/contracts/, which then must equal it. -/
import VE.WireContract.Table

namespace VE.WireContract.Tables.Corpus.Inner
def table : VE.WireContract.Table :=
  { contract := "inner@0", revision := 1, residual := ("INNER_BAD", "InvalidInput"),
    phases := [
      { name := "body", entries := [
        .check {
          id := "b1", loc := ⟨.root, [.tok "x"]⟩, guard := [], kind := .hasType [.atom .integer],
          code := "INNER_BAD", cls := "InvalidInput", text := [.lit "Inner: x is ", .arg "value" .json],
          args := [], inherited := false },
        .each "ys" ⟨.root, [.tok "ys", .star]⟩ [] [
          .check {
            id := "b2", loc := ⟨.item 0, []⟩, guard := [], kind := .hasType [.atom .string],
            code := "INNER_BAD", cls := "InvalidInput", text := [.lit "Inner: y ", .arg "index" .index],
            args := [], inherited := false }]] }] }
end VE.WireContract.Tables.Corpus.Inner

namespace VE.WireContract.Tables.Corpus.Demo
def table : VE.WireContract.Table :=
  { contract := "demo@0", revision := 1, residual := ("DEMO_INVALID_INPUT", "InvalidInput"),
    phases := [
      { name := "shape", entries := [
        .check {
          id := "1.1", loc := ⟨.root, [.tok "doc"]⟩, guard := [],
          kind := .keys ["items", "mode", "refs"] ["note", "owner", "part", "seed", "table"],
          code := "DEMO_SHAPE", cls := "InvalidInput", text := [.lit "Shape: document"], args := [],
          inherited := false },
        .check {
          id := "1.2", loc := ⟨.root, [.tok "doc", .tok "items"]⟩, guard := [],
          kind := .hasType [.atom .array], code := "DEMO_SHAPE", cls := "InvalidInput",
          text := [.lit "Shape: items"], args := [], inherited := false },
        .check {
          id := "1.3", loc := ⟨.root, [.tok "doc", .tok "items"]⟩, guard := [], kind := .maxItems 3,
          code := "DEMO_LIMIT", cls := "ResourceLimit",
          text := [.lit "Limit: ", .arg "count" .raw, .lit " items, at most ", .arg "limit" .raw], args := [],
          inherited := false },
        .check {
          id := "1.4", loc := ⟨.root, [.tok "doc", .tok "mode"]⟩, guard := [],
          kind := .oneOf [.str "open", .str "closed"], code := "DEMO_SHAPE", cls := "InvalidInput",
          text := [.lit "Shape: mode ", .arg "value" .json], args := [], inherited := false },
        .check {
          id := "1.5", loc := ⟨.root, [.tok "doc", .tok "refs"]⟩, guard := [],
          kind := .hasType [.arrayOf .string], code := "DEMO_SHAPE", cls := "InvalidInput",
          text := [.lit "Shape: refs"], args := [], inherited := false },
        .check {
          id := "1.6", loc := ⟨.root, [.tok "doc"]⟩,
          guard := [.equals ⟨.root, [.tok "doc", .tok "mode"]⟩ (.str "closed")], kind := .excludesMember "note",
          code := "DEMO_SHAPE", cls := "InvalidInput", text := [.lit "Shape: a closed document has a note"],
          args := [], inherited := false },
        .check {
          id := "1.7", loc := ⟨.root, [.tok "doc"]⟩,
          guard := [.equals ⟨.root, [.tok "doc", .tok "mode"]⟩ (.str "open")], kind := .requiresMember "owner",
          code := "DEMO_SHAPE", cls := "InvalidInput", text := [.lit "Shape: an open document has no owner"],
          args := [], inherited := false },
        .check {
          id := "1.8", loc := ⟨.root, [.tok "doc", .tok "owner"]⟩, guard := [], kind := .const (.str "root"),
          code := "DEMO_SHAPE", cls := "InvalidInput", text := [.lit "Shape: owner ", .arg "value" .raw],
          args := [], inherited := false },
        .check {
          id := "1.9", loc := ⟨.root, [.tok "doc", .tok "refs"]⟩, guard := [],
          kind := .excludesItem (.str "self"), code := "DEMO_SHAPE", cls := "InvalidInput",
          text := [.lit "Shape: refs names self"], args := [], inherited := false },
        .check {
          id := "1.10", loc := ⟨.root, [.tok "doc", .tok "refs"]⟩,
          guard := [.isType ⟨.root, [.tok "doc", .tok "note"]⟩ [.atom .string]], kind := .requiresItem (.str "a"),
          code := "DEMO_SHAPE", cls := "InvalidInput", text := [.lit "Shape: a note needs the ref a"],
          args := [], inherited := false }] },
      { name := "items", entries := [
        .each "items-a" ⟨.root, [.tok "doc", .tok "items", .star]⟩ [] [
          .check {
            id := "2.1a", loc := ⟨.item 0, []⟩, guard := [], kind := .exactKeys ["name", "tags"],
            code := "DEMO_SHAPE", cls := "InvalidInput", text := [.lit "Shape: item ", .arg "index" .raw],
            args := [], inherited := false },
          .check {
            id := "2.1b", loc := ⟨.item 0, [.tok "name"]⟩, guard := [],
            kind := .name ⟨some [(97, 122)], some [(97, 122), (48, 57), (95, 95)], none, some 8, [], ["__"], none⟩
              false,
            code := "DEMO_NAME", cls := "InvalidInput", text := [.lit "Name: ", .arg "value" .raw], args := [],
            inherited := false },
          .check {
            id := "2.1c", loc := ⟨.item 0, [.tok "name"]⟩, guard := [], kind := .uniqueSoFar,
            code := "DEMO_DUPLICATE", cls := "DuplicateDeclaration", text := [.lit "Duplicate: ", .arg "value" .raw],
            args := [], inherited := false },
          .check {
            id := "2.1d", loc := ⟨.item 0, [.tok "tags"]⟩, guard := [], kind := .hasType [.arrayOf .string],
            code := "DEMO_SHAPE", cls := "InvalidInput", text := [.lit "Shape: tags of ", .arg "name" .raw],
            args := [("name", ⟨.item 0, [.tok "name"]⟩)], inherited := false }],
        .each "items-b" ⟨.root, [.tok "doc", .tok "items", .star]⟩ [] [
          .check {
            id := "2.2a", loc := ⟨.item 0, [.tok "tags"]⟩, guard := [], kind := .sortedUnique,
            code := "DEMO_SHAPE", cls := "InvalidInput",
            text := [.lit "Shape: tags of ", .arg "name" .raw, .lit " are not sorted"],
            args := [("name", ⟨.item 0, [.tok "name"]⟩)], inherited := false },
          .each "tags" ⟨.item 0, [.tok "tags", .star]⟩ [] [
            .check {
              id := "2.2b", loc := ⟨.item 0, []⟩, guard := [], kind := .maxBytes 2,
              code := "DEMO_LIMIT", cls := "ResourceLimit",
              text := [.lit "Limit: tag ", .arg "value" .raw, .lit " of ", .arg "name" .raw],
              args := [("name", ⟨.item 1, [.tok "name"]⟩)], inherited := false }]],
        .each "table" ⟨.root, [.tok "doc", .tok "table", .star]⟩ [] [
          .check {
            id := "2.3a", loc := ⟨.item 0, []⟩, guard := [],
            kind := .name ⟨some [(97, 122)], some [(97, 122), (48, 57), (95, 95)], none, some 8, [], ["__"], none⟩
              true,
            code := "DEMO_NAME", cls := "InvalidInput", text := [.lit "Name: ", .arg "key" .raw], args := [],
            inherited := false },
          .check {
            id := "2.3b", loc := ⟨.item 0, []⟩, guard := [], kind := .hasType [.atom .integer],
            code := "DEMO_SHAPE", cls := "InvalidInput",
            text := [.lit "Shape: table entry ", .arg "key" .raw, .lit " is ", .arg "value" .json], args := [],
            inherited := false }]] },
      { name := "references", entries := [
        .each "refs" ⟨.root, [.tok "doc", .tok "refs", .star]⟩ [] [
          .check {
            id := "3.1", loc := ⟨.item 0, []⟩, guard := [],
            kind := .declaredIn ⟨.root, [.tok "doc", .tok "items", .star, .tok "name"]⟩,
            code := "DEMO_UNKNOWN", cls := "UnknownSymbol", text := [.lit "Unknown: ", .arg "value" .raw],
            args := [], inherited := false }],
        .check {
          id := "3.2", loc := ⟨.root, []⟩, guard := [],
          kind := .maxCount ⟨.root, [.tok "doc", .tok "items", .star, .tok "tags", .star]⟩ 4,
          code := "DEMO_LIMIT", cls := "ResourceLimit", text := [.lit "Limit: ", .arg "count" .raw, .lit " tags"],
          args := [], inherited := false },
        .scope "3.3" ⟨.root, [.tok "doc", .tok "part"]⟩ none none [
          .check {
            id := "b1", loc := ⟨.root, [.tok "x"]⟩, guard := [], kind := .hasType [.atom .integer],
            code := "INNER_BAD", cls := "InvalidInput", text := [.lit "Inner: x is ", .arg "value" .json],
            args := [], inherited := false },
          .each "ys" ⟨.root, [.tok "ys", .star]⟩ [] [
            .check {
              id := "b2", loc := ⟨.item 0, []⟩, guard := [], kind := .hasType [.atom .string],
              code := "INNER_BAD", cls := "InvalidInput", text := [.lit "Inner: y ", .arg "index" .index],
              args := [], inherited := false }]],
        .scope "3.4" ⟨.root, [.tok "doc"]⟩ (some "part_view") (some ("DEMO_SEMANTIC", "InvalidInput")) [
          .check {
            id := "b1", loc := ⟨.root, [.tok "x"]⟩, guard := [], kind := .hasType [.atom .integer],
            code := "INNER_BAD", cls := "InvalidInput", text := [.lit "Inner: x is ", .arg "value" .json],
            args := [], inherited := false },
          .each "ys" ⟨.root, [.tok "ys", .star]⟩ [] [
            .check {
              id := "b2", loc := ⟨.item 0, []⟩, guard := [], kind := .hasType [.atom .string],
              code := "INNER_BAD", cls := "InvalidInput", text := [.lit "Inner: y ", .arg "index" .index],
              args := [], inherited := false }]]] },
      { name := "semantic", entries := [
        .check {
          id := "4.1", loc := ⟨.root, []⟩, guard := [], kind := .hook "no_bad_name",
          code := "DEMO_SEMANTIC", cls := "InvalidInput", text := [.lit "Semantic: ", .arg "names" .list],
          args := [], inherited := false },
        .check {
          id := "4.3", loc := ⟨.root, []⟩, guard := [],
          kind := .classifier "demo_rules" [
            { id := "4.3a", code := "DEMO_SEMANTIC", cls := "InvalidInput",
              text := [.lit "Semantic: first ", .arg "n" .count], inherited := false },
            { id := "4.3b", code := "DEMO_SEMANTIC", cls := "InvalidInput", text := [.lit "Semantic: second"],
              inherited := false }],
          code := "DEMO_SEMANTIC", cls := "InvalidInput", text := [], args := [], inherited := false }] }] }
end VE.WireContract.Tables.Corpus.Demo

namespace VE.WireContract.Tables.Corpus.Defer
def table : VE.WireContract.Table :=
  { contract := "defer@0", revision := 1, residual := ("DEFER_INVALID_INPUT", "InvalidInput"),
    phases := [
      { name := "first", entries := [
        .check {
          id := "d1", loc := ⟨.root, [.tok "v"]⟩, guard := [], kind := .hasType [.atom .integer],
          code := "DEFER_SHAPE", cls := "InvalidInput", text := [.lit "Defer: v"], args := [],
          inherited := false }] },
      { name := "second", entries := [
        .check {
          id := "d2", loc := ⟨.root, []⟩, guard := [], kind := .hook "lean_only",
          code := "DEFER_SHAPE", cls := "InvalidInput", text := [.lit "Defer: lean only"], args := [],
          inherited := false },
        .check {
          id := "d3", loc := ⟨.root, [.tok "w"]⟩, guard := [], kind := .hasType [.atom .integer],
          code := "DEFER_SHAPE", cls := "InvalidInput", text := [.lit "Defer: w"], args := [],
          inherited := false }] }] }
end VE.WireContract.Tables.Corpus.Defer
