use crate::{
    Document, Environment, Error, Formula, MAX_DEPTH, MAX_NODES, MAX_SOURCE_BYTES, Result, Span,
    Term, environment::RESERVED, error,
};

#[derive(Clone, Debug)]
pub struct SourceNode {
    pub span: Span,
    pub source_name: Option<String>,
}
#[derive(Clone, Debug)]
pub struct ParseResult {
    pub document: Document,
    pub source: String,
    pub nodes: Vec<SourceNode>,
}
struct Parser<'a> {
    env: &'a Environment,
    s: &'a str,
    pos: usize,
    binders: Vec<String>,
    nodes: Vec<SourceNode>,
}
impl Parser<'_> {
    fn span(&self, start: usize) -> Span {
        let prefix = &self.s[..start];
        Span {
            start,
            end: self.pos.max(start + 1).min(self.s.len()),
            line: prefix.bytes().filter(|b| *b == b'\n').count() + 1,
            column: start - prefix.rfind('\n').map_or(0, |p| p + 1) + 1,
        }
    }
    fn err(&self, code: &str, msg: impl Into<String>, start: usize) -> Error {
        Error {
            code: code.into(),
            message: msg.into(),
            span: Some(self.span(start)),
        }
    }
    fn at(&self, s: &str) -> bool {
        self.s[self.pos..].starts_with(s)
    }
    fn eat(&mut self, s: &str) -> bool {
        if self.at(s) {
            self.pos += s.len();
            true
        } else {
            false
        }
    }
    fn literal(&mut self, s: &str) -> Result<()> {
        if self.eat(s) {
            Ok(())
        } else {
            Err(self.err("SyntaxError", format!("expected {s:?}"), self.pos))
        }
    }
    fn ident(&mut self) -> Result<(String, usize)> {
        let start = self.pos;
        if !self
            .s
            .as_bytes()
            .get(start)
            .is_some_and(u8::is_ascii_lowercase)
        {
            return Err(self.err("SyntaxError", "expected identifier", start));
        }
        self.pos += 1;
        while self
            .s
            .as_bytes()
            .get(self.pos)
            .is_some_and(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || *b == b'_')
        {
            self.pos += 1;
        }
        if self.pos - start > 64 {
            return Err(self.err("ResourceLimit", "identifier exceeds 64 bytes", start));
        }
        Ok((self.s[start..self.pos].to_owned(), start))
    }
    fn term(&mut self) -> Result<Term> {
        if self.eat("@") {
            let (name, p) = self.ident()?;
            if !self.env.constants.contains_key(&name) {
                return Err(self.err("UnknownSymbol", format!("unknown constant {name:?}"), p));
            }
            return Ok(Term::Const(name));
        }
        let (name, p) = self.ident()?;
        if RESERVED.contains(&name.as_str()) {
            return Err(self.err("SyntaxError", "reserved word cannot be a term", p));
        }
        self.binders
            .iter()
            .rev()
            .position(|b| b == &name)
            .map(|i| Term::Var(i as u64))
            .ok_or_else(|| self.err("UnboundVariable", format!("unbound variable {name:?}"), p))
    }
    fn node(&mut self, start: usize, f: Formula, name: Option<String>) -> Result<Formula> {
        if self.nodes.len() >= MAX_NODES {
            return Err(self.err("ResourceLimit", "AST node limit", start));
        }
        self.nodes.push(SourceNode {
            span: self.span(start),
            source_name: name,
        });
        Ok(f)
    }
    fn keyword(&self, s: &str) -> bool {
        self.at(s)
            && !self
                .s
                .as_bytes()
                .get(self.pos + s.len())
                .is_some_and(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || *b == b'_')
    }
    fn formula(&mut self, depth: usize) -> Result<Formula> {
        let start = self.pos;
        if depth > MAX_DEPTH {
            return Err(self.err("ResourceLimit", "formula depth limit", start));
        }
        let f;
        if self.keyword("true") {
            self.pos += 4;
            f = Formula::Top;
        } else if self.keyword("false") {
            self.pos += 5;
            f = Formula::Bottom;
        } else if self.eat("not (") {
            let body = self.formula(depth + 1)?;
            self.literal(")")?;
            f = Formula::Not(Box::new(body));
        } else if self.eat("if (") {
            let left = Box::new(self.formula(depth + 1)?);
            self.literal("), then (")?;
            let right = Box::new(self.formula(depth + 1)?);
            self.literal(")")?;
            f = Formula::Implies(left, right);
        } else if self.at("for every ") || self.at("there exists ") {
            let universal = self.eat("for every ");
            if !universal {
                self.literal("there exists ")?;
            }
            let (sort, p) = self.ident()?;
            if !self.env.sorts.contains(&sort) {
                return Err(self.err("UnknownSymbol", "unknown binder sort", p));
            }
            self.literal(" ")?;
            let (name, p) = self.ident()?;
            if RESERVED.contains(&name.as_str()) || self.env.schema_name(&name) {
                return Err(self.err("SyntaxError", "invalid binder name", p));
            }
            if self.binders.contains(&name) {
                return Err(self.err("ShadowedVariable", "binder shadows active binder", p));
            }
            self.literal(", (")?;
            self.binders.push(name.clone());
            let body = Box::new(self.formula(depth + 1)?);
            self.binders.pop();
            self.literal(")")?;
            return self.node(
                start,
                if universal {
                    Formula::Forall(sort, body)
                } else {
                    Formula::Exists(sort, body)
                },
                Some(name),
            );
        } else if self.eat("(") {
            let left = Box::new(self.formula(depth + 1)?);
            let and = self.eat(") and (");
            if !and && !self.eat(") or (") {
                return Err(self.err("SyntaxError", "expected ') and (' or ') or ('", self.pos));
            }
            let right = Box::new(self.formula(depth + 1)?);
            self.literal(")")?;
            f = if and {
                Formula::And(left, right)
            } else {
                Formula::Or(left, right)
            };
        } else {
            let left = self.term()?;
            if self.eat(" is ") {
                let (p, pos) = self.ident()?;
                if self.env.predicates.get(&p).is_none_or(|d| d.len() != 1) {
                    return Err(self.err("UnknownSymbol", "unknown unary predicate", pos));
                }
                f = Formula::Unary(p, left);
            } else if self.eat(" equals ") {
                f = Formula::Eq(left, self.term()?);
            } else {
                self.literal(" ")?;
                let (p, pos) = self.ident()?;
                if self.env.predicates.get(&p).is_none_or(|d| d.len() != 2) {
                    return Err(self.err("UnknownSymbol", "unknown binary predicate", pos));
                }
                self.literal(" ")?;
                f = Formula::Binary(p, left, self.term()?);
            }
        }
        self.node(start, f, None)
    }
}
pub fn parse_with_metadata(env: &Environment, source: &[u8]) -> Result<ParseResult> {
    if source.len() > MAX_SOURCE_BYTES {
        return error("ResourceLimit", "source exceeds 64 KiB");
    }
    if let Some(i) = source.iter().position(|b| !b.is_ascii()) {
        return Err(Error {
            code: "SyntaxError".into(),
            message: "semantic syntax must be ASCII".into(),
            span: Some(Span {
                start: i,
                end: i + 1,
                line: source[..i].iter().filter(|b| **b == b'\n').count() + 1,
                column: i - source[..i]
                    .iter()
                    .rposition(|b| *b == b'\n')
                    .map_or(0, |p| p + 1)
                    + 1,
            }),
        });
    }
    let s = std::str::from_utf8(source).expect("ASCII");
    let mut p = Parser {
        env,
        s,
        pos: 0,
        binders: Vec::new(),
        nodes: Vec::new(),
    };
    let mut formulas = Vec::new();
    if s.is_empty() {
        return Err(p.err(
            "SyntaxError",
            "document must contain at least one statement",
            0,
        ));
    }
    while p.pos < s.len() {
        formulas.push(p.formula(1)?);
        p.literal(".\n")?;
    }
    let document = Document::check(env, formulas).map_err(|mut e| {
        e.span = Some(Span {
            start: 0,
            end: s.len(),
            line: 1,
            column: 1,
        });
        e
    })?;
    Ok(ParseResult {
        document,
        source: s.into(),
        nodes: p.nodes,
    })
}
pub fn parse(env: &Environment, source: &[u8]) -> Result<Document> {
    Ok(parse_with_metadata(env, source)?.document)
}

pub fn print_document(doc: &Document) -> Result<String> {
    fn term(t: &Term, names: &[String]) -> String {
        match t {
            Term::Var(i) => names[names.len() - 1 - *i as usize].clone(),
            Term::Const(c) => format!("@{c}"),
        }
    }
    fn formula(f: &Formula, names: &mut Vec<String>, counter: &mut usize) -> String {
        match f {
            Formula::Top => "true".into(),
            Formula::Bottom => "false".into(),
            Formula::Unary(p, t) => format!("{} is {p}", term(t, names)),
            Formula::Binary(p, t, u) => format!("{} {p} {}", term(t, names), term(u, names)),
            Formula::Eq(t, u) => format!("{} equals {}", term(t, names), term(u, names)),
            Formula::Not(a) => format!("not ({})", formula(a, names, counter)),
            Formula::And(a, b) => format!(
                "({}) and ({})",
                formula(a, names, counter),
                formula(b, names, counter)
            ),
            Formula::Or(a, b) => format!(
                "({}) or ({})",
                formula(a, names, counter),
                formula(b, names, counter)
            ),
            Formula::Implies(a, b) => format!(
                "if ({}), then ({})",
                formula(a, names, counter),
                formula(b, names, counter)
            ),
            Formula::Forall(s, a) | Formula::Exists(s, a) => {
                let name = format!("x{}", *counter);
                *counter += 1;
                names.push(name.clone());
                let body = formula(a, names, counter);
                names.pop();
                format!(
                    "{} {s} {name}, ({body})",
                    if matches!(f, Formula::Forall(..)) {
                        "for every"
                    } else {
                        "there exists"
                    }
                )
            }
        }
    }
    let mut text = String::new();
    for f in doc.formulas() {
        let line = format!("{}.\n", formula(f, &mut Vec::new(), &mut 0));
        if text.len() + line.len() > MAX_SOURCE_BYTES {
            return error("ResourceLimit", "canonical document exceeds 64 KiB");
        }
        text.push_str(&line);
    }
    Ok(text)
}
