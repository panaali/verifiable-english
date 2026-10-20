/-! The words of an act phrase (docs/spec/act-phrases.md 4.1), below `VE.Norms.Wire` and `VE.Acts.Lexical`:
the reserved words, slot scanning, Python's whitespace and the word test, moved verbatim from `Norms/Wire.lean`
with their names, so that the act checks of both modules read one definition. -/
namespace VE.Norms.Wire

/-- Python `ve/environment.py` `RESERVED`, the words an act phrase may not use. -/
def actReserved : List String :=
  ["true", "false", "is", "equals", "not", "and", "or", "if", "then", "for", "every", "there",
   "exists", "believes", "must", "eventually", "no"]

/-- `{d}` slot occurrences in order, and the text with every slot replaced by
`slot` (Python `re.findall`/`re.sub` on `\{([0-9]+)\}`); fuel is the length. -/
def scanSlotsAux : Nat → List Char → List String × List Char
  | 0, cs => ([], cs)
  | _ + 1, [] => ([], [])
  | n + 1, '{' :: rest =>
    let digits := rest.takeWhile Char.isDigit
    match rest.drop digits.length with
    | '}' :: after =>
      if digits.isEmpty then
        let (ss, out) := scanSlotsAux n rest
        (ss, '{' :: out)
      else
        let (ss, out) := scanSlotsAux n after
        (String.mk digits :: ss, "slot".toList ++ out)
    | _ =>
      let (ss, out) := scanSlotsAux n rest
      (ss, '{' :: out)
  | n + 1, c :: rest =>
    let (ss, out) := scanSlotsAux n rest
    (ss, c :: out)

def scanSlots (cs : List Char) : List String × List Char := scanSlotsAux (cs.length + 1) cs

/-- Python `str.isspace`, the separator set of the no-argument `str.split()`
that Python `_regulated` normalises act phrases with (wider than
`Char.isWhitespace`: vertical tab, form feed, U+001C–U+001F, U+0085, no-break
and the Unicode space separators). -/
def pyWhitespace (c : Char) : Bool :=
  let n := c.toNat
  (0x09 ≤ n && n ≤ 0x0D) || (0x1C ≤ n && n ≤ 0x20) || n == 0x85 || n == 0xA0 ||
    n == 0x1680 || (0x2000 ≤ n && n ≤ 0x200A) || n == 0x2028 || n == 0x2029 ||
    n == 0x202F || n == 0x205F || n == 0x3000

def words (s : String) : List String := (s.split pyWhitespace).filter (· ≠ "")

def asciiLetter (c : Char) : Bool := ('a' ≤ c && c ≤ 'z') || ('A' ≤ c && c ≤ 'Z')

def actWord (w : String) : Bool :=
  match w.toList with
  | c :: cs => asciiLetter c && cs.all (fun d => asciiLetter d || d == '\'' || d == '-')
  | [] => false

end VE.Norms.Wire
