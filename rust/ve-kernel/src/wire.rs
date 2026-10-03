use crate::{Error, MAX_INDEX, MAX_PACKAGE_BYTES, Result, error};
use serde::de::{Deserializer, Visitor};
use serde_json::{Map, Value};
use sha2::{Digest, Sha256};

/// Decode the restricted JSON subset, detecting duplicate keys before insertion.
/// Recursion, input bytes and integer lexemes are bounded before allocation.
pub fn loads_json(bytes: &[u8]) -> Result<Value> {
    if bytes.len() > MAX_PACKAGE_BYTES {
        return error("ResourceLimit", "JSON exceeds 16 MiB");
    }
    std::str::from_utf8(bytes).map_err(|_| Error::new("SyntaxError", "invalid UTF-8 JSON"))?;
    let mut parser = Decoder { bytes, pos: 0 };
    let value = parser.value(0)?;
    parser.ws();
    if parser.pos != bytes.len() {
        return error("SyntaxError", "trailing JSON input");
    }
    fn reject_null(value: &Value) -> Result<()> {
        match value {
            Value::Null => error("InvalidInput", "null is not in v0"),
            Value::Array(a) => a.iter().try_for_each(reject_null),
            Value::Object(o) => o.values().try_for_each(reject_null),
            _ => Ok(()),
        }
    }
    reject_null(&value)?;
    Ok(value)
}
// Deserialize escapes as bytes so JSON syntax and the v0 Unicode restriction
// are separate checks. serde_json documents this path as preserving lone
// surrogates in WTF-8; from_utf8 then rejects them as InvalidInput.
struct StringBytes;
impl<'de> Visitor<'de> for StringBytes {
    type Value = Vec<u8>;
    fn expecting(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("a JSON string")
    }
    fn visit_bytes<E: serde::de::Error>(self, bytes: &[u8]) -> std::result::Result<Vec<u8>, E> {
        Ok(bytes.to_vec())
    }
}
struct Decoder<'a> {
    bytes: &'a [u8],
    pos: usize,
}
impl Decoder<'_> {
    fn ws(&mut self) {
        while self.pos < self.bytes.len()
            && matches!(self.bytes[self.pos], b' ' | b'\t' | b'\n' | b'\r')
        {
            self.pos += 1;
        }
    }
    fn take(&mut self, byte: u8) -> bool {
        if self.bytes.get(self.pos) == Some(&byte) {
            self.pos += 1;
            true
        } else {
            false
        }
    }
    fn expect(&mut self, byte: u8) -> Result<()> {
        if self.take(byte) {
            Ok(())
        } else {
            error(
                "SyntaxError",
                format!("expected JSON delimiter at byte {}", self.pos),
            )
        }
    }
    fn string(&mut self) -> Result<String> {
        let start = self.pos;
        self.expect(b'"')?;
        while let Some(&byte) = self.bytes.get(self.pos) {
            self.pos += 1;
            if byte == b'\\' {
                if self.pos >= self.bytes.len() {
                    break;
                }
                self.pos += 1;
            } else if byte == b'"' {
                let bytes = serde_json::Deserializer::from_slice(&self.bytes[start..self.pos])
                    .deserialize_bytes(StringBytes)
                    .map_err(|e| Error::new("SyntaxError", e.to_string()))?;
                return String::from_utf8(bytes)
                    .map_err(|_| Error::new("InvalidInput", "lone UTF-16 surrogate"));
            } else if byte < 0x20 {
                return error("SyntaxError", "unescaped control character in JSON string");
            }
        }
        error("SyntaxError", "unterminated JSON string")
    }
    fn value(&mut self, depth: usize) -> Result<Value> {
        if depth > 256 {
            return error("ResourceLimit", "JSON nesting exceeds 256 levels");
        }
        self.ws();
        match self.bytes.get(self.pos).copied() {
            Some(b'"') => Ok(Value::String(self.string()?)),
            Some(b'[') => {
                self.pos += 1;
                self.ws();
                let mut values = Vec::new();
                if self.take(b']') {
                    return Ok(Value::Array(values));
                }
                loop {
                    values.push(self.value(depth + 1)?);
                    self.ws();
                    if self.take(b']') {
                        break;
                    }
                    self.expect(b',')?;
                }
                Ok(Value::Array(values))
            }
            Some(b'{') => {
                self.pos += 1;
                self.ws();
                let mut values = Map::new();
                if self.take(b'}') {
                    return Ok(Value::Object(values));
                }
                loop {
                    self.ws();
                    let key = self.string()?;
                    self.ws();
                    self.expect(b':')?;
                    let value = self.value(depth + 1)?;
                    if values.contains_key(&key) {
                        return error(
                            "DuplicateDeclaration",
                            format!("duplicate JSON key {key:?}"),
                        );
                    }
                    values.insert(key, value);
                    self.ws();
                    if self.take(b'}') {
                        break;
                    }
                    self.expect(b',')?;
                }
                Ok(Value::Object(values))
            }
            Some(b't') if self.bytes[self.pos..].starts_with(b"true") => {
                self.pos += 4;
                Ok(Value::Bool(true))
            }
            Some(b'f') if self.bytes[self.pos..].starts_with(b"false") => {
                self.pos += 5;
                Ok(Value::Bool(false))
            }
            Some(b'N') if self.bytes[self.pos..].starts_with(b"NaN") => {
                error("InvalidInput", "NaN is not in v0")
            }
            Some(b'I') if self.bytes[self.pos..].starts_with(b"Infinity") => {
                error("InvalidInput", "Infinity is not in v0")
            }
            Some(b'-') if self.bytes[self.pos..].starts_with(b"-Infinity") => {
                error("InvalidInput", "-Infinity is not in v0")
            }
            Some(b'-' | b'0'..=b'9') => {
                let start = self.pos;
                let negative = self.take(b'-');
                if !self.take(b'0') {
                    if !matches!(self.bytes.get(self.pos), Some(b'1'..=b'9')) {
                        return error("SyntaxError", "invalid number");
                    }
                    while matches!(self.bytes.get(self.pos), Some(b'0'..=b'9')) {
                        self.pos += 1;
                    }
                }
                // Match only complete fraction/exponent suffixes. Incomplete
                // suffixes remain trailing syntax (Python's JSON decoder order).
                let integer_end = self.pos;
                if self.bytes.get(self.pos) == Some(&b'.')
                    && matches!(self.bytes.get(self.pos + 1), Some(b'0'..=b'9'))
                {
                    self.pos += 2;
                    while matches!(self.bytes.get(self.pos), Some(b'0'..=b'9')) {
                        self.pos += 1;
                    }
                }
                if matches!(self.bytes.get(self.pos), Some(b'e' | b'E')) {
                    let mut end = self.pos + 1;
                    if matches!(self.bytes.get(end), Some(b'+' | b'-')) {
                        end += 1;
                    }
                    if matches!(self.bytes.get(end), Some(b'0'..=b'9')) {
                        self.pos = end + 1;
                        while matches!(self.bytes.get(self.pos), Some(b'0'..=b'9')) {
                            self.pos += 1;
                        }
                    }
                }
                if self.pos != integer_end {
                    return error("InvalidInput", "floating point numbers are not in v0");
                }
                if self.pos - start > 16 {
                    return error("ResourceLimit", "JSON integer exceeds supported bound");
                }
                let digits =
                    std::str::from_utf8(&self.bytes[start + usize::from(negative)..self.pos])
                        .unwrap();
                let n: u64 = digits
                    .parse()
                    .map_err(|_| Error::new("InvalidInput", "invalid integer"))?;
                if n > MAX_INDEX || (negative && n != 0) {
                    return error("InvalidInput", "JSON integer outside [0, 2^53-1]");
                }
                Ok(Value::from(n))
            }
            Some(b'n') if self.bytes[self.pos..].starts_with(b"null") => {
                self.pos += 4;
                Ok(Value::Null)
            }
            _ => error("SyntaxError", format!("invalid JSON at byte {}", self.pos)),
        }
    }
}

pub fn canonical_json(value: &Value) -> Result<Vec<u8>> {
    fn encode(v: &Value, out: &mut Vec<u8>, depth: usize) -> Result<()> {
        if depth > 256 {
            return error("ResourceLimit", "JSON nesting exceeds 256 levels");
        }
        match v {
            Value::Null => return error("InvalidInput", "null is not in v0"),
            Value::Number(n) => {
                if n.as_u64().is_none_or(|n| n > MAX_INDEX) {
                    return error("InvalidInput", "unsupported JSON number");
                }
                out.extend_from_slice(n.to_string().as_bytes());
            }
            Value::Bool(b) => out.extend_from_slice(if *b { b"true" } else { b"false" }),
            Value::String(s) => out.extend(serde_json::to_vec(s).expect("string serialization")),
            Value::Array(a) => {
                out.push(b'[');
                for (i, item) in a.iter().enumerate() {
                    if i > 0 {
                        out.push(b',');
                    }
                    encode(item, out, depth + 1)?;
                }
                out.push(b']');
            }
            Value::Object(o) => {
                let mut entries: Vec<_> = o.iter().collect();
                entries.sort_by(|a, b| a.0.encode_utf16().cmp(b.0.encode_utf16()));
                out.push(b'{');
                for (i, (key, value)) in entries.iter().enumerate() {
                    if i > 0 {
                        out.push(b',');
                    }
                    out.extend(serde_json::to_vec(key).expect("key serialization"));
                    out.push(b':');
                    encode(value, out, depth + 1)?;
                }
                out.push(b'}');
            }
        }
        if out.len() > MAX_PACKAGE_BYTES {
            return error("ResourceLimit", "canonical JSON exceeds 16 MiB");
        }
        Ok(())
    }
    let mut out = Vec::new();
    encode(value, &mut out, 0)?;
    Ok(out)
}
pub fn digest(domain: &str, value: &Value) -> Result<String> {
    let mut h = Sha256::new();
    h.update(domain.as_bytes());
    h.update(canonical_json(value)?);
    Ok(format!("{:x}", h.finalize()))
}
pub(crate) fn object<'a>(v: &'a Value, code: &str) -> Result<&'a Map<String, Value>> {
    v.as_object()
        .ok_or_else(|| Error::new(code, "expected an object"))
}
pub(crate) fn fields<'a>(
    v: &'a Value,
    keys: &[&str],
    code: &str,
) -> Result<&'a Map<String, Value>> {
    let obj = object(v, code)?;
    if obj.len() != keys.len() || keys.iter().any(|k| !obj.contains_key(*k)) {
        return error(code, format!("expected exactly fields {keys:?}"));
    }
    Ok(obj)
}

/// Wire array length of each formula tag, tag included (Python `ve.ast.WIRE_ARITY` without the
/// integer comparisons, which Rust does not decode). Surface records repeat it; a unit test there
/// keeps the two equal.
pub(crate) const FORMULA_ARITY: &[(&str, usize)] = &[
    ("top", 1),
    ("bottom", 1),
    ("unary", 3),
    ("binary", 4),
    ("atom", 3),
    ("eq", 3),
    ("not", 2),
    ("and", 3),
    ("or", 3),
    ("implies", 3),
    ("forall", 3),
    ("exists", 3),
    ("reach", 5),
];

pub(crate) fn formula_tag_arity(tag: &str) -> usize {
    FORMULA_ARITY
        .iter()
        .find(|(name, _)| *name == tag)
        .map_or(0, |(_, arity)| *arity)
}
