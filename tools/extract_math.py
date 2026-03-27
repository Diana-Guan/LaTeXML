"""Extract math content from one LaTeX source into a minimal math-only .tex file."""

from __future__ import annotations

import argparse
import bisect
import re
from dataclasses import dataclass
from pathlib import Path


MATH_ENVS = {
    "equation",
    "equation*",
    "align",
    "align*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "array",
    "aligned",
}

CUSTOM_MACRO_ARGS = {
    "mainStep": {2: "mainStep:title"},
    "solutionStep": {2: "solutionStep:title", 3: "solutionStep:body"},
}


@dataclass
class Token:
    kind: str
    value: str
    start: int
    end: int


@dataclass
class Span:
    start: int
    end: int
    label: str


@dataclass
class MathNode:
    kind: str
    content: str
    start: int
    end: int
    line_start: int
    line_end: int
    context: str


def normalize_line_endings(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_comments(text: str) -> str:
    lines = []
    for line in text.split("\n"):
        out = []
        i = 0
        while i < len(line):
            if line[i] == "%" and (i == 0 or line[i - 1] != "\\"):
                break
            out.append(line[i])
            i += 1
        lines.append("".join(out))
    return "\n".join(lines)


def line_starts(text: str) -> list[int]:
    starts = [0]
    for idx, char in enumerate(text):
        if char == "\n":
            starts.append(idx + 1)
    return starts


def line_number(starts: list[int], pos: int) -> int:
    return bisect.bisect_right(starts, pos)


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\\":
            if text.startswith(r"\[", i):
                tokens.append(Token("display_open", r"\[", i, i + 2))
                i += 2
                continue
            if text.startswith(r"\]", i):
                tokens.append(Token("display_close", r"\]", i, i + 2))
                i += 2
                continue
            if text.startswith(r"\(", i):
                tokens.append(Token("inline_open", r"\(", i, i + 2))
                i += 2
                continue
            if text.startswith(r"\)", i):
                tokens.append(Token("inline_close", r"\)", i, i + 2))
                i += 2
                continue

            match = re.match(r"\\(begin|end)\{([^}]+)\}", text[i:])
            if match:
                kind = "begin_env" if match.group(1) == "begin" else "end_env"
                value = match.group(2)
                end = i + match.end()
                tokens.append(Token(kind, value, i, end))
                i = end
                continue

            match = re.match(r"\\[A-Za-z@]+|\\.", text[i:])
            if match:
                end = i + match.end()
                tokens.append(Token("command", match.group(0)[1:], i, end))
                i = end
                continue

        if text.startswith("$$", i):
            tokens.append(Token("double_dollar", "$$", i, i + 2))
            i += 2
            continue
        if ch == "$":
            tokens.append(Token("dollar", "$", i, i + 1))
            i += 1
            continue
        if ch == "{":
            tokens.append(Token("brace_open", "{", i, i + 1))
            i += 1
            continue
        if ch == "}":
            tokens.append(Token("brace_close", "}", i, i + 1))
            i += 1
            continue
        if ch.isspace():
            start = i
            while i < n and text[i].isspace():
                i += 1
            tokens.append(Token("space", text[start:i], start, i))
            continue

        start = i
        while i < n and not text[i].isspace() and text[i] not in "\\${}":
            i += 1
        tokens.append(Token("text", text[start:i], start, i))
    return tokens


def skip_space(text: str, pos: int) -> int:
    while pos < len(text) and text[pos].isspace():
        pos += 1
    return pos


def read_group(text: str, pos: int) -> tuple[str, int]:
    pos = skip_space(text, pos)
    if pos >= len(text) or text[pos] != "{":
        raise ValueError(f"Expected '{{' at position {pos}")

    depth = 0
    start = pos + 1
    i = pos
    while i < len(text):
        char = text[i]
        if char == "\\":
            i += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:i], i + 1
        i += 1
    raise ValueError("Unterminated group")


def find_macro_spans(text: str, tokens: list[Token]) -> list[Span]:
    spans: list[Span] = []
    for token in tokens:
        if token.kind != "command" or token.value not in CUSTOM_MACRO_ARGS:
            continue
        arg_map = CUSTOM_MACRO_ARGS[token.value]
        pos = token.end
        for arg_num in range(1, max(arg_map) + 1):
            try:
                pos = skip_space(text, pos)
                if pos < len(text) and text[pos] == "[":
                    end = text.find("]", pos + 1)
                    if end == -1:
                        break
                    pos = end + 1
                    pos = skip_space(text, pos)
                content, next_pos = read_group(text, pos)
            except ValueError:
                break
            if arg_num in arg_map:
                spans.append(Span(pos + 1, next_pos - 1, arg_map[arg_num]))
            pos = next_pos
    spans.sort(key=lambda span: (span.start, -(span.end - span.start)))
    return spans


def enclosing_context(spans: list[Span], start: int, end: int) -> str:
    label = "plain"
    best_size = None
    for span in spans:
        if span.start <= start and end <= span.end:
            size = span.end - span.start
            if best_size is None or size < best_size:
                label = span.label
                best_size = size
    return label


def find_matching_token(tokens: list[Token], start_idx: int, open_kind: str, close_kind: str) -> int | None:
    depth = 1
    i = start_idx + 1
    while i < len(tokens):
        token = tokens[i]
        if token.kind == open_kind:
            depth += 1
        elif token.kind == close_kind:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def find_matching_env(tokens: list[Token], start_idx: int, env_name: str) -> int | None:
    depth = 1
    i = start_idx + 1
    while i < len(tokens):
        token = tokens[i]
        if token.kind == "begin_env" and token.value == env_name:
            depth += 1
        elif token.kind == "end_env" and token.value == env_name:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def extract_math_nodes(text: str, tokens: list[Token], spans: list[Span]) -> list[MathNode]:
    starts = line_starts(text)
    nodes: list[MathNode] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        start = end = None
        kind = None

        if token.kind == "display_open":
            end_idx = find_matching_token(tokens, i, "display_open", "display_close")
            if end_idx is not None:
                start = token.end
                end = tokens[end_idx].start
                kind = "display"
                i = end_idx + 1
                nodes.append(
                    MathNode(
                        kind=kind,
                        content=text[start:end],
                        start=start,
                        end=end,
                        line_start=line_number(starts, start),
                        line_end=line_number(starts, end),
                        context=enclosing_context(spans, start, end),
                    )
                )
                continue

        elif token.kind == "inline_open":
            end_idx = find_matching_token(tokens, i, "inline_open", "inline_close")
            if end_idx is not None:
                start = token.end
                end = tokens[end_idx].start
                kind = "inline"
                i = end_idx + 1
                nodes.append(
                    MathNode(
                        kind=kind,
                        content=text[start:end],
                        start=start,
                        end=end,
                        line_start=line_number(starts, start),
                        line_end=line_number(starts, end),
                        context=enclosing_context(spans, start, end),
                    )
                )
                continue

        elif token.kind == "double_dollar":
            end_idx = find_matching_token(tokens, i, "double_dollar", "double_dollar")
            if end_idx is not None:
                start = token.end
                end = tokens[end_idx].start
                kind = "display"
                i = end_idx + 1
                nodes.append(
                    MathNode(
                        kind=kind,
                        content=text[start:end],
                        start=start,
                        end=end,
                        line_start=line_number(starts, start),
                        line_end=line_number(starts, end),
                        context=enclosing_context(spans, start, end),
                    )
                )
                continue

        elif token.kind == "dollar":
            end_idx = find_matching_token(tokens, i, "dollar", "dollar")
            if end_idx is not None:
                start = token.end
                end = tokens[end_idx].start
                kind = "inline"
                i = end_idx + 1
                nodes.append(
                    MathNode(
                        kind=kind,
                        content=text[start:end],
                        start=start,
                        end=end,
                        line_start=line_number(starts, start),
                        line_end=line_number(starts, end),
                        context=enclosing_context(spans, start, end),
                    )
                )
                continue

        elif token.kind == "begin_env" and token.value in MATH_ENVS:
            end_idx = find_matching_env(tokens, i, token.value)
            if end_idx is not None:
                start = token.start
                end = tokens[end_idx].end
                kind = f"environment:{token.value}"
                i = end_idx + 1
                nodes.append(
                    MathNode(
                        kind=kind,
                        content=text[start:end],
                        start=start,
                        end=end,
                        line_start=line_number(starts, start),
                        line_end=line_number(starts, end),
                        context=enclosing_context(spans, start, end),
                    )
                )
                continue

        i += 1
    return nodes


def strip_macro(text: str, macro: str, keep_arg: int | None) -> str:
    pattern = f"\\{macro}"
    out = []
    i = 0
    while i < len(text):
        if text.startswith(pattern, i):
            pos = i + len(pattern)
            args = []
            try:
                while True:
                    pos = skip_space(text, pos)
                    if pos < len(text) and text[pos] == "[":
                        end = text.find("]", pos + 1)
                        if end == -1:
                            raise ValueError("Unterminated optional argument")
                        pos = end + 1
                        continue
                    if pos < len(text) and text[pos] == "{":
                        arg, pos = read_group(text, pos)
                        args.append(arg)
                        if len(args) == 3:
                            break
                    else:
                        break
                if keep_arg is None:
                    replacement = ""
                elif keep_arg - 1 < len(args):
                    replacement = f" {args[keep_arg - 1]} "
                else:
                    raise ValueError("Missing required argument")
                out.append(replacement)
                i = pos
                continue
            except ValueError:
                pass
        out.append(text[i])
        i += 1
    return "".join(out)


def unwrap_tikz_nodes(text: str) -> str:
    pattern = re.compile(
        r"\\tikz(?:\[[^\]]*\])?\s*\\node(?:\[[^\]]*\])?(?:\([^)]*\))?\{(.*?)\};",
        re.DOTALL,
    )
    previous = None
    while previous != text:
        previous = text
        text = pattern.sub(lambda match: strip_nested_math_delims(match.group(1).strip()), text)
    return text


def strip_nested_math_delims(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("$") and stripped.endswith("$") and len(stripped) >= 2:
        return stripped[1:-1].strip()
    if stripped.startswith(r"\(") and stripped.endswith(r"\)"):
        return stripped[2:-2].strip()
    if stripped.startswith(r"\[") and stripped.endswith(r"\]"):
        return stripped[2:-2].strip()
    return stripped


def unwrap_inline_math(text: str) -> str:
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"\$(.+?)\$", lambda match: match.group(1).strip(), text, flags=re.DOTALL)
        text = re.sub(r"\\\((.+?)\\\)", lambda match: match.group(1).strip(), text, flags=re.DOTALL)
        text = re.sub(r"\\\[(.+?)\\\]", lambda match: match.group(1).strip(), text, flags=re.DOTALL)
    return text


def cleanup_math(text: str) -> str:
    cleaned = text
    cleaned = unwrap_tikz_nodes(cleaned)
    for macro, keep_arg in (
        ("colorbox", 2),
        ("textcolor", 2),
        ("text", 1),
        ("deflink", 2),
        ("qdeflink", 2),
        ("backtoterm", 2),
        ("hyperlink", 2),
        ("hyperref", 1),
        ("hypertarget", None),
        ("defanchor", None),
        ("questionanchor", None),
        ("marginnote", None),
        ("hspace*", None),
        ("hspace", None),
    ):
        cleaned = strip_macro(cleaned, macro, keep_arg)

    cleaned = unwrap_inline_math(cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned.strip()


def emit_tex(nodes: list[MathNode], source_path: Path, output_path: Path) -> None:
    lines = [
        r"\documentclass{article}",
        r"\usepackage{amsmath,amssymb}",
        "",
        r"\begin{document}",
        "",
        f"% Extracted from {source_path.name}",
        "",
    ]

    for index, node in enumerate(nodes, start=1):
        cleaned = cleanup_math(node.content)
        if not cleaned:
            continue
        lines.append(
            f"% item={index} kind={node.kind} context={node.context} "
            f"lines={node.line_start}-{node.line_end}"
        )
        if node.kind in {"environment:equation", "environment:equation*", "environment:align", "environment:align*", "environment:gather", "environment:gather*", "environment:multline", "environment:multline*"}:
            lines.append(cleaned)
        else:
            lines.append(r"\[")
            lines.append(cleaned)
            lines.append(r"\]")
        lines.append("")

    lines.extend([r"\end{document}", ""])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract math content from one LaTeX file into extracted_file/<name>_mathonly.tex"
    )
    parser.add_argument("input_file", help="Path to one .tex file")
    parser.add_argument(
        "--output-dir",
        default="extracted_file",
        help="Directory for generated files (default: extracted_file)",
    )
    args = parser.parse_args()

    input_path = Path(args.input_file).expanduser().resolve()
    if not input_path.is_file():
        raise SystemExit(f"Input file not found: {input_path}")

    raw_text = input_path.read_text(encoding="utf-8")
    preprocessed = strip_comments(normalize_line_endings(raw_text))
    tokens = tokenize(preprocessed)
    spans = find_macro_spans(preprocessed, tokens)
    nodes = extract_math_nodes(preprocessed, tokens, spans)

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = (Path.cwd() / output_dir).resolve()
    output_path = output_dir / f"{input_path.stem}_mathonly.tex"
    emit_tex(nodes, input_path, output_path)
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
