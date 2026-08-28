"""A strict YAML subset, stdlib-only — enough for this repo's data files.

The repo's discipline is no third-party dependencies (the gazetteer is emitted
by hand with json.dumps for strings). This loader reads that same dialect back:

- block maps, nested by 2-space indentation
- block lists of scalars (``- item``)
- inline lists ``[a, b, c]`` and inline maps ``{k: v, k2: v2}``
- scalars: integers, ``true``/``false``/``null``, "double-quoted" strings
  (json escapes), and bare strings
- comments: full-line and trailing (`` # …`` outside quotes)

Anything outside the subset raises YamliteError with a line number, rather
than guessing — the point is predictable round-trips, not YAML compliance.
"""
import json
import re

class YamliteError(ValueError):
    pass


_INT = re.compile(r"-?\d+$")


def _strip_comment(text):
    """Remove a trailing comment, respecting double quotes."""
    out, in_q, i = [], False, 0
    while i < len(text):
        c = text[i]
        if c == '"' and (i == 0 or text[i - 1] != "\\"):
            in_q = not in_q
        elif c == "#" and not in_q and (i == 0 or text[i - 1] in " \t"):
            break
        out.append(c)
        i += 1
    return "".join(out).rstrip()


def _scalar(tok, ln):
    tok = tok.strip()
    if tok.startswith('"'):
        try:
            return json.loads(tok)
        except json.JSONDecodeError as e:
            raise YamliteError(f"line {ln}: bad quoted string {tok!r}") from e
    if tok.startswith("["):
        return _inline_list(tok, ln)
    if tok.startswith("{"):
        return _inline_map(tok, ln)
    if _INT.match(tok):
        return int(tok)
    if tok in ("true", "false"):
        return tok == "true"
    if tok in ("null", "~", ""):
        return None
    return tok


def _split_inline(body, ln):
    """Split an inline collection body on commas outside quotes/brackets."""
    parts, depth, in_q, cur = [], 0, False, []
    for c in body:
        if c == '"' and (not cur or cur[-1] != "\\"):
            in_q = not in_q
        if not in_q:
            if c in "[{":
                depth += 1
            elif c in "]}":
                depth -= 1
            elif c == "," and depth == 0:
                parts.append("".join(cur))
                cur = []
                continue
        cur.append(c)
    if in_q or depth:
        raise YamliteError(f"line {ln}: unterminated inline collection")
    if "".join(cur).strip():
        parts.append("".join(cur))
    return parts


def _inline_list(tok, ln):
    if not tok.endswith("]"):
        raise YamliteError(f"line {ln}: unterminated list {tok!r}")
    return [_scalar(p, ln) for p in _split_inline(tok[1:-1], ln)]


def _inline_map(tok, ln):
    if not tok.endswith("}"):
        raise YamliteError(f"line {ln}: unterminated map {tok!r}")
    out = {}
    for part in _split_inline(tok[1:-1], ln):
        if ":" not in part:
            raise YamliteError(f"line {ln}: bad inline map entry {part!r}")
        k, v = part.split(":", 1)
        out[_scalar(k, ln)] = _scalar(v, ln)
    return out


def _key(tok, ln):
    k = _scalar(tok, ln)
    if isinstance(k, bool) or k is None:
        return tok.strip()
    return k


def loads(text):
    lines = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = _strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if line.lstrip(" ").startswith("\t"):
            raise YamliteError(f"line {n}: tabs are not part of the subset")
        lines.append((n, indent, line.strip()))
    value, nxt = _block(lines, 0, 0)
    if nxt != len(lines):
        n = lines[nxt][0]
        raise YamliteError(f"line {n}: unexpected content after top-level block")
    return value


def _block(lines, i, indent):
    """Parse the block starting at lines[i], all at exactly `indent`."""
    if i >= len(lines):
        return {}, i
    n, ind, body = lines[i]
    if ind != indent:
        raise YamliteError(f"line {n}: expected indent {indent}, got {ind}")
    if body.startswith("- "):
        return _block_list(lines, i, indent)
    return _block_map(lines, i, indent)


def _block_list(lines, i, indent):
    out = []
    while i < len(lines):
        n, ind, body = lines[i]
        if ind != indent:
            break
        if not body.startswith("- "):
            raise YamliteError(f"line {n}: mixed list and map at one level")
        out.append(_scalar(body[2:], n))
        i += 1
    return out, i


def _block_map(lines, i, indent):
    out = {}
    while i < len(lines):
        n, ind, body = lines[i]
        if ind < indent:
            break
        if ind != indent:
            raise YamliteError(f"line {n}: bad indent {ind} (block is {indent})")
        if body.startswith("- "):
            raise YamliteError(f"line {n}: mixed map and list at one level")
        if ":" not in body:
            raise YamliteError(f"line {n}: expected 'key: value', got {body!r}")
        k, _, v = body.partition(":")
        key = _key(k, n)
        if key in out:
            raise YamliteError(f"line {n}: duplicate key {key!r}")
        v = v.strip()
        if v:
            out[key] = _scalar(v, n)
            i += 1
        else:
            i += 1
            if i < len(lines) and lines[i][1] > indent:
                out[key], i = _block(lines, i, lines[i][1])
            else:
                out[key] = None
    return out, i


def load(path):
    return loads(path.read_text(encoding="utf-8"))
