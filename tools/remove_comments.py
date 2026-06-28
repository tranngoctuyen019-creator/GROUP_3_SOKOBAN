#!/usr/bin/env python3
import sys
import tokenize
from pathlib import Path
from io import BytesIO


def strip_comments(src_bytes):
    out_tokens = []
    try:
        tokens = list(tokenize.tokenize(BytesIO(src_bytes).readline))
    except Exception:
        return src_bytes
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            continue
        out_tokens.append(tok)
    try:
        new = tokenize.untokenize(out_tokens)
    except Exception:
        return src_bytes
    if isinstance(new, bytes):
        return new
    return new.encode('utf-8')


def process_path(p: Path):
    if p.is_dir():
        for f in p.rglob('*.py'):
            process_path(f)
        return
    if not p.is_file():
        return
    b = p.read_bytes()
    newb = strip_comments(b)
    if newb != b:
        p.write_bytes(newb)
        print(f"Stripped comments: {p}")
    else:
        print(f"No changes: {p}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: remove_comments.py <paths...>")
        sys.exit(1)
    for a in sys.argv[1:]:
        process_path(Path(a))
