//! Wire contract tables (docs/spec/wire-contract-s4-2.md 3): one type per type of
//! `lean/VE/WireContract/Table.lean`, same constructors, same fields, same order. A generated
//! table (`contract_tables.rs`) is a static value of `Table` that the compiler type-checks. Data
//! only: no verdict reads it, and the engine that runs it is wc-s4-2b's.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Step {
    Tok(&'static str),
    Star,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Base {
    Root,
    /// The item of the n-th enclosing group; 0 is the innermost.
    Item(u32),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Pattern {
    pub base: Base,
    pub steps: &'static [Step],
}

/// A scalar literal of a contract (base spec 2.3); it has no `null`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Value {
    Bool(bool),
    Int(u64),
    Str(&'static str),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Atom {
    Null,
    Boolean,
    Integer,
    String,
    Array,
    Object,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TypeForm {
    Atom(Atom),
    ArrayOf(Atom),
    Tuple(&'static [Atom]),
}

/// A literal of a `when` guard.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Lit {
    Present(Pattern),
    Absent(Pattern),
    Equals(Pattern, Value),
    Differs(Pattern, Value),
    IsType(Pattern, &'static [TypeForm]),
    NotType(Pattern, &'static [TypeForm]),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct NameClass {
    /// Inclusive code point ranges.
    pub first: Option<&'static [(u32, u32)]>,
    pub rest: Option<&'static [(u32, u32)]>,
    pub min_bytes: Option<u64>,
    pub max_bytes: Option<u64>,
    pub forbid_prefix: &'static [&'static str],
    pub forbid_infix: &'static [&'static str],
    pub one_of: Option<&'static [&'static str]>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Renderer {
    Raw,
    Json,
    Index,
    Count,
    List,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Piece {
    Lit(&'static str),
    Arg(&'static str, Renderer),
}

/// One check of a classifier set (base spec 2.5).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Member {
    pub id: &'static str,
    pub code: &'static str,
    pub cls: &'static str,
    pub text: &'static [Piece],
    pub inherited: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    HasType(&'static [TypeForm]),
    ExactKeys(&'static [&'static str]),
    Keys(&'static [&'static str], &'static [&'static str]),
    Const(Value),
    OneOf(&'static [Value]),
    MaxItems(u64),
    MaxBytes(u64),
    MaxCount(Pattern, u64),
    Name(NameClass, bool),
    SortedUnique,
    UniqueSoFar,
    DeclaredIn(Pattern),
    RequiresMember(&'static str),
    RequiresItem(Value),
    ExcludesMember(&'static str),
    ExcludesItem(Value),
    Hook(&'static str),
    Classifier(&'static str, &'static [Member]),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Check {
    pub id: &'static str,
    /// `at`
    pub loc: Pattern,
    /// `when`
    pub guard: &'static [Lit],
    pub kind: Kind,
    pub code: &'static str,
    pub cls: &'static str,
    pub text: &'static [Piece],
    pub args: &'static [(&'static str, Pattern)],
    pub inherited: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Entry {
    Check(Check),
    Each(&'static str, Pattern, &'static [Lit], &'static [Entry]),
    /// A resolved `include`: its id, `at`, view, the `as` code with its class, and the inlined entries.
    Scope(&'static str, Pattern, Option<&'static str>, Option<(&'static str, &'static str)>, &'static [Entry]),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Phase {
    pub name: &'static str,
    pub entries: &'static [Entry],
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Table {
    pub contract: &'static str,
    pub revision: u64,
    /// The residual code and its class.
    pub residual: (&'static str, &'static str),
    pub phases: &'static [Phase],
}

/// A file a generated module was generated from, as its lock names it (wire-contract-s4-2.md 4).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Source {
    pub file: &'static str,
    pub revision: u64,
    pub sha256: &'static str,
}
